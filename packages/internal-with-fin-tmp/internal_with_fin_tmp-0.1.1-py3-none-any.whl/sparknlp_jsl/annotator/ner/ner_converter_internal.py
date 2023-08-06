from sparknlp.common import *

class NerConverterInternal(AnnotatorApproach):
    """
    Converts a IOB or IOB2 representation of NER to a user-friendly one,
    by associating the tokens of recognized entities and their label.
    Chunks with no associated entity (tagged "O") are filtered.

    ==========================================  ======================
    Input Annotation types                      Output Annotation type
    ==========================================  ======================
    ``DOCUMENT, TOKEN, NAMED_ENTITY``           ``CHUNK``
    ==========================================  ======================

    Parameters
    ----------
    whiteList
        If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels
    blackList
        If defined, list of entities to ignore. The rest will be proccessed. Do not include IOB prefix on labels
    preservePosition
        Whether to preserve the original position of the tokens in the original document or use the modified tokens
    greedyMode
        Whether to ignore B tags for contiguous tokens of same entity same
    threshold
        Confidence threshold to filter the chunk entities.

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
    >>> data = spark.createDataFrame([["A 63-year-old man presents to the hospital ..."]]).toDF("text")
    >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models").setOutputCol("embs")
    >>> nerModel = MedicalNerModel.pretrained("ner_jsl", "en", "clinical/models").setInputCols(["sentence", "token", "embs"]).setOutputCol("ner")
    >>> nerConverter = NerConverterInternal().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")
    ...
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     sentenceDetector,
    ...     tokenizer,
    ...     embeddings,
    ...     nerModel,
    ...     nerConverter])
    """
    name = 'NerConverterInternal'

    whiteList = Param(
        Params._dummy(),
        "whiteList",
        "If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels",
        typeConverter=TypeConverters.toListString
    )

    preservePosition = Param(
        Params._dummy(),
        "preservePosition",
        "Whether to preserve the original position of the tokens in the original document or use the modified tokens",
        typeConverter=TypeConverters.toBoolean
    )

    greedyMode = Param(
        Params._dummy(),
        "greedyMode",
        "Whether to ignore B tags for contiguous tokens of same entity same",
        typeConverter=TypeConverters.toBoolean
    )

    threshold = Param(
        Params._dummy(),
        "threshold",
        "Confidence threshold",
        typeConverter=TypeConverters.toFloat
    )

    replaceDictResource = Param(Params._dummy(),
                                "replaceDictResource",
                                "replace dictionary pairs",
                                typeConverter=TypeConverters.identity)
    blackList = Param(Params._dummy(), "blackList",
                      "If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels",
                      TypeConverters.toListString)

    replaceLabels = Param(Params._dummy(), "replaceLabels",
                          "Custom replace labels",
                          TypeConverters.identity)

    def setWhiteList(self, entities):
        """If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels

        Parameters
        ----------
        entities : list
            If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels
        """
        return self._set(whiteList=entities)

    def setBlackList(self, entities):
        """If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels

        Parameters
        ----------
        entities : list
           If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels
        """
        return self._set(blackList=entities)

    def setPreservePosition(self, p):
        """Sets whether to preserve the original position of the tokens in the original document or use the modified tokens

        Parameters
        ----------
        p : bool
            Whether to preserve the original position of the tokens in the original document or use the modified tokens
        """
        return self._set(preservePosition=p)

    def setGreedyMode(self, p):
        """Sets  whether to ignore B tags for contiguous tokens of same entity same

        Parameters
        ----------
        p : bool
             Whether to ignore B tags for contiguous tokens of same entity same
        """
        return self._set(greedyMode=p)

    def setThreshold(self, p):
        """Sets confidence threshold to filter the chunk entities.

        Parameters
        ----------
        p : float
            Confidence threshold to filter the chunk entities.
        """
        return self._set(threshold=p)

    def setReplaceDictResource(self, path, read_as=ReadAs.TEXT, options=None):
        """Sets replace dictionary pairs

        Parameters
        ----------
        path : str
            Path to the external resource
        read_as : str, optional
            How to read the resource, by default ReadAs.TEXT
        options : dict, optional
            Options for reading the resource, by default {"format": "text"}

        """
        if options is None:
            options = {"delimiter": ","}
        return self._set(replaceDictResource=ExternalResource(path, read_as, options))


    def setReplaceLabels(self, labels):
        """Sets custom relation labels

        Parameters
        ----------
        labels : dict[str, str]
            Dictionary which maps old to new labels
        """
        labels = labels.copy()
        from sparknlp_jsl.internal import CustomLabels
        return self._set(replaceLabels=CustomLabels(labels))

    @keyword_only
    def __init__(self):
        super(NerConverterInternal, self).__init__(classname="com.johnsnowlabs.nlp.annotators.ner.NerConverterInternal")

    def _create_model(self, java_model):
        return NerConverterInternalModel(java_model=java_model)


class NerConverterInternalModel(AnnotatorModel):
    """
    Converts a IOB or IOB2 representation of NER to a user-friendly one,
    by associating the tokens of recognized entities and their label.
    Chunks with no associated entity (tagged "O") are filtered.

    ==========================================  ======================
    Input Annotation types                      Output Annotation type
    ==========================================  ======================
    ``DOCUMENT, TOKEN, NAMED_ENTITY``           ``CHUNK``
    ==========================================  ======================

    Parameters
    ----------
    whiteList
        If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels
    blackList
        If defined, list of entities to ignore. The rest will be proccessed. Do not include IOB prefix on labels
    preservePosition
        Whether to preserve the original position of the tokens in the original document or use the modified tokens
    greedyMode
        Whether to ignore B tags for contiguous tokens of same entity same
    threshold
        Confidence threshold to filter the chunk entities.

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
    >>> data = spark.createDataFrame([["A 63-year-old man presents to the hospital ..."]]).toDF("text")
    >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models").setOutputCol("embs")
    >>> nerModel = MedicalNerModel.pretrained("ner_jsl", "en", "clinical/models").setInputCols(["sentence", "token", "embs"]).setOutputCol("ner")
    >>> nerConverter = NerConverterInternal().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")
    ...
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     sentenceDetector,
    ...     tokenizer,
    ...     embeddings,
    ...     nerModel,
    ...     nerConverter])
    """
    name = 'NerConverterInternal'

    whiteList = Param(
        Params._dummy(),
        "whiteList",
        "If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels",
        typeConverter=TypeConverters.toListString
    )

    preservePosition = Param(
        Params._dummy(),
        "preservePosition",
        "Whether to preserve the original position of the tokens in the original document or use the modified tokens",
        typeConverter=TypeConverters.toBoolean
    )

    greedyMode = Param(
        Params._dummy(),
        "greedyMode",
        "Whether to ignore B tags for contiguous tokens of same entity same",
        typeConverter=TypeConverters.toBoolean
    )

    threshold = Param(
        Params._dummy(),
        "threshold",
        "Confidence threshold",
        typeConverter=TypeConverters.toFloat
    )

    replaceDict = Param(Params._dummy(), "replaceDict", "dictionary of entities to replace",
                        typeConverter=TypeConverters.identity)

    blackList = Param(Params._dummy(), "blackList",
                      "If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels",
                      TypeConverters.toListString)


    def setWhiteList(self, entities):
        """If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels

        Parameters
        ----------
        entities : list
            If defined, list of entities to process. The rest will be ignored. Do not include IOB prefix on labels
        """
        return self._set(whiteList=entities)

    def setBlackList(self, entities):
        """If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels

        Parameters
        ----------
        entities : list
           If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels
        """
        return self._set(blackList=entities)

    def setPreservePosition(self, p):
        """Sets whether to preserve the original position of the tokens in the original document or use the modified tokens

        Parameters
        ----------
        p : bool
            Whether to preserve the original position of the tokens in the original document or use the modified tokens
        """
        return self._set(preservePosition=p)

    def setGreedyMode(self, p):
        """Sets  whether to ignore B tags for contiguous tokens of same entity same

        Parameters
        ----------
        p : bool
             Whether to ignore B tags for contiguous tokens of same entity same
        """
        return self._set(greedyMode=p)

    def setThreshold(self, p):
        """Sets confidence threshold to filter the chunk entities.

        Parameters
        ----------
        p : float
            Confidence threshold to filter the chunk entities.
        """
        return self._set(threshold=p)


    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.merge.ChunkMergeModel",
                 java_model=None):
        super(ChunkMergeModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    def __init__(self,classname="com.johnsnowlabs.nlp.annotators.ner.NerConverterInternalModel",java_model=None):
        super(NerConverterInternalModel, self).__init__(
            classname=classname,
            java_model=java_model
        )


