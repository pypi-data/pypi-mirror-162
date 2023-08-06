from sparknlp.common import *
from sparknlp_jsl.annotator.generic_classifier.generic_classifier import GenericClassifierApproach


class RelationExtractionApproach(GenericClassifierApproach):
    """
    Trains a TensorFlow model for relation extraction. The Tensorflow graph in ``.pb`` format needs to be specified with
    ``setModelFile``. The result is a RelationExtractionModel.
    To start training, see the parameters that need to be set in the Parameters section.



    ===========================================  ======================
    Input Annotation types                       Output Annotation type
    ===========================================  ======================
    ``WORD_EMBEDDINGS, POS, CHUNK, DEPENDENCY``  ``CATEGORY``
    ===========================================  ======================

    Parameters
    ----------
    fromEntityBeginCol
        From Entity Begining Column
    fromEntityEndCol
        From Entity End Column
    fromEntityLabelCol
        From Entity Label Column
    toEntityBeginCol
        To Entity Begining Column
    toEntityEndCol
        To Entity End Column
    toEntityLabelCol
        "To Entity Label Column

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
    >>> documentAssembler = DocumentAssembler() \
    ...   .setInputCol("text") \
    ...   .setOutputCol("document")
    ...
    >>> tokenizer = Tokenizer() \
    ...   .setInputCols(["document"]) \
    ...   .setOutputCol("tokens")
    ...
    >>> embedder = WordEmbeddingsModel \
    ...   .pretrained("embeddings_clinical", "en", "clinical/models") \
    ...   .setInputCols(["document", "tokens"]) \
    ...   .setOutputCol("embeddings")
    ...
    >>> posTagger = PerceptronModel \
    ...   .pretrained("pos_clinical", "en", "clinical/models") \
    ...   .setInputCols(["document", "tokens"]) \
    ...   .setOutputCol("posTags")
    ...
    >>> nerTagger = MedicalNerModel \
    ...   .pretrained("ner_events_clinical", "en", "clinical/models") \
    ...   .setInputCols(["document", "tokens", "embeddings"]) \
    ...   .setOutputCol("ner_tags")
    ...
    >>> nerConverter = NerConverter() \
    ...   .setInputCols(["document", "tokens", "ner_tags"]) \
    ...   .setOutputCol("nerChunks")
    ...
    >>> depencyParser = DependencyParserModel \
    ...   .pretrained("dependency_conllu", "en") \
    ...   .setInputCols(["document", "posTags", "tokens"]) \
    ...   .setOutputCol("dependencies")
    ...
    >>> re = RelationExtractionApproach() \
    ...   .setInputCols(["embeddings", "posTags", "train_ner_chunks", "dependencies"]) \
    ...   .setOutputCol("relations_t") \
    ...   .setLabelColumn("target_rel") \
    ...   .setEpochsNumber(300) \
    ...   .setBatchSize(200) \
    ...   .setLearningRate(0.001) \
    ...   .setModelFile("path/to/graph_file.pb") \
    ...   .setFixImbalance(True) \
    ...   .setValidationSplit(0.05) \
    ...   .setFromEntity("from_begin", "from_end", "from_label") \
    ...   .setToEntity("to_begin", "to_end", "to_label")
    ...
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     tokenizer,
    ...     embedder,
    ...     posTagger,
    ...     nerTagger,
    ...     nerConverter,
    ...     depencyParser,
    ...     re])

    >>> model = pipeline.fit(trainData)

    """

    name = "RelationExtractionApproach"

    fromEntityBeginCol = Param(Params._dummy(), "fromEntityBeginCol", "From Entity Begining Column",
                               TypeConverters.toString)
    fromEntityEndCol = Param(Params._dummy(), "fromEntityEndCol", "From Entity End Column", TypeConverters.toString)
    fromEntityLabelCol = Param(Params._dummy(), "fromEntityLabelCol", "From Entity Label Column",
                               TypeConverters.toString)

    toEntityBeginCol = Param(Params._dummy(), "toEntityBeginCol", "To Entity Begining Column", TypeConverters.toString)
    toEntityEndCol = Param(Params._dummy(), "toEntityEndCol", "To Entity End Column", TypeConverters.toString)
    toEntityLabelCol = Param(Params._dummy(), "toEntityLabelCol", "To Entity Label Column", TypeConverters.toString)

    customLabels = Param(Params._dummy(), "customLabels",
                         "Custom relation labels",
                         TypeConverters.identity)

    def setFromEntity(self, begin_col, end_col, label_col):
        """Sets from entity

        Parameters
        ----------
        begin_col : str
             Column that has a reference of where the chunk begins
        end_col: str
             Column that has a reference of where the chunk end
        label_col: str
             Column that has a reference what are the type of chunk
        """
        self._set(fromEntityBeginCol=begin_col)
        self._set(fromEntityEndCol=end_col)
        return self._set(fromEntityLabelCol=label_col)


    def setToEntity(self, begin_col, end_col, label_col):
        """Sets to entity

        Parameters
        ----------
        begin_col : str
             Column that has a reference of where the chunk begins
        end_col: str
             Column that has a reference of where the chunk end
        label_col: str
             Column that has a reference what are the type of chunk
        """
        self._set(toEntityBeginCol=begin_col)
        self._set(toEntityEndCol=end_col)
        return self._set(toEntityLabelCol=label_col)

    def setCustomLabels(self, labels):
        """Sets custom relation labels

        Parameters
        ----------
        labels : dict[str, str]
            Dictionary which maps old to new labels
        """
        labels = labels.copy()
        from sparknlp_jsl.internal import CustomLabels
        return self._set(customLabels=CustomLabels(labels))

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.RelationExtractionApproach"):
        super(RelationExtractionApproach, self).__init__(classname=classname)


class RelationExtractionModel(AnnotatorModel):
    """
    Trains a TensorFlow model for relation extraction. The Tensorflow graph in ``.pb`` format needs to be specified with
    ``setModelFile``. The result is a RelationExtractionModel.
    To start training, see the parameters that need to be set in the Parameters section.

    ===========================================  ======================
    Input Annotation types                       Output Annotation type
    ===========================================  ======================
    ``WORD_EMBEDDINGS, POS, CHUNK, DEPENDENCY``  ``CATEGORY``
    ===========================================  ======================

    Parameters
    ----------
    predictionThreshold
        Minimal activation of the target unit to encode a new relation instance
    relationPairs
        List of dash-separated pairs of named entities ("ENTITY1-ENTITY2", e.g. "Biomarker-RelativeDay"), which will be processed
    relationPairsCaseSensitive
        Determines whether relation pairs are case sensitive
    maxSyntacticDistance
        Maximal syntactic distance, as threshold (Default: 0)

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
    ...   .setInputCol("text") \\
    ...   .setOutputCol("document")
    ...
    >>> tokenizer = Tokenizer() \\
    ...   .setInputCols(["document"]) \\
    ...   .setOutputCol("tokens")
    ...
    >>> embedder = WordEmbeddingsModel \
    ...   .pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens"]) \\
    ...   .setOutputCol("embeddings")
    ...
    >>> posTagger = PerceptronModel \\
    ...   .pretrained("pos_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens"]) \\
    ...   .setOutputCol("posTags")
    ...
    >>> nerTagger = MedicalNerModel \\
    ...   .pretrained("ner_events_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens", "embeddings"]) \\
    ...   .setOutputCol("ner_tags")
    ...
    >>> nerConverter = NerConverter() \\
    ...   .setInputCols(["document", "tokens", "ner_tags"]) \\
    ...   .setOutputCol("nerChunks")
    ...
    >>> depencyParser = DependencyParserModel \\
    ...   .pretrained("dependency_conllu", "en") \\
    ...   .setInputCols(["document", "posTags", "tokens"]) \\
    ...   .setOutputCol("dependencies")
    ...
    >>> relationPairs = [
    ...   "direction-external_body_part_or_region",
    ...   "external_body_part_or_region-direction",
    ...   "direction-internal_organ_or_component",
    ...   "internal_organ_or_component-direction"
    ... ]
    ...
    >>> re_model = RelationExtractionModel.pretrained("re_bodypart_directions", "en", "clinical/models") \\
    ...     .setInputCols(["embeddings", "pos_tags", "ner_chunks", "dependencies"]) \\
    ...     .setOutputCol("relations") \\
    ...     .setRelationPairs(relationPairs) \\
    ...     .setMaxSyntacticDistance(4) \\
    ...     .setPredictionThreshold(0.9)
    ...
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     tokenizer,
    ...     embedder,
    ...     posTagger,
    ...     nerTagger,
    ...     nerConverter,
    ...     depencyParser,
    ...     re_model])

    >>> model = pipeline.fit(trainData)
    >>> data = spark.createDataFrame([["MRI demonstrated infarction in the upper brain stem , left cerebellum and  right basil ganglia"]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    ...
    >>> result.selectExpr("explode(relations) as relations")
    ...  .select(
    ...    "relations.metadata.chunk1",
    ...    "relations.metadata.entity1",
    ...    "relations.metadata.chunk2",
    ...    "relations.metadata.entity2",
    ...    "relations.result"
    ...  )
    ...  .where("result != 0")
    ...  .show(truncate=False)
    ...
    ... # Show results
    ... result.selectExpr("explode(relations) as relations") \\
    ...   .select(
    ...      "relations.metadata.chunk1",
    ...      "relations.metadata.entity1",
    ...      "relations.metadata.chunk2",
    ...      "relations.metadata.entity2",
    ...      "relations.result"
    ...   ).where("result != 0") \
    ...   .show(truncate=False)
    +------+---------+-------------+---------------------------+------+
    |chunk1|entity1  |chunk2       |entity2                    |result|
    +------+---------+-------------+---------------------------+------+
    |upper |Direction|brain stem   |Internal_organ_or_component|1     |
    |left  |Direction|cerebellum   |Internal_organ_or_component|1     |
    |right |Direction|basil ganglia|Internal_organ_or_component|1     |
    +------+---------+-------------+---------------------------+------+

    """
    name = "RelationExtractionModel"

    predictionThreshold = Param(Params._dummy(), "predictionThreshold",
                                "Minimal activation of the target unit to encode a new relation instance",
                                TypeConverters.toFloat)

    relationPairs = Param(Params._dummy(), "relationPairs",
                          "List of dash-separated pairs of named entities  which will be processed",
                          TypeConverters.toString)

    relationPairsCaseSensitive = Param(Params._dummy(), "relationPairsCaseSensitive", "Determines whether relation pairs are case sensitive",
                                       TypeConverters.toBoolean)

    maxSyntacticDistance = Param(Params._dummy(), "maxSyntacticDistance",
                                 "Maximal syntactic distance, as threshold (Default: 0)",
                                 TypeConverters.toInt)

    classes = Param(Params._dummy(), "classes", "Categorization classes", TypeConverters.toListString)


    def setMaxSyntacticDistance(self, distance):
        """Sets maximal syntactic distance, as threshold (Default: 0)

        Parameters
        ----------
        b : int
            Maximal syntactic distance, as threshold (Default: 0)

        """
        return self._set(maxSyntacticDistance=distance)

    def setPredictionThreshold(self, threshold):
        """Sets Minimal activation of the target unit to encode a new relation instance

        Parameters
        ----------
        threshold : float
            Minimal activation of the target unit to encode a new relation instance

        """
        return self._set(predictionThreshold=threshold)

    def setRelationPairs(self, pairs):
        """Sets List of dash-separated pairs of named entities ("ENTITY1-ENTITY2", e.g. "Biomarker-RelativeDay"), which will be processed

        Parameters
        ----------
        pairs : str
            List of dash-separated pairs of named entities ("ENTITY1-ENTITY2", e.g. "Biomarker-RelativeDay"), which will be processed
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

    def setCustomLabels(self, labels):
        """Sets custom relation labels

        Parameters
        ----------
        labels : dict[str, str]
            Dictionary which maps old to new labels
        """
        self._call_java("setCustomLabels",labels)

    def getClasses(self):
        """
        Returns labels used to train this model
        """
        return self._call_java("getClasses")

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.RelationExtractionModel",
                 java_model=None):
        super(RelationExtractionModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            relationPairsCaseSensitive=False,
            maxSyntacticDistance=0,
            predictionThreshold=0.5,
            relationPairs=""
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        if name == "posology_re":
            return PosologyREModel()
        else:
            return ResourceDownloader.downloadModel(RelationExtractionModel, name, lang, remote_loc,
                                                    j_dwn='InternalsPythonResourceDownloader')

class PosologyREModel(RelationExtractionModel):
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.PosologyREModel",
                 java_model=None):
        super(RelationExtractionModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
