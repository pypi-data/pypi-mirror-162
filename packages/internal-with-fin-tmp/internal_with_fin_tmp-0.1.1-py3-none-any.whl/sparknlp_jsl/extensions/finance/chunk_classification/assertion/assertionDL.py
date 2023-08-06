from sparknlp.common import *
from sparknlp_jsl.annotator.assertion.assertionDL import AssertionDLApproach as A
from sparknlp_jsl.annotator.assertion.assertionDL import AssertionDLModel as M
class AssertionDLApproach(A):
    """Train a Assertion Model algorithm using deep learning.
    from extracted entities and text. AssertionLogRegModel requires DOCUMENT, CHUNK and WORD_EMBEDDINGS type
    annotator inputs, which can be obtained by e.g a

    The training data should have annotations columns of type ``DOCUMENT``, ``CHUNK``, ``WORD_EMBEDDINGS``, the ``label`` column
    (The assertion status that you want to predict), the ``start`` (the start index for the term that has the assertion status),
    the ``end`` column (the end index for the term that has the assertion status).This model use a deep learning to predict the entity.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    label
        Column with one label per document. Example of possible values: “present”, “absent”, “hypothetical”, “conditional”, “associated_with_other_person”, etc.
    startCol
        Column that contains the token number for the start of the target
    endCol
        olumn that contains the token number for the end of the target
    batchSize
        Size for each batch in the optimization process
    epochs
        Number of epochs for the optimization process
    learningRate
        Learning rate for the optimization process
    dropout
        dropout", "Dropout at the output of each layer
    maxSentLen
        Max length for an input sentence.
    graphFolder
        Folder path that contain external graph files
    graphFile
        Graph file name to use
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()
    validationSplit
        Choose the proportion of training dataset to be validated against the model on each Epoch. The value should be between 0.0 and 1.0 and by default it is 0.0 and off.
    evaluationLogExtended
       Select if you want to have mode eval.
    testDataset
        Path to test dataset. If set used to calculate statistic on it during training.
    includeConfidence
        whether to include confidence scores in annotation metadata
    enableOutputLogs
        whether or not to output logs
    outputLogsPath
        Folder path to save training logs
    verbose
        Level of verbosity during training
    scopeWindow
        The scope window of the assertion expression
    Examples
    --------
    >>> import sparknlp
    >>> from sparknlp.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp.training import *
    >>> from pyspark.ml import Pipeline
    >>> document_assembler = DocumentAssembler() \\
    ...    .setInputCol("text") \\
    ...    .setOutputCol("document")
    >>> sentence_detector = SentenceDetector() \\
    ...    .setInputCol("document") \\
    ...    .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...    .setInputCols(["sentence"]) \\
    ...    .setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...    .setInputCols(["sentence", "token"]) \\
    ...    .setOutputCol("word_embeddings") \\
    ...    .setCaseSensitive(False)
    >>> chunk = Chunker() \\
    ...    .setInputCols([sentence]) \\
    ...    .setChunkCol("chunk") \\
    ...    .setOutputCol("chunk")
    >>> assertion = AssertionDLApproach() \\
    ...    .setLabelCol("label") \\
    ...    .setInputCols(["document", "chunk", "word_embeddings"]) \\
    ...    .setOutputCol("assertion") \\
    ...    .setOutputCol("assertion") \\
    ...    .setBatchSize(128) \\
    ...    .setDropout(0.012) \\
    ...    .setLearningRate(0.015) \\
    ...    .setEpochs(1) \\
    ...    .setStartCol("start") \\
    ...    .setScopeWindow([3, 4]) \\
    ...    .setEndCol("end") \\
    ...    .setMaxSentLen(250)
    >>> assertionPipeline = Pipeline(stages=[
    ...    document_assembler,
    ...    sentence_detector,
    ...    tokenizer,
    ...    embeddings,
    ...    chunk,
    ...    assertion])
    >>> assertionModel = assertionPipeline.fit(dataset)
    """

    def _create_model(self, java_model):
        return AssertionDLModel(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(AssertionDLApproach, self).__init__(
            classname="com.johnsnowlabs.extensions.finance.chunk_classification.assertion.AssertionDLApproach")
        self._setDefault(label="label", batchSize=64, epochs=5, learningRate=0.0012, dropout=0.05, maxSentLen=250,
                         includeConfidence=False, scopeWindow=[-1, -1])


class AssertionDLModel(M):
    """AssertionDL is a deep Learning based approach used to extract Assertion Status
    from extracted entities and text. AssertionDLModel requires DOCUMENT, CHUNK and WORD_EMBEDDINGS type
    annotator inputs, which can be obtained by e.g a


    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    maxSentLen
        Max length for an input sentence.
    targetNerLabels
        List of NER labels to mark as target for assertion, must match NER output.
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    classes
        Tags used to trained this AssertionDLModel
    scopeWindow
        The scope window of the assertion expression
    Examples
    --------

    >>> import sparknlp
    >>> from sparknlp.base import *
    >>> from sparknlp.common import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp.training import *
    >>> import sparknlp_jsl
    >>> from sparknlp_jsl.base import *
    >>> from sparknlp_jsl.annotator import *
    >>> from pyspark.ml import Pipeline
    >>> data = spark.createDataFrame([["Patient with severe fever and sore throat"],["Patient shows no stomach pain"],["She was maintained on an epidural and PCA for pain control."]]).toDF("text")
    >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...  .setOutputCol("embeddings")
    >>> nerModel = MedicalNerModel.pretrained("ner_clinical", "en", "clinical/models") \\
    ...  .setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    >>> nerConverter = NerConverter().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")
    >>> clinicalAssertion = AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models") \\
    ...  .setInputCols(["sentence", "ner_chunk", "embeddings"]) \\
    ...  .setOutputCol("assertion")
    >>> assertionPipeline = Pipeline(stages=[
    ...  documentAssembler,
    ...  sentenceDetector,
    ...  tokenizer,
    ...  embeddings,
    ...  nerModel,
    ...  nerConverter,
    ...  clinicalAssertion
    ... ])

    >>> assertionModel = assertionPipeline.fit(data)


    >>> result = assertionModel.transform(data)
    >>> result.selectExpr("ner_chunk.result as ner", "assertion.result").show(3, truncate=False)
    +--------------------------------+--------------------------------+
    |ner                             |result                          |
    +--------------------------------+--------------------------------+
    |[severe fever, sore throat]     |[present, present]              |
    |[stomach pain]                  |[absent]                        |
    |[an epidural, PCA, pain control]|[present, present, hypothetical]|
    +--------------------------------+--------------------------------+



    """
    name = "AssertionDLModel"


    def __init__(self, classname="com.johnsnowlabs.extensions.finance.chunk_classification.assertion.AssertionDLModel", java_model=None):
        super(AssertionDLModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(AssertionDLModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

