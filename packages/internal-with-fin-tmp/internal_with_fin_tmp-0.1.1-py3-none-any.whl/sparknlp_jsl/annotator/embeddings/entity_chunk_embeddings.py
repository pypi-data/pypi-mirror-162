from sparknlp.annotator import BertSentenceEmbeddings
from sparknlp.common import *

class EntityChunkEmbeddings(BertSentenceEmbeddings):
    """
    Weighted average embeddings of multiple named entities chunk annotations

    ====================== =======================
    Input Annotation types Output Annotation type
    ====================== =======================
    ``DEPENDENCY, CHUNK``  ``SENTENCE_EMBEDDINGS``
    ====================== =======================

    Parameters
    ----------
    targetEntities
        Target entities and their related entities
    entityWeights
        Relative weights of entities.
    maxSyntacticDistance
        Maximal syntactic distance between related entities. Default value is 2.

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
    >>> documenter = DocumentAssembler()\
    ...     .setInputCol("text")\
    ...     .setOutputCol("documents")
    >>> sentence_detector = SentenceDetector() \
    ...     .setInputCols("documents") \
    ...     .setOutputCol("sentences")
    >>> tokenizer = Tokenizer() \
    ...     .setInputCols("sentences") \
    ...     .setOutputCol("tokens")
    >>> embeddings = WordEmbeddingsModel() \
    ...     .pretrained("embeddings_clinical", "en", "clinical/models")\
    ...     .setInputCols(["sentences", "tokens"])\
    ...     .setOutputCol("embeddings")
    >>> ner_model = MedicalNerModel()\
    ...     .pretrained("ner_posology_large", "en", "clinical/models")\
    ...     .setInputCols(["sentences", "tokens", "embeddings"])\
    ...     .setOutputCol("ner")
    >>> ner_converter = NerConverterInternal()\
    ...     .setInputCols("sentences", "tokens", "ner")\
    ...     .setOutputCol("ner_chunks")
    >>> pos_tager = PerceptronModel()\
    ...     .pretrained("pos_clinical", "en", "clinical/models")\
    ...     .setInputCols("sentences", "tokens")\
    ...     .setOutputCol("pos_tags")
    >>> dependency_parser = DependencyParserModel()\
    ...     .pretrained("dependency_conllu", "en")\
    ...     .setInputCols(["sentences", "pos_tags", "tokens"])\
    ...     .setOutputCol("dependencies")
    >>> drug_chunk_embeddings = EntityChunkEmbeddings()\
    ...     .pretrained("sbiobert_base_cased_mli","en","clinical/models")\
    ...     .setInputCols(["ner_chunks", "dependencies"])\
    ...     .setOutputCol("drug_chunk_embeddings")\
    ...     .setMaxSyntacticDistance(3)\
    ...     .setTargetEntities({"DRUG": []})
    ...     .setEntityWeights({"DRUG": 0.8, "STRENGTH": 0.2, "DOSAGE": 0.2, "FORM": 0.5})
    >>> sampleData = "The parient was given metformin 125 mg, 250 mg of coumadin and then one pill paracetamol"
    >>> data = SparkContextForTest.spark.createDataFrame([[sampleData]]).toDF("text")
    >>> pipeline = Pipeline().setStages([
    ...     documenter,
    ...     sentence_detector,
    ...     tokenizer,
    ...     embeddings,
    ...     ner_model,
    ...     ner_converter,
    ...     pos_tager,
    ...     dependency_parser,
    ...     drug_chunk_embeddings])
    >>> results = pipeline.fit(data).transform(data)
    >>> results = results \
    ...     .selectExpr("explode(drug_chunk_embeddings) AS drug_chunk") \
    ...     .selectExpr("drug_chunk.result", "slice(drug_chunk.embeddings, 1, 5) AS drug_embedding") \
    ...     .cache()
    >>> results.show(truncate=False)
+-----------------------------+-----------------------------------------------------------------+
|                       result|                                                  drug_embedding"|
+-----------------------------+-----------------------------------------------------------------+
|metformin 125 mg             |[-0.267413, 0.07614058, -0.5620966, 0.83838946, 0.8911504]       |
|250 mg coumadin              |[0.22319649, -0.07094894, -0.6885556, 0.79176235, 0.82672405]    |
|one pill paracetamol         |[-0.10939768, -0.29242, -0.3574444, 0.3981813, 0.79609615]       |
+-----------------------------+-----------------------------------------------------------------+
"""
    name = "EntityChunkEmbeddings"

    entityWeights = Param(Params._dummy(),
                          "entityWeights",
                          "Relative weights of named entities.",
                          typeConverter=TypeConverters.identity)

    targetEntities = Param(Params._dummy(),
                           "targetEntities",
                           "Target entities and the entities they are related to.",
                           typeConverter=TypeConverters.identity)

    maxSyntacticDistance = Param(Params._dummy(), "maxSyntacticDistance",
                                 "Maximal syntactic distance between related DRUG and non-DRUG entities",
                                 TypeConverters.toInt)

    def setEntityWeights(self, weights={}):
        """Sets the relative weights of the embeddings of specific entities. By default the dictionary is empty and
         all entities have equal weights. If non-empty and some entity is not in it, then its weight is set to 0.

        Parameters
        ----------
        weights: : dict[str, float]
            Dictionary with the relative weighs of entities. The notation TARGET_ENTITY:RELATED_ENTITY can be used to
            specify the weight of a entity which is related to specific target entity (e.g. "DRUG:SYMPTOM": 0.3).
            Entity names are case-insensitive.
        """
        self._call_java("setEntityWeights",weights)

    def setTargetEntities(self, entities={}):
        """Sets the target entities and maps them to their related entities. A target entity with an empty list of
        related entities means all other entities are assumed to be related to it.

        Parameters
        ----------
        entities: dict[str, list[str]]
            Dictionary with target and related entities (TARGET: [RELATED1, RELATED2,...]). If the list of related
            entities is empty, then all non-target entities are considered.
            Entity names are case insensitive.
        """
        self._call_java("setTargetEntities",entities)

    def setMaxSyntacticDistance(self, distance):
        """Sets the maximal syntactic distance between related entities. Default value is 2.
        Parameters
        ----------
        distance : int
            Maximal syntactic distance
        """
        return self._set(maxSyntacticDistance=distance)

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.embeddings.EntityChunkEmbeddings", java_model=None):
        super(EntityChunkEmbeddings, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            dimension=768,
            batchSize=32,
            maxSentenceLength=128,
            caseSensitive=True,
            maxSyntacticDistance=2
        )

    @staticmethod
    def pretrained(name="sbiobert_base_cased_mli", lang="en", remote_loc="clinical/models"):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(EntityChunkEmbeddings, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')