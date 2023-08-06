from sparknlp_jsl.annotator.resolution.sentence_entity_resolver import SentenceEntityResolverModel as M
from sparknlp_jsl.annotator.resolution.sentence_entity_resolver import SentenceEntityResolverApproach as A
from sparknlp.common import *


class SentenceEntityResolverApproach(A, ):
    """Thius class contains all the parameters and methods to train a SentenceEntityResolverModel.
       The model transforms a dataset with Input Annotation type SENTENCE_EMBEDDINGS, coming from e.g.
       [BertSentenceEmbeddings](/docs/en/transformers#bertsentenceembeddings)
       and returns the normalized entity for a particular trained ontology / curated dataset.
       (e.g. ICD-10, RxNorm, SNOMED etc.)

       ========================================= ======================
       Input Annotation types                    Output Annotation type
       ========================================= ======================
       ``SENTENCE_EMBEDDINGS``                    ``ENTITY``
       ========================================= ======================

       Parameters
       ----------
       labelCol
            Column name for the value we are trying to resolve
       normalizedCol
            Column name for the original, normalized description
       pretrainedModelPath
            Path to an already trained SentenceEntityResolverModel, which is used as a starting point for training the new model.
       overrideExistingCodes
            Whether to override the existing codes with new data while continue the training from a pretrained model. Default value is false(keep all the codes).
       returnCosineDistances
            Extract Cosine Distances. TRUE or False
       aux_label_col
            Auxiliary label which maps resolved entities to additional labels
       useAuxLabel
            Use AuxLabel Col or not
       overrideExistingCodes
            Whether to override the codes present in a pretrained model with new codes when the training process begins with a pretrained model
       dropCodesList
            A list of codes in a pretrained model that will be omitted when the training process begins with a pretrained model


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
       >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
       >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
       >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
       >>> bertEmbeddings = BertSentenceEmbeddings.pretrained("sent_biobert_pubmed_base_cased") \\
       ...  .setInputCols(["sentence"]) \\
       ...  .setOutputCol("embeddings")
       >>> snomedTrainingPipeline = Pipeline(stages=[
       ...  documentAssembler,
       ...  sentenceDetector,
       ...  bertEmbeddings,
       ... ])
       >>> snomedTrainingModel = snomedTrainingPipeline.fit(data)
       >>> snomedData = snomedTrainingModel.transform(data).cache()
       >>> assertionModel = assertionPipeline.fit(data)
       >>> assertionModel = assertionPipeline.fit(data)

       >>> bertExtractor = SentenceEntityResolverApproach() \\
       ...   .setNeighbours(25) \\
       ...   .setThreshold(1000) \\
       ...   .setInputCols(["bert_embeddings"]) \\
       ...   .setNormalizedCol("normalized_text") \\
       ...   .setLabelCol("label") \\
       ...   .setOutputCol("snomed_code") \\
       ...   .setDistanceFunction("EUCLIDIAN") \\
       ...   .setCaseSensitive(False)

       >>> snomedModel = bertExtractor.fit(snomedData)
       """

    @keyword_only
    def __init__(self):
        super(SentenceEntityResolverApproach, self).__init__(
            classname="com.johnsnowlabs.extensions.finance.chunk_classification.resolution.SentenceEntityResolverApproach")
        self._setDefault(labelCol="code", normalizedCol="code", distanceFunction="EUCLIDEAN", neighbours=500,
                         threshold=5, missAsEmpty=True, returnCosineDistances=True)


class SentenceEntityResolverModel(
    # sparknlp_jsl.annotator.resolution.sentence_entity_resolver.SentenceEntityResolverModel,
    M,
):
    """Thius class contains all the parameters and methods to train a SentenceEntityResolverModel.
       The model transforms a dataset with Input Annotation type SENTENCE_EMBEDDINGS, coming from e.g.
       [BertSentenceEmbeddings](/docs/en/transformers#bertsentenceembeddings)
       and returns the normalized entity for a particular trained ontology / curated dataset.
       (e.g. ICD-10, RxNorm, SNOMED etc.)

       ========================================= ======================
       Input Annotation types                    Output Annotation type
       ========================================= ======================
       ``SENTENCE_EMBEDDINGS``                   ``ENTITY``
       ========================================= ======================

       Parameters
       ----------
       returnCosineDistances
            Extract Cosine Distances. TRUE or False
       aux_label_col
            Auxiliary label which maps resolved entities to additional labels
       useAuxLabel
            Use AuxLabel Col or not

       searchTree
            Search tree for resolution

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
       >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
       >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
       >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
       >>> bertEmbeddings = BertSentenceEmbeddings.pretrained("sent_biobert_pubmed_base_cased") \\
       ...  .setInputCols(["sentence"]) \\
       ...  .setOutputCol("embeddings")
       >>> snomedTrainingPipeline = Pipeline(stages=[
       ...  documentAssembler,
       ...  sentenceDetector,
       ...  bertEmbeddings,
       ... ])
       >>> snomedTrainingModel = snomedTrainingPipeline.fit(data)
       >>> snomedData = snomedTrainingModel.transform(data).cache()
       >>> assertionModel = assertionPipeline.fit(data)
       >>> assertionModel = assertionPipeline.fit(data)

       >>> bertExtractor = SentenceEntityResolverApproach() \\
       ...   .setNeighbours(25) \\
       ...   .setThreshold(1000) \\
       ...   .setInputCols(["bert_embeddings"]) \\
       ...   .setNormalizedCol("normalized_text") \\
       ...   .setLabelCol("label") \\
       ...   .setOutputCol("snomed_code") \\
       ...   .setDistanceFunction("EUCLIDIAN") \\
       ...   .setCaseSensitive(False)

       >>> snomedModel = bertExtractor.fit(snomedData)
       """
    name = "SentenceEntityResolverModel"
    returnCosineDistances = Param(Params._dummy(), "returnCosineDistances",
                                  "Extract Cosine Distances. TRUE or False",
                                  typeConverter=TypeConverters.toBoolean)
    aux_label_col = Param(Params._dummy(), "aux_label_col",
                          "Auxiliary label which maps resolved entities to additional labels",
                          typeConverter=TypeConverters.toString)

    useAuxLabel = Param(Params._dummy(), "useAuxLabel",
                        "Use AuxLabel Col or not",
                        typeConverter=TypeConverters.toBoolean)
    searchTree = Param(Params._dummy(), "searchTree", "Search tree for resolution", TypeConverters.identity)

    def __init__(self,
                 classname="com.johnsnowlabs.extensions.finance.chunk_classification.resolution.SentenceEntityResolverModel",
                 java_model=None):
        super(SentenceEntityResolverModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(SentenceEntityResolverModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')
