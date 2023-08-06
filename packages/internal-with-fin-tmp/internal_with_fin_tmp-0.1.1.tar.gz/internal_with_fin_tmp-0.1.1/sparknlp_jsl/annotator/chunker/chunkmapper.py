from sparknlp.common import *

class ChunkMapperApproach(AnnotatorApproach):
    """
    The chunk mapper Approach load a JsonDictionary that have the relations to be mapped in the ChunkMapperModel

    ====================== =======================
    Input Annotation types Output Annotation type
    ====================== =======================
    ``CHUNK``              ``LABEL_DEPENDENCY``
    ====================== =======================

    Parameters
    ----------
    dictionary
        Dictionary path where is the json that contains the mappinmgs columns
    rel
        Relation that we going to use to map the chunk
    lowerCase
        Parameter to decide if we going to use the chunk mapper or not

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
    >>> chunkerMapperapproach = ChunkMapperApproach()\
    ...    .setInputCols(["ner_chunk"])\
    ...    .setOutputCol("mappings")\
    ...    .setDictionary("/home/jsl/mappings2.json") \
    ...    .setRels(["action"]) \
    >>> sampleData = "The patient was given Warfarina Lusa and amlodipine 10 MG."
    >>> pipeline = Pipeline().setStages([
    ...     documenter,
    ...     sentence_detector,
    ...     tokenizer,
    ...     embeddings,
    ...     ner_model,
    ...     ner_converter])
    >>> results = pipeline.fit(data).transform(data)
    >>> results.select("mappings").show(truncate=False)
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|mappings                                                                                                                                                                                                                                                                                                                                                                                               |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|[{labeled_dependency, 22, 35, Analgesic, {chunk -> 0, relation -> action, confidence -> 0.56995, all_relations -> Antipyretic, entity -> Warfarina Lusa, sentence -> 0}, []}, {labeled_dependency, 41, 50, NONE, {entity -> amlodipine, sentence -> 0, chunk -> 1, confidence -> 0.9989}, []}, {labeled_dependency, 55, 56, NONE, {entity -> MG, sentence -> 0, chunk -> 2, confidence -> 0.9123}, []}]|
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

"""
    name = "ChunkMapperApproach"

    dictionary = Param(Params._dummy(),
                       "dictionary",
                       "Path to dictionary file in tsv or csv format",
                       typeConverter=TypeConverters.toString)
    rel = Param(Params._dummy(),
                "rel",
                "Relation for the model",
                typeConverter=TypeConverters.toString)

    lowerCase = Param(Params._dummy(),
                      "lowerCase",
                      "Set if we want to save the dictionary in lower case or not",
                      typeConverter=TypeConverters.toBoolean)

    allowMultiTokenChunk = Param(Params._dummy(),
                                 "allowMultiTokenChunk",
                                 "Whether   skyp relations with multitokens",
                                 typeConverter=TypeConverters.toBoolean)

    multivaluesRelations = Param(Params._dummy(),
                                 "multivaluesRelations",
                                 "Whether  to decide if we want to send multi-chunk tokens or only single token chunks",
                                 typeConverter=TypeConverters.toBoolean)

    rels = Param(Params._dummy(),
                 "rels",
                 "relations to be mappen in the dictionary",
                 typeConverter=TypeConverters.toListString)

    def setDictionary(self, p):
        """Sets if we want to use 'bow' for word embeddings or 'sentence' for sentences"
        Parameters
        ----------
        path : str
            Path where is the dictionary
        """
        return self._set(dictionary=p)

    def setLowerCase(self,lc):
        """Set if we want to save the keys of the dictionary in lower case or not
        Parameters
        ----------
        lc : bool
            Parameter that select if you want to use the keys in lower case or not
        """
        return self._set(lowerCase=lc)

    def setAllowMultiTokenChunk(self,mc):
        """Whether  if we skyp relations with multitokens
        Parameters
        ----------
        mc : bool
            "Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        """
        return self._set(allowMultiTokenChunk=mc)

    def setMultivaluesRelations(self,mc):
        """Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        Parameters
        ----------
         mc : bool
             "Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        """
        return self._set(multivaluesRelations=mc)

    def setRel(self, r):
        return self._set(rel=r)

    def setRels(self, rs):
        return self._set(rels=rs)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkMapperApproach"):
        super(ChunkMapperApproach, self).__init__(
            classname=classname
        )
    def _create_model(self, java_model):
        return ChunkMapperModel(java_model=java_model)


class ChunkMapperModel(AnnotatorModel):
    """
    The chunk mapper Approach load a JsonDictionary that have the relations to be mapped in the ChunkMapperModel

    ====================== =======================
    Input Annotation types Output Annotation type
    ====================== =======================
    ``CHUNK``              ``LABEL_DEPENDENCY``
    ====================== =======================

    Parameters
    ----------
    dictionary
        Dictionary path where is the json that contains the mappinmgs columns
    rel
        Relation that we going to use to map the chunk
    lowerCase
        Parameter to decide if we going to use the chunk mapper or not

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
    >>> chunkerMapperapproach = ChunkMapperModel()\
    ...    .pretrained()\
    ...    .setInputCols(["ner_chunk"])\
    ...    .setOutputCol("mappings")\
    ...    .setRels(["action"]) \
    >>> sampleData = "The patient was given Warfarina Lusa and amlodipine 10 MG."
    >>> pipeline = Pipeline().setStages([
    ...     documenter,
    ...     sentence_detector,
    ...     tokenizer,
    ...     embeddings,
    ...     ner_model,
    ...     ner_converter])
    >>> results = pipeline.fit(data).transform(data)
    >>> results = results \
    ...     .selectExpr("explode(drug_chunk_embeddings) AS drug_chunk") \
    ...     .selectExpr("drug_chunk.result", "slice(drug_chunk.embeddings, 1, 5) AS drug_embedding") \
    ...     .cache()
    >>> results.show(truncate=False)
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|mappings                                                                                                                                                                                                                                                                                                                                                                                               |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|[{labeled_dependency, 22, 35, Analgesic, {chunk -> 0, relation -> action, confidence -> 0.56995, all_relations -> Antipyretic, entity -> Warfarina Lusa, sentence -> 0}, []}, {labeled_dependency, 41, 50, NONE, {entity -> amlodipine, sentence -> 0, chunk -> 1, confidence -> 0.9989}, []}, {labeled_dependency, 55, 56, NONE, {entity -> MG, sentence -> 0, chunk -> 2, confidence -> 0.9123}, []}]|
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
"""
    name = "ChunkMapperModel"



    rel = Param(Params._dummy(),
                "rel",
                "Relation for the model",
                typeConverter=TypeConverters.toString)

    lowerCase = Param(Params._dummy(),
                      "lowerCase",
                      "Set if we want to save the dictionary in lower case or not",
                      typeConverter=TypeConverters.toBoolean)

    allowMultiTokenChunk = Param(Params._dummy(),
                                 "allowMultiTokenChunk",
                                 "Whether  if we skyp relations with multitokens",
                                 typeConverter=TypeConverters.toBoolean)

    multivaluesRelations = Param(Params._dummy(),
                                 "multivaluesRelations",
                                 "Whether  if we skyp relations with multitokens",
                                 typeConverter=TypeConverters.toBoolean)

    rels = Param(Params._dummy(),
                 "rels",
                 "Relations to be mappen in the dictionary",
                 typeConverter=TypeConverters.toListString)


    def setRel(self, r):
        return self._set(rel=r)

    def setRels(self, rs):
        return self._set(rels=rs)

    def setLowerCase(self,lc):
        """Set if we want to save the keys of the dictionary in lower case or not
        Parameters
        ----------
        lc : bool
            Parameter that select if you want to use the keys in lower case or not
        """
        return self._set(lowerCase=lc)

    def setAllowMultiTokenChunk(self,mc):
        """Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        Parameters
        ----------
        mc : bool
            "Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        """
        return self._set(allowMultiTokenChunk=mc)

    def setMultivaluesRelations(self,mc):
        """Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        Parameters
        ----------
         mc : bool
             "Whether  to decide if we want to send multi-chunk tokens or only single token chunks
        """
        return self._set(multivaluesRelations=mc)


    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkMapperModel", java_model=None):
        super(ChunkMapperModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name="", lang="en", remote_loc="clinical/models"):
        """Downloads and loads a pretrained model.

        Parameters
        ----------
        name : str, optional
            Name of the pretrained model.
        lang : str, optional
            Language of the pretrained model, by default "en"
        remote_loc : str, optional
            Optional remote address of the resource, by default None. Will use
            Spark NLPs repositories otherwise.

        Returns
        -------
        ChunkMapperModel
            The restored model
        """
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(ChunkMapperModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')