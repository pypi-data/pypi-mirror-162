from sparknlp.common import *

class ChunkSentenceSplitter(AnnotatorModel):
    """
    Split the document using the chunks that you provided,and put in the metadata the chunk entity.
    The first piece of documento to the first chunk will have the entity as header.

    Use the identifier or field as a entity.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``DOCUMENT, CHUNK``    ``DOCUMENT``
    ====================== ======================

    Parameters
    ----------
    inputType
        The type of the entity that you want to filter by default sentence_embeddings.Possible values
        ``document|token|wordpiece|word_embeddings|sentence_embeddings|category|date|sentiment|pos|chunk|named_entity|regex|dependency|labeled_dependency|language|keyword``
    Examples
    --------
    >>> document = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> regexMatcher = RegexMatcher().setExternalRules("../src/test/resources/chunker/title_regex.txt", ",") \\
    ...     .setInputCols("document") \\
    ...     .setOutputCol("chunks") \\
    >>> chunkSentenceSplitter = ChunkSentenceSplitter().setInputCols("chunks","document").setOutputCol("paragraphs")
    >>> pipeline = Pipeline().setStages([documentAssembler,regexMatcher,chunkSentenceSplitter])
    >>> result = pipeline.fit(data).transform(data).select("paragraphs")
    >>> result.show()

    """

    groupBySentences = Param(Params._dummy(), "groupBySentences",
                             "This parameter allow split the paragraphs grouping the chunks by sentences." +
                             "if is false we assume that we have 1 document annotations and all chunks are for this document." +
                             "Use false if the input column of your chunk annotator was a sentenceDetector column."
                             "Use true when we have a sentence detector as input column or when the document have many sentences per row",
                             TypeConverters.toBoolean)

    insertChunk = Param(Params._dummy(), "insertChunk", "Whether to insert the chunk in the paragraph or not",
                        TypeConverters.toBoolean)

    defaultEntity = Param(Params._dummy(), "defaultEntity",
                          "Add the default name for the entity that is between the init of the document and the first chunk",
                          TypeConverters.toString)

    name = "ChunkSentenceSplitter"

    def setGroupBySentences(self, value):
        """Sets the groupBySentences that allow split the paragraphs grouping the chunks by sentences.
            If is false we assume that we have 1 document annotations and all chunks are for this document.
            Use false if the input column of your chunk annotator was a sentenceDetector column.
            Use true when we have a sentence detector as input column or when the document have many sentences per row

        Parameters
        ----------
        value : Boolean
           Allow split the paragraphs grouping the chunks by sentences
        """
        return self._set(groupBySentences=value)

    def setInsertChunk(self, value):
        """Whether to insert the chunk in the paragraph or not.

        Parameters
        ----------
        value : Boolean
           Whether to insert the chunk in the paragraph or not.
        """
        return self._set(insertChunk=value)

    def setDefaultEntity(self, value):
        """Sets the key in the metadata dictionary that you want to filter (by default 'entity')

        Parameters
        ----------
        value : str
           The key in the metadata dictionary that you want to filter (by default 'entity')
        """
        return self._set(defaultEntity=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkSentenceSplitter", java_model=None):
        super(ChunkSentenceSplitter, self).__init__(
            classname=classname,
            java_model=java_model
        )