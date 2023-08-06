from sparknlp.common import *

class Router(AnnotatorModel):
    """
    Convert chunks from regexMatcher to chunks with a entity in the metadata.
    Use the identifier or field as a entity.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``ANY``                ``ANY``
    ====================== ======================

    Parameters
    ----------
    inputType
        The type of the entity that you want to filter by default sentence_embeddings.Possible values
        ``document|token|wordpiece|word_embeddings|sentence_embeddings|category|date|sentiment|pos|chunk|named_entity|regex|dependency|labeled_dependency|language|keyword``
    filterFieldsElements
        The filterfieldsElements are the allowed values for the metadata field that is being used
    metadataField
        The key in the metadata dictionary that you want to filter (by default ``entity``)

    Examples
    --------

    >>> test_data = spark.createDataFrame(sentences).toDF("text")
    >>> document = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentence = SentenceDetector().setInputCols("document").setOutputCol("sentence")
    >>> regexMatcher = RegexMatcher().setExternalRules("../src/test/resources/regex-matcher/rules2.txt", ",") \\
    ...     .setInputCols("sentence") \\
    ...     .setOutputCol("regex") \\
    ...     .setStrategy("MATCH_ALL")
    >>> chunk2Doc = Chunk2Doc().setInputCols("regex").setOutputCol("doc_chunk")
    >>> embeddings = BertSentenceEmbeddings.pretrained("sent_small_bert_L2_128") \\
    ...     .setInputCols("doc_chunk") \\
    ...     .setOutputCol("bert") \\
    ...     .setCaseSensitive(False) \\
    ...     .setMaxSentenceLength(32)
    >>> router_name_embeddings = Router() \\
    ...     .setInputType("sentence_embeddings") \\
    ...     .setInputCols("bert") \\
    ...     .setMetadataField("identifier") \\
    ...     .setFilterFieldsElements(["name"]) \\
    ...     .setOutputCol("names_embeddings")\
    >>> router_city_embeddings = Router() \\
    ...     .setInputType("sentence_embeddings") \\
    ...     .setInputCols(["bert"]) \\
    ...     .setMetadataField("identifier") \\
    ...     .setFilterFieldsElements(["city"]) \\
    ...     .setOutputCol("cities_embeddings")
    >>> router_names = Router() \\
    ...     .setInputType("chunk") \\
    ...     .setInputCols("regex") \\
    ...     .setMetadataField("identifier") \\
    ...     .setFilterFieldsElements(["name"]) \\
    ...     .setOutputCol("names_chunks")
    >>> pipeline = Pipeline().setStages(
    >>>     [document, sentence, regexMatcher, chunk2Doc, router_names, embeddings, router_name_embeddings,
    ...      router_city_embeddings])
    """
    name = "Router"

    inputType = Param(Params._dummy(), "inputType",
                      "The type of the entity that you want to filter by default sentence_embeddings.Possible values document|token|wordpiece|word_embeddings|"
                      "sentence_embeddings|category|date|sentiment|pos|chunk|named_entity|regex|dependency|labeled_dependency|language|keyword ",
                      TypeConverters.toString)

    filterFieldsElements = Param(Params._dummy(), "filterFieldsElements",
                                 "The filterfieldsElements are the allowed values for the metadata field that is being used",
                                 TypeConverters.toListString)
    metadataField = Param(Params._dummy(), "metadataField",
                          "The key in the metadata dictionary that you want to filter (by default 'entity')",
                          TypeConverters.toString)

    def setInputType(self, value):
        """Sets the type of the entity that you want to filter by default sentence_embedding

        Parameters
        ----------
        value : int
            The type of the entity that you want to filter by default sentence_embedding
        """
        return self._set(inputType=value)

    def setFilterFieldsElements(self, value):
        """Sets the filterfieldsElements are the allowed values for the metadata field that is being used

        Parameters
        ----------
        value : list
           The filterfieldsElements are the allowed values for the metadata field that is being used
        """
        return self._set(filterFieldsElements=value)

    def setMetadataField(self, value):
        """Sets the key in the metadata dictionary that you want to filter (by default 'entity')

        Parameters
        ----------
        value : str
           The key in the metadata dictionary that you want to filter (by default 'entity')
        """
        return self._set(metadataField=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.Router", java_model=None):
        super(Router, self).__init__(
            classname=classname,
            java_model=java_model
        )
