from sparknlp.common import *
from sparknlp_jsl.annotator.classification.medical_bert_for_sequence_classification import MedicalBertForSequenceClassification


class ZeroShotRelationExtractionModel(MedicalBertForSequenceClassification):
    """
    ZeroShotRelationExtractionModel implements zero shot binary relations extraction by utilizing BERT transformer
    models trained on the NLI (Natural Language Inference) task. The model inputs consists of documents/sentences and
    paired NER chunks, usually obtained by RENerChunksFilter. The definitions of relations which are extracted is given
    by a dictionary structures, specifying a set of statements regarding the relationship of named entities. These
    statements are automatically appended to each document in the dataset and the NLI model is used to determine
     whether a particular relationship between entities.

    ==========================================  ======================
    Input Annotation types                      Output Annotation type
    ==========================================  ======================
    ``CHUNK, DOCUMENT``                         ``CATEGORY``
    ==========================================  ======================

    Parameters
    ----------
    relationalCategories
        A dictionary with definitions of relational categories. The keys of dictionary are the relation labels and the
        values are lists of hypothesis templates. For example:
              {"CURE": [
                    "{TREATMENT, DRUG} cures {PROBLEM}."
                    ],
                "IMPROVE": [
                    "{TREATMENT} improves {PROBLEM}.",
                    "{TREATMENT} cures {PROBLEM}."
                    ]}
    predictionThreshold
        Minimal confidence score to encode a relation (Default: 0.5f)
    multiLabel
        Whether or not a pair of entities can be categorized by multiple relations (Default: False)

    Examples
    --------
    >>> documentAssembler = DocumentAssembler()
    >>> documenter = sparknlp.DocumentAssembler() \
    ...     .setInputCol("text") \
    ...     .setOutputCol("document")
    >>> tokenizer = sparknlp.annotators.Tokenizer() \
    ...     .setInputCols(["document"]) \
    ...     .setOutputCol("tokens")
    >>> sentencer = sparknlp.annotators.SentenceDetector()\
    ...     .setInputCols(["document"])\
    ...     .setOutputCol("sentences")
    >>> words_embedder = sparknlp.annotators.WordEmbeddingsModel() \
    ...     .pretrained("embeddings_clinical", "en", "clinical/models") \
    ...     .setInputCols(["sentences", "tokens"]) \
    ...     .setOutputCol("embeddings")
    >>> pos_tagger = sparknlp.annotators.PerceptronModel() \
    ...     .pretrained("pos_clinical", "en", "clinical/models") \
    ...     .setInputCols(["sentences", "tokens"]) \
    ...     .setOutputCol("pos_tags")
    >>> ner_tagger = MedicalNerModel() \
    ...     .pretrained("ner_clinical", "en", "clinical/models") \
    ...     .setInputCols(["sentences", "tokens", "embeddings"]) \
    ...     .setOutputCol("ner_tags")
    >>> ner_converter = sparknlp.annotators.NerConverter() \
    ...     .setInputCols(["sentences", "tokens", "ner_tags"]) \
    ...     .setOutputCol("ner_chunks")
    >>> dependency_parser = sparknlp.annotators.DependencyParserModel() \
    ...     .pretrained("dependency_conllu", "en") \
    ...     .setInputCols(["document", "pos_tags", "tokens"]) \
    ...     .setOutputCol("dependencies")
    >>> re_ner_chunk_filter = RENerChunksFilter() \
    ...     .setRelationPairs(["problem-test","problem-treatment"]) \
    ...     .setMaxSyntacticDistance(4)\
    ...     .setDocLevelRelations(False)\
    ...     .setInputCols(["ner_chunks", "dependencies"]) \
    ...     .setOutputCol("re_ner_chunks")
    >>> re_model = ZeroShotRelationExtractionModel \
    ...     .load("/tmp/spark_sbert_zero_shot") \
    ...     .setRelationalCategories({
    ...         "CURE": ["{TREATMENT} cures {PROBLEM}."],
    ...         "IMPROVE": ["{TREATMENT} improves {PROBLEM}.", "{TREATMENT} cures {PROBLEM}."],
    ...         "REVEAL": ["{TEST} reveals {PROBLEM}."]})\
    ...     .setMultiLabel(False)\
    ...     .setInputCols(["re_ner_chunks", "sentences"]) \
    ...     .setOutputCol("relations")
    >>> data = spark.createDataFrame(
    ...     [["Paracetamol can alleviate headache or sickness. An MRI test can be used to find cancer."]]
    ...     ).toDF("text")
    >>> results = sparknlp.base.Pipeline() \
    ...     .setStages([documenter, tokenizer, sentencer, words_embedder, pos_tagger, ner_tagger, ner_converter,
    ...         dependency_parser, re_ner_chunk_filter, re_model]) \
    ...     .fit(data) \
    ...     .transform(data) \
    >>> results\
    ...     .selectExpr("explode(relations) as relation")\
    ...     .selectExpr("relation.result", "relation.metadata.confidence")\
    ...     .show(truncate=False)
+-------+----------+
|result |confidence|
+-------+----------+
|REVEAL |0.9760039 |
|IMPROVE|0.98819494|
|IMPROVE|0.9929625 |
+-------+----------+
"""
    relationalCategories = Param(Params._dummy(),
                                 "relationalCategories",
                                 "Definitions of relational categories",
                                 TypeConverters.identity)

    predictionThreshold = Param(Params._dummy(),
                                "predictionThreshold",
                                "Minimal confidence score to encode a relation (Default: 0.5f)",
                                TypeConverters.toFloat)

    multiLabel = Param(Params._dummy(),
                       "multiLabel",
                       "Whether or not a pair of entities can be categorized by multiple relations (Default: False)",
                       TypeConverters.toBoolean)

    def setRelationalCategories(self, categories):
        """Set definitions of relational categories

        Parameters
        ----------
        categories : dict[str, list[str]]
            xxx
        """
        categories = categories.copy()
        from sparknlp_jsl.internal import RelationalCategories
        return self._set(relationalCategories=RelationalCategories(categories))

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.ZeroShotRelationExtractionModel", java_model=None):
        super(ZeroShotRelationExtractionModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            predictionThreshold=0.5,
            multiLabel=False
        )

    @staticmethod
    def pretrained(name="", lang="en", remote_loc="clinical/models"):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(ZeroShotRelationExtractionModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

    @staticmethod
    def loadSavedModel(folder, spark_session):
        """Loads a locally saved model.

        Parameters
        ----------
        folder : str
            Folder of the saved model
        spark_session : pyspark.sql.SparkSession
            The current SparkSession

        Returns
        -------
        ZeroShotRelationExtractionModel
            The restored model
        """
        from sparknlp_jsl.internal import _ZeroShotRelationExtractionModelLoader
        jModel = _ZeroShotRelationExtractionModelLoader(folder, spark_session._jsparkSession)._java_obj
        return ZeroShotRelationExtractionModel(java_model=jModel)