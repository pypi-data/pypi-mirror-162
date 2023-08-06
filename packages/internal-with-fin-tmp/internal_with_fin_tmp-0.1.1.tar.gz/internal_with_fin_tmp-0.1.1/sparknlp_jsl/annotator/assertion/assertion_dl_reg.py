from sparknlp.common import *


class AssertionLogRegApproach(AnnotatorApproach):
    """Train a Assertion algorithm using a regression log model.

    Excluding the label, this can be done with for example:
    - a :class: SentenceDetector,
    - a :class: Chunk,
    - a :class: WordEmbeddingsModel.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    label
        Column with label per each token
    maxIter
        Max number of iterations for algorithm
    regParam
        Regularization parameter
    eNetParam
        Elastic net parameter
    beforeParam
        Length of the context before the target
    afterParam
        Length of the context after the target
    startCol
        Column that contains the token number for the start of the target"
    externalFeatures
        Additional dictionaries paths to use as a features
    endCol
        Column that contains the token number for the end of the target
    nerCol
        Column with NER type annotation output, use either nerCol or startCol and endCol
    targetNerLabels
        List of NER labels to mark as target for assertion, must match NER output


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
    ...
    >>> sentence_detector = SentenceDetector() \\
    ...    .setInputCol("document") \\
    ...    .setOutputCol("sentence")
    ...
    >>> tokenizer = Tokenizer() \\
    ...    .setInputCols(["sentence"]) \\
    ...    .setOutputCol("token")
    ...
    >>> glove = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...    .setInputCols(["sentence", "token"]) \\
    ...    .setOutputCol("word_embeddings") \
    ...
    >>> chunk = Chunker() \\
    ...    .setInputCols([sentence]) \\
    ...    .setChunkCol("chunk") \\
    ...    .setOutputCol("chunk")
    ...
    Then the AssertionLogRegApproach model is defined. Label column is needed in the dataset for training.
    >>> assertion = AssertionLogRegApproach() \\
    ...    .setLabelCol("label") \\
    ...    .setInputCols(["document", "chunk", "word_embeddings"]) \\
    ...    .setOutputCol("assertion") \\
    ...    .setReg(0.01) \\
    ...    .setBefore(11) \\
    ...    .setAfter(13) \\
    ...    .setStartCol("start") \\
    ...    .setEndCol("end")
    ...
    >>> assertionPipeline = Pipeline(stages=[
    ...    document_assembler,
    ...    sentence_detector,
    ...    tokenizer,
    ...    glove,
    ...    chunk,
    ...    assertion
    ...])

    >>> assertionModel = assertionPipeline.fit(dataset)
    """

    label = Param(Params._dummy(), "label", "Column with one label per document", typeConverter=TypeConverters.toString)
    maxIter = Param(Params._dummy(), "maxIter", "Max number of iterations for algorithm", TypeConverters.toInt)
    regParam = Param(Params._dummy(), "regParam", "Regularization parameter", TypeConverters.toFloat)
    eNetParam = Param(Params._dummy(), "eNetParam", "Elastic net parameter", TypeConverters.toFloat)
    beforeParam = Param(Params._dummy(), "beforeParam", "Length of the context before the target", TypeConverters.toInt)
    afterParam = Param(Params._dummy(), "afterParam", "Length of the context after the target", TypeConverters.toInt)
    startCol = Param(Params._dummy(), "startCol", "Column that contains the token number for the start of the target",
                     typeConverter=TypeConverters.toString)
    endCol = Param(Params._dummy(), "endCol", "Column that contains the token number for the end of the target",
                   typeConverter=TypeConverters.toString)
    nerCol = Param(Params._dummy(), "nerCol",
                   "Column with NER type annotation output, use either nerCol or startCol and endCol",
                   typeConverter=TypeConverters.toString)
    targetNerLabels = Param(Params._dummy(), "targetNerLabels",
                            "List of NER labels to mark as target for assertion, must match NER output",
                            typeConverter=TypeConverters.toListString)

    def setLabelCol(self, label):
        return self._set(label=label)

    def setMaxIter(self, maxiter):
        return self._set(maxIter=maxiter)

    def setReg(self, lamda):
        return self._set(regParam=lamda)

    def setEnet(self, enet):
        return self._set(eNetParam=enet)

    def setBefore(self, before):
        return self._set(beforeParam=before)

    def setAfter(self, after):
        return self._set(afterParam=after)

    def setStartCol(self, s):
        return self._set(startCol=s)

    def setEndCol(self, e):
        return self._set(endCol=e)

    def setNerCol(self, n):
        return self._set(nerCol=n)

    def setTargetNerLabels(self, v):
        return self._set(targetNerLabels=v)

    def _create_model(self, java_model):
        return AssertionLogRegModel(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(AssertionLogRegApproach, self).__init__(
            classname="com.johnsnowlabs.nlp.annotators.assertion.logreg.AssertionLogRegApproach")
        self._setDefault(label="label", beforeParam=11, afterParam=13)

class AssertionLogRegModel(AnnotatorModel, HasStorageRef):
    """This is a main class in AssertionLogReg family. Logarithmic Regression is used to extract Assertion Status
        from extracted entities and text. AssertionLogRegModel requires DOCUMENT, CHUNK and WORD_EMBEDDINGS type
        annotator inputs, which can be obtained by e.g a

    Excluding the label, this can be done with for example:

    - a :class:`.SentenceDetector`,
    - a :class:`Chunk`,
    - a :class:`.WordEmbeddingsModel`.


    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    beforeParam
        Length of the context before the target
    afterParam
        Length of the context after the target
    startCol
        Column that contains the token number for the start of the target"
    endCol
        Column that contains the token number for the end of the target
    nerCol
        Column with NER type annotation output, use either nerCol or startCol and endCol
    targetNerLabels


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
    ...
    >>> sentence_detector = SentenceDetector() \\
    ...    .setInputCol("document") \\
    ...    .setOutputCol("sentence")
    ...
    >>> tokenizer = Tokenizer() \\
    ...    .setInputCols(["sentence"]) \\
    ...    .setOutputCol("token")
    ...
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...    .setInputCols(["sentence", "token"]) \\
    ...    .setOutputCol("word_embeddings") \
    ...    .setCaseSensitive(False)
    ...
    >>> chunk = Chunker() \\
    ...    .setInputCols([sentence]) \\
    ...    .setChunkCol("chunk") \\
    ...    .setOutputCol("chunk")
    ...
    Then the AssertionLogRegApproach model is defined. Label column is needed in the dataset for training.
    >>> assertion = AssertionLogRegModel().pretrained() \\
    ...    .setLabelCol("label") \\
    ...    .setInputCols(["document", "chunk", "word_embeddings"]) \\
    ...    .setOutputCol("assertion") \\
    ...
    ...
    >>> assertionPipeline = Pipeline(stages=[
    ...    document_assembler,
    ...    sentence_detector,
    ...    tokenizer,
    ...    embeddings,
    ...    chunk,
    ...    assertion
    >>>])

    >>> assertionModel = assertionPipeline.fit(dataset)
    >>> assertionPretrained = assertionModel.transform(dataset)
"""
    name = "AssertionLogRegModel"

    beforeParam = Param(Params._dummy(), "beforeParam", "Length of the context before the target", TypeConverters.toInt)
    afterParam = Param(Params._dummy(), "afterParam", "Length of the context after the target", TypeConverters.toInt)
    startCol = Param(Params._dummy(), "startCol", "Column that contains the token number for the start of the target",
                     typeConverter=TypeConverters.toString)
    endCol = Param(Params._dummy(), "endCol", "Column that contains the token number for the end of the target",
                   typeConverter=TypeConverters.toString)
    nerCol = Param(Params._dummy(), "nerCol",
                   "Column with NER type annotation output, use either nerCol or startCol and endCol",
                   typeConverter=TypeConverters.toString)
    targetNerLabels = Param(Params._dummy(), "targetNerLabels",
                            "List of NER labels to mark as target for assertion, must match NER output",
                            typeConverter=TypeConverters.toListString)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.assertion.logreg.AssertionLogRegModel",
                 java_model=None):
        super(AssertionLogRegModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(AssertionLogRegModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')
