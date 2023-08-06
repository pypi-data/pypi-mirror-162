from sparknlp.common import *

class RENerChunksFilter(AnnotatorModel):
    """Filters and outputs combinations of relations between extracted entities, for further processing.
    This annotator is especially useful to create inputs for the RelationExtractionDLModel.

    ==============================  ======================
    Input Annotation types          Output Annotation type
    ==============================  ======================
    ``CHUNK,DEPENDENCY``            ``CHUNK``
    ==============================  ======================

    Parameters
    ----------
    relationPairs
        List of valid relations to encode
    relationPairsCaseSensitive
        Determines whether relation pairs are case sensitive
    maxSyntacticDistance
        Maximum syntactic distance between a pair of named entities to consider them as a relation
    docLevelRelations
        Include relations between entities from different sentences (Default: False)

    Examples
    --------

    >>> documenter = DocumentAssembler()\\
    ...   .setInputCol("text")\\
    ...   .setOutputCol("document")
    ...
    >>> sentencer = SentenceDetector()\\
    ...   .setInputCols(["document"])\\
    ...   .setOutputCol("sentences")
    ...
    >>> tokenizer = Tokenizer()\\
    ...   .setInputCols(["sentences"])\\
    ...   .setOutputCol("tokens")
    ...
    >>> words_embedder = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\\
    ...   .setInputCols(["sentences", "tokens"])\\
    ...   .setOutputCol("embeddings")
    ...
    >>> pos_tagger = PerceptronModel.pretrained("pos_clinical", "en", "clinical/models")\\
    ...   .setInputCols(["sentences", "tokens"])\\
    ...   .setOutputCol("pos_tags")
    ...
    >>> dependency_parser = DependencyParserModel.pretrained("dependency_conllu", "en")\\
    ...   .setInputCols(["sentences", "pos_tags", "tokens"])\\
    ...   .setOutputCol("dependencies")
    ...
    >>> clinical_ner_tagger = MedicalNerModel.pretrained("jsl_ner_wip_greedy_clinical","en","clinical/models")\\
    ...   .setInputCols(["sentences", "tokens", "embeddings"])\\
    ...   .setOutputCol("ner_tags")
    ...
    >>> ner_chunker = NerConverter()\\
    ...   .setInputCols(["sentences", "tokens", "ner_tags"])\\
    ...   .setOutputCol("ner_chunks")
    ...
    ... # Define the relation pairs and the filter
    >>> relationPairs = [
    ...   "direction-external_body_part_or_region",
    ...   "external_body_part_or_region-direction",
    ...   "direction-internal_organ_or_component",
    ...   "internal_organ_or_component-direction"
    ... ]
    ...
    >>> re_ner_chunk_filter = RENerChunksFilter()\\
    ...   .setInputCols(["ner_chunks", "dependencies"])\\
    ...   .setOutputCol("re_ner_chunks")\\
    ...   .setMaxSyntacticDistance(4)\\
    ...   .setRelationPairs(["internal_organ_or_component-direction"])
    ...
    >>> trained_pipeline = Pipeline(stages=[
    ...   documenter,
    ...   sentencer,
    ...   tokenizer,
    ...   words_embedder,
    ...   pos_tagger,
    ...   clinical_ner_tagger,
    ...   ner_chunker,
    ...   dependency_parser,
    ...   re_ner_chunk_filter
    ... ])
    ...
    >>> data = spark.cre>>>DataFrame([["MRI demonstrated infarction in the upper brain stem , left cerebellum and  right basil ganglia"]]).toDF("text")
    >>> result = trained_pipeline.fit(data).transform(data)
    ...
    ... # Show results
    >>> result.selectExpr("explode(re_ner_chunks) as re_chunks") \
    ...   .selectExpr("re_chunks.begin", "re_chunks.result", "re_chunks.metadata.entity", "re_chunks.metadata.paired_to") \
    ...   .show(6, truncate=False)
    +-----+-------------+---------------------------+---------+
    |begin|result       |entity                     |paired_to|
    +-----+-------------+---------------------------+---------+
    |35   |upper        |Direction                  |41       |
    |41   |brain stem   |Internal_organ_or_component|35       |
    |35   |upper        |Direction                  |59       |
    |59   |cerebellum   |Internal_organ_or_component|35       |
    |35   |upper        |Direction                  |81       |
    |81   |basil ganglia|Internal_organ_or_component|35       |
    +-----+-------------+---------------------------+---------+
    +---------------------------------------------------------+


    """
    name = "RENerChunksFilter"

    relationPairs = Param(Params._dummy(), "relationPairs", "List of dash-separated pairs of named entitiese",
                          TypeConverters.toString)

    relationPairsCaseSensitive = Param(Params._dummy(), "relationPairsCaseSensitive", "Determines whether relation pairs are case sensitive",
                                       TypeConverters.toBoolean)

    maxSyntacticDistance = Param(Params._dummy(), "maxSyntacticDistance",
                                 "Maximum syntactic distance between a pair of named entities to consider them as a relation",
                                 TypeConverters.toInt)

    docLevelRelations = Param(Params._dummy(), "docLevelRelations",
                              "Include relations between entities from different sentences (Default: False)",
                              TypeConverters.toBoolean)

    def setMaxSyntacticDistance(self, distance):
        """Sets maximum syntactic distance between a pair of named entities to consider them as a relation"

        Parameters
        ----------
        distance : int
           Maximum syntactic distance between a pair of named entities to consider them as a relation
        """
        return self._set(maxSyntacticDistance=distance)

    def setDocLevelRelations(self, docLevelRelations):
        """Sets whether to include relations between entities from different sentences

        Parameters
        ----------
        docLevelRelations : bool
            Whether to include relations between entities from different sentences
        """
        return self._set(docLevelRelations=docLevelRelations)

    def setRelationPairs(self, pairs):
        """Sets list of dash-separated pairs of named entities

        Parameters
        ----------
        pairs : str
           List of dash-separated pairs of named entities
        """
        if type(pairs) is not list:
            pairs_str = pairs
        else:
            pairs_str = ",".join(pairs)
        return self._set(relationPairs=pairs_str)

    def setRelationPairsCaseSensitive(self, value):
        """Sets the case sensitivity of relation pairs
        Parameters
        ----------
        value : boolean
            whether relation pairs are case sensitive
        """
        return self._set(relationPairsCaseSensitive=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.RENerChunksFilter",
                 java_model=None):
        super(RENerChunksFilter, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            relationPairsCaseSensitive=False,
            maxSyntacticDistance=0,
            docLevelRelations=False,
            relationPairs=""
        )
