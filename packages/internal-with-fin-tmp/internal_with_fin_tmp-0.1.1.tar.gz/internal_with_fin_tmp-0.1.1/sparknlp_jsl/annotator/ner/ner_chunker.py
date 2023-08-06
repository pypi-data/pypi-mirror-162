from sparknlp.common import *

class NerChunker(AnnotatorModel):
    """Extracts phrases that fits into a known pattern using the NER tags. Useful for entity groups with neighboring tokens
       when there is no pretrained NER model to address certain issues. A Regex needs to be provided to extract the tokens
       between entities.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK``                       ``NAMED_ENTITY``
    ========================================= ======================

    Parameters
    ----------
    setRegexParsers
        A list of regex patterns to match chunks, for example: [“‹DT›?‹JJ›*‹NN”]

    Examples
    --------

    >>> import sparknlp
    >>> from sparknlp.base import *
    >>> from sparknlp_jsl.base import *
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
    ...    .setOutputCol("embeddings") \
    ...    .setCaseSensitive(False)
    ...
    >>> ner = MedicalNerModel.pretrained("ner_radiology", "en", "clinical/models") \\
    ...    .setInputCols(["sentence", "token","embeddings"]) \\
    ...    .setOutputCol("ner") \
    ...    .setCaseSensitive(False)
    ...
    >>> chunker = NerChunker() \\
    ...    .setInputCols(["sentence","ner"]) \\
    ...    .setChunkCol("ner_chunk") \\
    ...    .setOutputCol("chunk")
    ...    .setRegexParsers(Array("<ImagingFindings>.*<BodyPart>"))
    ...
    ...
    >>> pipeline = Pipeline(stages=[
    ...    document_assembler,
    ...    sentence_detector,
    ...    tokenizer,
    ...    embeddings,
    ...    ner,
    ...    chunker
    ...])
    >>> result = pipeline.fit.fit(dataset).transform(dataset)

    """

    name = "NerChunker"

    regexParsers = Param(Params._dummy(), "regexParsers", "an array of grammar based chunk parsers",
                         TypeConverters.toListString)

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.ner.NerChunker",
                 java_model=None):
        super(NerChunker, self).__init__(
            classname=classname,
            java_model=java_model
        )

    def setRegexParsers(self, b):
        """
        Sets list of regex patterns to match chunks, for example: Array(“‹DT›?‹JJ›*‹NN›”

        Parameters
        ----------
        b : List[String]
             list of regex patterns to match chunks, for example: Array(“‹DT›?‹JJ›*‹NN›”
        """
        return self._set(regexParsers=b)

