from sparknlp.common import *


class ChunkFiltererApproach(AnnotatorApproach):
    """ Model that Filters entities coming from CHUNK annotations. Filters can be set via a white list of terms or a regular expression.
        White list criteria is enabled by default. To use regex, `criteria` has to be set to `regex`.

    ==============================  ======================
    Input Annotation types          Output Annotation type
    ==============================  ======================
    ``DOCUMENT, CHUNK, ASSERTION``  ``CHUNK``
    ==============================  ======================

    Parameters
    ----------
    whiteList
        If defined, list of entities to process. The rest will be ignored
    regex
        If defined, list of entities to process. The rest will be ignored.
    criteria
           Tag representing what is the criteria to filter the chunks. possibles values (assertion|isIn|regex)
                isIn : Filter by the chunk
                regex : Filter using a regex
    entitiesConfidence
        Path to csv with  pairs (entity,confidenceThreshold). Filter the chunks with  entities which have confidence lower than the confidence threshold.

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
    >>> data = spark.createDataFrame([["Has a past history of gastroenteritis and stomach pain, however patient ..."]]).toDF("text")
    >>> docAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
    >>> posTagger = PerceptronModel.pretrained() \
    ...    .setInputCols(["sentence", "token"]) \
    ...    .setOutputCol("pos")
    >>> chunker = Chunker() \
    ...   .setInputCols(["pos", "sentence"]) \
    ...   .setOutputCol("chunk") \
    ...   .setRegexParsers(["(<NN>)+"])
    ...
    >>> chunkerFilter = ChunkFiltererApproach() \
    ...   .setInputCols(["sentence","chunk"]) \
    ...   .setOutputCol("filtered") \
    ...   .setCriteria("isin") \
    ...   .setWhiteList(["gastroenteritis"])
    ...
    >>> pipeline = Pipeline(stages=[
    ...   docAssembler,
    ...   sentenceDetector,
    ...   tokenizer,
    ...   posTagger,
    ...   chunker,
    ...   chunkerFilter])
    ...
    >>> result = pipeline.fit(data).transform(data)
    >>> result.selectExpr("explode(chunk)").show(truncate=False)

    >>> result.selectExpr("explode(chunk)").show(truncate=False)
    +---------------------------------------------------------------------------------+
    |col                                                                              |
    +---------------------------------------------------------------------------------+
    |{chunk, 11, 17, history, {sentence -> 0, chunk -> 0}, []}                        |
    |{chunk, 22, 36, gastroenteritis, {sentence -> 0, chunk -> 1}, []}                |
    |{chunk, 42, 53, stomach pain, {sentence -> 0, chunk -> 2}, []}                   |
    |{chunk, 64, 70, patient, {sentence -> 0, chunk -> 3}, []}                        |
    |{chunk, 81, 110, stomach pain now.We don't care, {sentence -> 0, chunk -> 4}, []}|
    |{chunk, 118, 132, gastroenteritis, {sentence -> 0, chunk -> 5}, []}              |
    +---------------------------------------------------------------------------------+

    >>> result.selectExpr("explode(filtered)").show(truncate=False)
    +-------------------------------------------------------------------+
    |col                                                                |
    +-------------------------------------------------------------------+
    |{chunk, 22, 36, gastroenteritis, {sentence -> 0, chunk -> 1}, []}  |
    |{chunk, 118, 132, gastroenteritis, {sentence -> 0, chunk -> 5}, []}|
    +-------------------------------------------------------------------+

    """

    name = "ChunksFilterApproach"

    whiteList = Param(
        Params._dummy(),
        "whiteList",
        "If defined, list of entities to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    regex = Param(
        Params._dummy(),
        "regex",
        "If defined, list of entities to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    filterValue = Param(
        Params._dummy(),
        "filterValue",
        "possibles values result|entity.",
        typeConverter=TypeConverters.toString
    )

    criteria = Param(Params._dummy(), "criteria",
                     "Select mode",
                     TypeConverters.toString)

    entitiesConfidenceResource = Param(Params._dummy(),
                                       "entitiesConfidenceResource",
                                       "Path to csv with  entity pairs to remove based on the confidance level",
                                       typeConverter=TypeConverters.identity)

    def setWhiteList(self, value):
        """Sets list of entities to process. The rest will be ignored.

        Parameters
        ----------
        value : list
           If defined, list of entities to process. The rest will be ignored.
        """
        return self._set(whiteList=value)

    def setRegex(self, value):
        """Sets llist of regex to process. The rest will be ignored.

        Parameters
        ----------
        value : list
           List of dash-separated pairs of named entities
        """
        return self._set(regex=value)

    def setCriteria(self, s):
        """Set tag representing what is the criteria to filter the chunks. possibles values (isIn|regex)

        Parameters
        ----------
        s : str
           List of dash-separated pairs of named entities
        """
        return self._set(criteria=s)

    def setFilterEntity(self, s):
        """Set tag representing what is the criteria to filter the chunks. possibles values (assertion|isIn|regex)

        Parameters
        ----------
        s : str
           possibles values result|entity.
        """
        return self._set(filterValue=s)

    def setEntitiesConfidenceResource(self, path, read_as=ReadAs.TEXT, options=None):
        if options is None:
            options = {"delimiter": ","}
        return self._set(entitiesConfidenceResource=ExternalResource(path, read_as, options))

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkFiltererApproach"):
        super(ChunkFiltererApproach, self).__init__(classname=classname)

    def _create_model(self, java_model):
        return ChunkFilterer(java_model=java_model)


class ChunkFilterer(AnnotatorModel):
    """ Model that Filters entities coming from CHUNK annotations. Filters can be set via a white list of terms or a regular expression.
        White list criteria is enabled by default. To use regex, `criteria` has to be set to `regex`.This model was trained using the ChunkFiltererApproach
        and has embeded the list of pairs (entity,confidenceThreshold).

       ==============================  ======================
       Input Annotation types          Output Annotation type
       ==============================  ======================
       ``DOCUMENT, CHUNK, ASSERTION``  ``CHUNK``
       ==============================  ======================

       Parameters
       ----------
       whiteList
           If defined, list of entities to process. The rest will be ignored
       regex
           If defined, list of entities to process. The rest will be ignored.
       criteria
              Tag representing what is the criteria to filter the chunks. possibles values (assertion|isIn|regex)
                   isIn : Filter by the chunk
                   regex : Filter using a regex

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
       >>> data = spark.createDataFrame([["Has a past history of gastroenteritis and stomach pain, however patient ..."]]).toDF("text")
       >>> docAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
       >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
       >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
       >>> posTagger = PerceptronModel.pretrained() \
       ...    .setInputCols(["sentence", "token"]) \
       ...    .setOutputCol("pos")
       >>> chunker = Chunker() \
       ...   .setInputCols(["pos", "sentence"]) \
       ...   .setOutputCol("chunk") \
       ...   .setRegexParsers(["(<NN>)+"])
       ...
       >>> chunkerFilter = ChunkFilterer() \
       ...   .setInputCols(["sentence","chunk"]) \
       ...   .setOutputCol("filtered") \
       ...   .setCriteria("isin") \
       ...   .setWhiteList(["gastroenteritis"])
       ...
       >>> pipeline = Pipeline(stages=[
       ...   docAssembler,
       ...   sentenceDetector,
       ...   tokenizer,
       ...   posTagger,
       ...   chunker,
       ...   chunkerFilter])
       ...
       >>> result = pipeline.fit(data).transform(data)
       >>> result.selectExpr("explode(chunk)").show(truncate=False)


       >>> result.selectExpr("explode(chunk)").show(truncate=False)
       +---------------------------------------------------------------------------------+
       |col                                                                              |
       +---------------------------------------------------------------------------------+
       |{chunk, 11, 17, history, {sentence -> 0, chunk -> 0}, []}                        |
       |{chunk, 22, 36, gastroenteritis, {sentence -> 0, chunk -> 1}, []}                |
       |{chunk, 42, 53, stomach pain, {sentence -> 0, chunk -> 2}, []}                   |
       |{chunk, 64, 70, patient, {sentence -> 0, chunk -> 3}, []}                        |
       |{chunk, 81, 110, stomach pain now.We don't care, {sentence -> 0, chunk -> 4}, []}|
       |{chunk, 118, 132, gastroenteritis, {sentence -> 0, chunk -> 5}, []}              |
       +---------------------------------------------------------------------------------+

       >>> result.selectExpr("explode(filtered)").show(truncate=False)
       +-------------------------------------------------------------------+
       |col                                                                |
       +-------------------------------------------------------------------+
       |{chunk, 22, 36, gastroenteritis, {sentence -> 0, chunk -> 1}, []}  |
       |{chunk, 118, 132, gastroenteritis, {sentence -> 0, chunk -> 5}, []}|
       +-------------------------------------------------------------------+
         """
    name = "ChunkFilterer"

    whiteList = Param(
        Params._dummy(),
        "whiteList",
        "If defined, list of entities to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    regex = Param(
        Params._dummy(),
        "regex",
        "If defined, list of entities to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    filterValue = Param(
        Params._dummy(),
        "filterValue",
        "possibles values result|entity.",
        typeConverter=TypeConverters.toString
    )

    criteria = Param(Params._dummy(), "criteria",
                     "Select mode",
                     TypeConverters.toString)

    def setWhiteList(self, value):
        return self._set(whiteList=value)

    def setRegex(self, value):
        return self._set(regex=value)

    def setFilterEntity(self, s):
        return self._set(filterValue=s)

    def setCriteria(self, s):
        return self._set(criteria=s)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkFilterer", java_model=None):
        super(ChunkFilterer, self).__init__(
            classname=classname,
            java_model=java_model
        )