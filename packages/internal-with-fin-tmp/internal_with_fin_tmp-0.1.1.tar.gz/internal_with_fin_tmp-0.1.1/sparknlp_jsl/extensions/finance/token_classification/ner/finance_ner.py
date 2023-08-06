import sys

from sparknlp.common import *
import sparknlp
from sparknlp.internal import ExtendedJavaWrapper
from sparknlp_jsl.annotator.ner.medical_ner import MedicalNerApproach as A
from sparknlp_jsl.annotator.ner.medical_ner import MedicalNerModel as M


class FinanceNerApproach(A):
    """This Named Entity recognition annotator allows to train generic NER model
    based on Neural Networks.

    The architecture of the neural network is a Char CNNs - BiLSTM - CRF that
    achieves state-of-the-art in most datasets.

    For instantiated/pretrained models, see :class:`.NerDLModel`.

    The training data should be a labeled Spark Dataset, in the format of
    :class:`.CoNLL` 2003 IOB with `Annotation` type columns. The data should
    have columns of type ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` and an additional
    label column of annotator type ``NAMED_ENTITY``.

    Excluding the label, this can be done with for example:

    - a SentenceDetector,
    - a Tokenizer and
    - a WordEmbeddingsModel (any embeddings can be chosen, e.g. BertEmbeddings
      for BERT based embeddings).

    For extended examples of usage, see the `Spark NLP Workshop <https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/training/english/dl-ner>`__.

    ==================================== ======================
    Input Annotation types               Output Annotation type
    ==================================== ======================
    ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` ``NAMED_ENTITY``
    ==================================== ======================

    Parameters
    ----------
    labelColumn
        Column with label per each token
    entities
        Entities to recognize
    minEpochs
        Minimum number of epochs to train, by default 0
    maxEpochs
        Maximum number of epochs to train, by default 50
    verbose
        Level of verbosity during training, by default 2
    randomSeed
        Random seed
    lr
        Learning Rate, by default 0.001
    po
        Learning rate decay coefficient. Real Learning Rage = lr / (1 + po *
        epoch), by default 0.005
    batchSize
        Batch size, by default 8
    dropout
        Dropout coefficient, by default 0.5
    graphFolder
        Folder path that contain external graph files
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    useContrib
        whether to use contrib LSTM Cells. Not compatible with Windows. Might
        slightly improve accuracy
    validationSplit
        Choose the proportion of training dataset to be validated against the
        model on each Epoch. The value should be between 0.0 and 1.0 and by
        default it is 0.0 and off, by default 0.0
    evaluationLogExtended
        Whether logs for validation to be extended, by default False.
    testDataset
        Path to test dataset. If set used to calculate statistic on it during
        training.
    includeConfidence
        whether to include confidence scores in annotation metadata, by default
        False
    includeAllConfidenceScores
        whether to include all confidence scores in annotation metadata or just
        the score of the predicted tag, by default False
    enableOutputLogs
        Whether to use stdout in addition to Spark logs, by default False
    outputLogsPath
        Folder path to save training logs
    enableMemoryOptimizer
        Whether to optimize for large datasets or not. Enabling this option can
        slow down training, by default False

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

    First extract the prerequisites for the NerDLApproach

    >>> documentAssembler = DocumentAssembler() \\
    ...     .setInputCol("text") \\
    ...     .setOutputCol("document")
    >>> sentence = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...     .setInputCols(["sentence"]) \\
    ...     .setOutputCol("token")
    >>> embeddings = BertEmbeddings.pretrained() \\
    ...     .setInputCols(["sentence", "token"]) \\
    ...     .setOutputCol("embeddings")

    Then the training can start

    >>> nerTagger = MedicalNerApproach() \\
    ...     .setInputCols(["sentence", "token", "embeddings"]) \\
    ...     .setLabelColumn("label") \\
    ...     .setOutputCol("ner") \\
    ...     .setMaxEpochs(1) \\
    ...     .setRandomSeed(0) \\
    ...     .setVerbose(0)
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     sentence,
    ...     tokenizer,
    ...     embeddings,
    ...     nerTagger
    ... ])
    >>> conll = CoNLL()
    >>> trainingData = conll.readDataset(spark, "src/test/resources/conll2003/eng.train")
    >>> pipelineModel = pipeline.fit(trainingData)
    """

    def _create_model(self, java_model):
        return FinanceNerApproach(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(FinanceNerApproach, self).__init__(classname="com.johnsnowlabs.extensions.finance.token_classification.ner.FinanceNerApproach")
        uc = False if sys.platform == 'win32' else True
        self._setDefault(
            minEpochs=0,
            maxEpochs=50,
            lr=float(0.001),
            po=float(0.005),
            batchSize=8,
            dropout=float(0.5),
            verbose=2,
            useContrib=uc,
            validationSplit=float(0.0),
            evaluationLogExtended=False,
            includeConfidence=False,
            includeAllConfidenceScores=False,
            enableOutputLogs=False,
            enableMemoryOptimizer=False,
            pretrainedModelPath="",
            overrideExistingTags=True,
            earlyStoppingCriterion=0.0,
            earlyStoppingPatience=0
        )


class _FinanceNerModelLoader(ExtendedJavaWrapper):
    def __init__(self, ner_model_path, path, jspark):
        super(_FinanceNerModelLoader, self).__init__(
            "com.johnsnowlabs.extensions.finance.token_classification.ner.FinanceNerModel.loadSavedModel", ner_model_path, path, jspark)


class FinanceNerModel(M):
    """This Named Entity recognition annotator is a generic NER model based on
    Neural Networks.

    Neural Network architecture is Char CNNs - BiLSTM - CRF that achieves
    state-of-the-art in most datasets.

    This is the instantiated model of the :class:`.NerDLApproach`. For training
    your own model, please see the documentation of that class.

    Pretrained models can be loaded with :meth:`.pretrained` of the companion
    object:

    >>> nerModel = MedicalNerDLModel.pretrained() \\
    ...     .setInputCols(["sentence", "token", "embeddings"]) \\
    ...     .setOutputCol("ner")


    The default model is ``"ner_dl"``, if no name is provided.

    For available pretrained models please see the `Models Hub
    <https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition>`__.
    Additionally, pretrained pipelines are available for this module, see
    `Pipelines <https://nlp.johnsnowlabs.com/docs/en/pipelines>`__.

    Note that some pretrained models require specific types of embeddings,
    depending on which they were trained on. For example, the default model
    ``"ner_dl"`` requires the WordEmbeddings ``"glove_100d"``.

    For extended examples of usage, see the `Spark NLP Workshop
    <https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Public/3.SparkNLP_Pretrained_Models.ipynb>`__.

    ==================================== ======================
    Input Annotation types               Output Annotation type
    ==================================== ======================
    ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` ``NAMED_ENTITY``
    ==================================== ======================

    Parameters
    ----------
    batchSize
        Size of every batch, by default 8
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    includeConfidence
        Whether to include confidence scores in annotation metadata, by default
        False
    includeAllConfidenceScores
        Whether to include all confidence scores in annotation metadata or just
        the score of the predicted tag, by default False
    inferenceBatchSize
        Number of sentences to process in a single batch during inference
    classes
        Tags used to trained this NerDLModel
    labelCasing:
        Setting all labels of the NER models upper/lower case. values upper|lower

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
    >>> documentAssembler = DocumentAssembler() \\
    ...     .setInputCol("text") \\
    ...     .setOutputCol("document")
    >>> sentence = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...     .setInputCols(["sentence"]) \\
    ...     .setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained() \\
    ...     .setInputCols(["sentence", "token"]) \\
    ...     .setOutputCol("bert")
    >>> nerTagger = MedicalNerDLModel.pretrained() \\
    ...     .setInputCols(["sentence", "token", "bert"]) \\
    ...     .setOutputCol("ner")
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     sentence,
    ...     tokenizer,
    ...     embeddings,
    ...     nerTagger
    ... ])
    >>> data = spark.createDataFrame([["U.N. official Ekeus heads for Baghdad."]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    """
    name = "FinanceNerModel"

    def __init__(self, classname="com.johnsnowlabs.extensions.finance.token_classification.ner.FinanceNerModel", java_model=None):
        super(FinanceNerModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            includeConfidence=False,
            includeAllConfidenceScores=False,
            batchSize=8,
            inferenceBatchSize=1
        )

    @staticmethod
    def pretrained(name="ner_dl", lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        return ResourceDownloader.downloadModel(FinanceNerModel, name, lang, remote_loc)

    @staticmethod
    def loadSavedModel(ner_model_path, folder, spark_session):
        jModel = _FinanceNerModelLoader(ner_model_path, folder, spark_session._jsparkSession)._java_obj
        return FinanceNerModel(java_model=jModel)

    @staticmethod
    def pretrained(name="ner_clinical", lang="en", remote_loc="clinical/models"):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(FinanceNerModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')
