from sparknlp.common import *


class ChunkConverter(AnnotatorModel):
    """
    Convert chunks from regexMatcher to chunks with a entity in the metadata.
    Use the identifier or field as a entity.

    Examples
    --------

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``CHUNK``               ``CHUNK``
    ====================== ======================

    >>> test_data = spark.createDataFrame([
    ...    (1,"My first sentence with the first rule. This is my second sentence with ceremonies rule."),
    ...    ]).toDF("id", "text")
    >>> document_assembler = DocumentAssembler().setInputCol('text').setOutputCol('document')
    >>> sentence_detector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> regex_matcher = RegexMatcher()\
    ...    .setInputCols("sentence")\
    ...    .setOutputCol("regex")\
    ...    .setExternalRules(path="../src/test/resources/regex-matcher/rules.txt",delimiter=",")
    >>> chunkConverter = ChunkConverter().setInputCols("regex").setOutputCol("chunk")
    >>> pipeline = Pipeline(stages=[document_assembler, sentence_detector, regex_matcher, regex_matcher,chunkConverter])
    >>> model = pipeline.fit(test_data)
    >>> outdf = model.transform(test_data)
    +------------------------------------------------------------------------------------------------+
    |col                                                                                             |
    +------------------------------------------------------------------------------------------------+
    |[chunk, 23, 31, the first, [identifier -> NAME, sentence -> 0, chunk -> 0, entity -> NAME], []] |
    |[chunk, 71, 80, ceremonies, [identifier -> NAME, sentence -> 1, chunk -> 0, entity -> NAME], []]|
    +------------------------------------------------------------------------------------------------+

    """
    name = "ChunkConverter"

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkConverter", java_model=None):
        super(ChunkConverter, self).__init__(
            classname=classname,
            java_model=java_model
        )
