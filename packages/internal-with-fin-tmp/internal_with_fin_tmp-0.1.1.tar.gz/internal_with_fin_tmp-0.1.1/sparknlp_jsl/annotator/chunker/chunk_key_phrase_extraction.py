from sparknlp.common import *
from sparknlp.annotator.embeddings.bert_sentence_embeddings import BertSentenceEmbeddings

class ChunkKeyPhraseExtraction(BertSentenceEmbeddings):
    """
    Chunk KeyPhrase Extraction uses Bert Sentence Embeddings to determine the most relevant key phrases describing a
    text. The input to the model consists of chunk annotations and sentence or document annotation. The model compares
    the chunks against the corresponding sentences/documents and selects the chunks which are most representative of
    the broader text context (i.e. the document or the sentence they belong to). The key phrases candidates (i.e. the
    input chunks) can be generated in various ways, e.g. by NGramGenerator, TextMatcher or NerConverter. The model
    operates either at sentence (selecting the most descriptive chunks from the sentence they belong to) or at document
    level. In the latter case, the key phrases are selected to represent all the input document annotations.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``DOCUMENT, CHUNK``    ``CHUNK``
    ====================== ======================

    Parameters
    ----------

    topN
        The number of key phrases to select.
    selectMostDifferent
        Finds the topN * 2 key phrases and then selects topN of them, such as that they are the most different from
        each other
    divergence
        The divergence value determines how different from each the extracted key phrases are. Uses Maximal Marginal
        Relevance (MMR). MMR should not be used in conjunction with selectMostDifferent as they aim to achieve the same
        goal, but in different ways.
    documentLevelProcessing
        Extract key phrases from the whole document  from particular sentences which the chunks refer to.
    concatenateSentences
        Concatenate the input sentence/documentation annotations before computing their embeddings.

    Examples
    --------


    >>> documenter = sparknlp.DocumentAssembler() \
    ...     .setInputCol("text") \
    ...     .setOutputCol("document")
    ...
    >>> sentencer = sparknlp.annotators.SentenceDetector() \
    ...     .setInputCols(["document"])\
    ...     .setOutputCol("sentences")
    ...
    >>> tokenizer = sparknlp.annotators.Tokenizer() \
    ...     .setInputCols(["document"]) \
    ...     .setOutputCol("tokens") \
    ...
    >>>  embeddings = sparknlp.annotators.WordEmbeddingsModel() \
    ...     .pretrained("embeddings_clinical", "en", "clinical/models") \
    ...     .setInputCols(["document", "tokens"]) \
    ...     .setOutputCol("embeddings")
    ...
    >>> ner_tagger = MedicalNerModel() \
    ...     .pretrained("ner_jsl_slim", "en", "clinical/models") \
    ...     .setInputCols(["sentences", "tokens", "embeddings"]) \
    ...     .setOutputCol("ner_tags")
    ...
    >>> ner_converter = NerConverter()\
    ...     .setInputCols("sentences", "tokens", "ner_tags")\
    ...     .setOutputCol("ner_chunks")
    ...
    >>> key_phrase_extractor = ChunkKeyPhraseExtraction\
    ...     .pretrained()\
    ...     .setTopN(1)\
    ...     .setDocumentLevelProcessing(False)\
    ...     .setDivergence(0.4)\
    ...     .setInputCols(["sentences", "ner_chunks"])\
    ...     .setOutputCol("ner_chunk_key_phrases")
    ...
    >>> pipeline = sparknlp.base.Pipeline() \
    ...     .setStages([documenter, sentencer, tokenizer, embeddings, ner_tagger, ner_converter, key_phrase_extractor])
    ...
    >>> data = spark.createDataFrame([["Her Diabetes has become type 2 in the last year with her Diabetes.He complains of swelling in his right forearm."]]).toDF("text")
    >>> results = pipeline.fit(data).transform(data)
    >>> results\
    ...     .selectExpr("explode(ner_chunk_key_phrases) AS key_phrase")\
    ...     .selectExpr(
    ...         "key_phrase.result",
    ...         "key_phrase.metadata.entity",
    ...         "key_phrase.metadata.DocumentSimilarity",
    ...         "key_phrase.metadata.MMRScore")\
    ...     .show(truncate=False)

    +-----------------------------+------------------+-------------------+
    |result                       |DocumentSimilarity|MMRScore           |
    +-----------------------------+------------------+-------------------+
    |gestational diabetes mellitus|0.7391447825527298|0.44348688715422274|
    |28-year-old                  |0.4366776288430703|0.13577881610104517|
    |type two diabetes mellitus   |0.7323921930094919|0.085800103824974  |
    +-----------------------------+------------------+-------------------+

    """

    name = "ChunkKeyPhraseExtraction"

    topN = Param(Params._dummy(),
                 "topN",
                 "Number of key phrases to extract, ordered by their score",
                 typeConverter=TypeConverters.toInt
                 )

    def setTopN(self, value):
        """Set the number of key phrases to extract. The default value is 3.

        Parameters
        ----------
        value : integer
           Number of key phrases to extract.
        """
        return self._set(topN=value)

    divergence = Param(Params._dummy(),
                       "divergence",
                       "The divergence value determines how different from each the extracted key phrases are. "
                       "The value must be in the the interval [0, 1]. The higher the value is, "
                       "the more divergence is enforced.  The default value is 0.2.",
                       typeConverter=TypeConverters.toFloat
                       )

    def setDivergence(self, value):
        """Set the level of divergence of the extracted key phrases. The value should be in the interval [0, 1].
            This parameter should not be used if setSelectMostDifferent is true - the two parameters aim to achieve the
            same goal in different ways. The default is 0, i.e. there is no constraint on the order of key phrases
             extracted.

        Parameters
        ----------
        value : float
           Divergence value
        """
        return self._set(divergence=value)

    selectMostDifferent = Param(Params._dummy(),
                                "selectMostDifferent",
                                "Find the topN * 2 key phrases and then select topN of them, such as that they are the "
                                "most different from each other",
                                typeConverter=TypeConverters.toBoolean
                                )

    def setSelectMostDifferent(self, value):
        """Let the model return the top N key phrases which are the most different from each other. Using this paramter
        only makes sense if the divergence parameter is set to 0. The default value is 'false'

        Parameters
        ----------
        value : boolean
           whether to select the most different key phrases or not.
        """
        return self._set(selectMostDifferent=value)

    documentLevelProcessing = Param(Params._dummy(),
                                    "documentLevelProcessing",
                                    "Let the model extract key phrase at the document or at the sentence level",
                                    typeConverter=TypeConverters.toBoolean
                                    )

    def setDocumentLevelProcessing(self, value):
        """Extract key phrases from the whole document or from particular sentences which the chunks refer to.
         The default value is 'false'.

        Parameters
        ----------
        value : boolean
           Whether to extract key phrases from the whole document(all sentences).
        """
        return self._set(documentLevelProcessing=value)

    concatenateSentences = Param(Params._dummy(),
                                 "concatenateSentences",
                                 "Concatenate input sentence annotations before computing their embedding.",
                                 typeConverter=TypeConverters.toBoolean
                                 )

    def setConcatenateSentences(self, value):
        """Concatenate the input sentence/documentation annotations before computing their embeddings. This parameter
        is only used if documentLevelProcessing is true. If concatenateSentences is set to true, the model will
        concatenate the document/sentence input annotations and compute a single embedding. If it is false, the model
        will compute the embedding of each sentence separately and then average the resulting embedding vectors.
        The default value is 'false'.

        Parameters
        ----------
        value : boolean
           Whether to concatenate the input sentence/document annotations in order to compute the embedding of the
           whole document.
        """
        return self._set(concatenateSentences=value)

    dropPunctuation = Param(Params._dummy(),
                            "dropPunctuation",
                            "Remove punctuation marks from input chunks.",
                            typeConverter=TypeConverters.toBoolean
                            )

    def setDropPunctuation(self, value):
        """This parameter determines whether to remove punctuation marks from the input chunks. Chunks coming from NER
        models are not affected.
        The default value is 'true'.

        Parameters
        ----------
        value : boolean
           Whether to remove punctuation marks from input chunks.
        """
        return self._set(dropPunctuation=value)

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.embeddings.ChunkKeyPhraseExtraction", java_model=None):
        super(ChunkKeyPhraseExtraction, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            dimension=768,
            batchSize=8,
            maxSentenceLength=128,
            caseSensitive=False,
            divergence=0.0,
            documentLevelProcessing=True,
            topN=3,
            selectMostDifferent=False,
            concatenateSentences=True,
            dropPunctuation=True
        )

    @staticmethod
    def pretrained(name="sbert_jsl_medium_uncased", lang="en", remote_loc="clinical/models"):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(ChunkKeyPhraseExtraction, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')