from sparknlp.common import *

class IOBTagger(AnnotatorModel):
    """
    Merges token tags and NER labels from chunks in the specified format.
    For example output columns as inputs from

    ==========================================  ======================
    Input Annotation types                      Output Annotation type
    ==========================================  ======================
    ``TOKEN, CHUNK``                            ``NAMED_ENTITY``
    ==========================================  ======================

    Parameters
    ----------
    Scheme
        Format of tags, either IOB or BIOES

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
    >>> nerConverter = NerConverter().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")
    ...
    >>> iobTagger = IOBTagger().setInputCols(["token", "ner_chunk"]).setOutputCol("ner_label")
    >>> pipeline = Pipeline(stages=[documentAssembler, sentenceDetector, tokenizer, embeddings, nerModel, nerConverter, iobTagger])
    ...
    >>> result.selectExpr("explode(ner_label) as a") \
    ...   .selectExpr("a.begin","a.end","a.result as chunk","a.metadata.word as word") \
    ...   .where("chunk!='O'").show(5, False)
    +-----+---+-----------+-----------+
    |begin|end|chunk      |word       |
    +-----+---+-----------+-----------+
    |5    |15 |B-Age      |63-year-old|
    |17   |19 |B-Gender   |man        |
    |64   |72 |B-Modifier |recurrent  |
    |98   |107|B-Diagnosis|cellulitis |
    |110  |119|B-Diagnosis|pneumonias |
    +-----+---+-----------+-----------+
    """

    name = "IOBTaggerModel"

    scheme = Param(Params._dummy(), "scheme", "Format of tags, either IOB or BIOES",
                   typeConverter=TypeConverters.toString)

    def setScheme(self, f):
        """Sets format of tags, either IOB or BIOES

        Parameters
        ----------
        pairs : str
            Format of tags, either IOB or BIOES
        """
        return self._set(scheme=f)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.ner.IOBTagger",
                 java_model=None):
        super(IOBTagger, self).__init__(
            classname=classname,
            java_model=java_model
        )
