from sparknlp.annotator import BertSentenceEmbeddings
from sparknlp.common import *


class BertSentenceChunkEmbeddings(BertSentenceEmbeddings):
    """
    BERT Sentence embeddings for chunk annotations which take into account the context of the sentence the chunk appeared in.
    This is an extension of BertSentenceEmbeddings which combines the embedding of a chunk with the embedding of the
    surrounding sentence. For each input chunk annotation, it finds the corresponding sentence, computes
    the BERT sentence embedding of both the chunk and the sentence and averages them. The resulting embeddings are
    useful in cases, in which one needs a numerical representation of a text chunk which is sensitive to
    the context it appears in.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``DOCUMENT, CHUNK``    ``SENTENCE_EMBEDDINGS``
    ====================== ======================

    Parameters
    ----------
    chunkWeight
        Relative weight of chunk embeddings in comparison to sentence embeddings. The value should between 0 and 1.
        The default is 0.5, which means the chunk and sentence embeddings are given equal weight.

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

    First extract the prerequisites for the NerDLModel

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
    >>> nerConverter = NerConverter() \\
    ...     .setInputCols(["sentence", "token","ner"]) \\
    ...     .setOutputCol("ner_chunk")
    >>> embeddings = BertSentenceChunkEmbeddings.pretrained("sbluebert_base_uncased_mli", "en", "clinical/models") \\
    ...     .setInputCols(["sentence", "ner_chunk"]) \\
    ...     .setOutputCol("sentence_chunk_embeddings")
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     sentence,
    ...     tokenizer,
    ...     embeddings,
    ...     nerTagger,
    ...     nerConverter
    ...     embeddings
    ... ])
    >>> data = spark.createDataFrame([["Her Diabetes has become type 2 in the last year with her Diabetes.He complains of swelling in his right forearm."]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    >>> result
    ...   .selectExpr("explode(sentence_chunk_embeddings) AS s")
    ...   .selectExpr("s.result", "slice(s.embeddings, 1, 5) AS averageEmbedding")
    ...   .show(truncate=false)
    +-----------------------------+-----------------------------------------------------------------+
    |                       result|                                                 averageEmbedding|
    +-----------------------------+-----------------------------------------------------------------+
    |Her Diabetes                 |[-0.31995273, -0.04710883, -0.28973156, -0.1294758, 0.12481072]  |
    |type 2                       |[-0.027161136, -0.24613449, -0.0949309, 0.1825444, -0.2252143]   |
    |her Diabetes                 |[-0.31995273, -0.04710883, -0.28973156, -0.1294758, 0.12481072]  |
    |swelling in his right forearm|[-0.45139068, 0.12400375, -0.0075617577, -0.90806055, 0.12871636]|
    +-----------------------------+-----------------------------------------------------------------+

    """

    name = "BertSentenceChunkEmbeddings"

    chunkWeight = Param(Params._dummy(),
                        "chunkWeight",
                        "Relative weight of chunk embeddings in comparison to sentence embeddings. The value should between 0 and 1."
                        "The default is 0.5, which means the chunk and sentence embeddings are given equal weight.",
                        typeConverter=TypeConverters.toFloat
                        )

    def setChunkWeight(self, value):
        """Sets  the relative weight of chunk embeddings in comparison to sentence embeddings. The value should between 0 and 1.
           The default is 0.5, which means the chunk and sentence embeddings are given equal weight.

        Parameters
        ----------
        value : float
           Relative weight of chunk embeddings in comparison to sentence embeddings. The value should between 0 and 1.
           The default is 0.5, which means the chunk and sentence embeddings are given equal weight.
        """
        return self._set(chunkWeight=value)

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.embeddings.BertSentenceChunkEmbeddings", java_model=None):
        super(BertSentenceChunkEmbeddings, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            dimension=768,
            batchSize=8,
            maxSentenceLength=128,
            caseSensitive=False,
            chunkWeight=0.5
        )

    @staticmethod
    def pretrained(name="sent_small_bert_L2_768", lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(BertSentenceChunkEmbeddings, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')
    @staticmethod
    def load(path):
        from sparknlp_jsl.internal import _BertSentenceEmbeddingsToBertSentenceChunkEmbeddingsLoader
        jModel = _BertSentenceEmbeddingsToBertSentenceChunkEmbeddingsLoader(path)._java_obj
        return BertSentenceChunkEmbeddings(java_model=jModel)