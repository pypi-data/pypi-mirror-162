from sparknlp.internal import ExtendedJavaWrapper


class _UpdateCacheModels(ExtendedJavaWrapper):
    def __init__(self, cache_folder=""):
        super(_UpdateCacheModels, self).__init__(
            "com.johnsnowlabs.util.UpdateModels.updateCacheModels", cache_folder)


class _UpdateModels(ExtendedJavaWrapper):
    def __init__(self, date_cutoff):
        super(_UpdateModels, self).__init__(
            "com.johnsnowlabs.util.UpdateModels.updateModels", date_cutoff)


class _HadoopOperations(ExtendedJavaWrapper):
    def __init__(self, local_file, hdfs_file):
        super(_HadoopOperations, self).__init__(
            "com.johnsnowlabs.util.HadoopOperations.moveFile", local_file, hdfs_file)


class _MedicalBertTokenClassifierLoader(ExtendedJavaWrapper):
    def __init__(self, path, jspark):
        super(_MedicalBertTokenClassifierLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalBertForTokenClassifier.loadSavedModel", path, jspark)


class _MedicalBertTokenClassifierLoaderOpensource(ExtendedJavaWrapper):
    def __init__(self, bertForTokenClassifierPath, tfModelPath, jspark):
        super(_MedicalBertTokenClassifierLoaderOpensource, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalBertForTokenClassifier.loadSavedModelOpenSource",
            bertForTokenClassifierPath, tfModelPath, jspark)


class _MedicalBertForSequenceClassificationLoader(ExtendedJavaWrapper):
    def __init__(self, path, jspark):
        super(_MedicalBertForSequenceClassificationLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalBertForSequenceClassification.loadSavedModel", path,
            jspark)


class _MedicalBertForSequenceClassificationLoaderOpensource(ExtendedJavaWrapper):
    def __init__(self, bertForSequenceClassifierPath, tfModelPath, jspark):
        super(_MedicalBertForSequenceClassificationLoaderOpensource, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalBertForSequenceClassification.loadSavedModelOpenSource",
            bertForSequenceClassifierPath, tfModelPath, jspark)


class _FinanceBertForSequenceClassificationLoaderOpensource(ExtendedJavaWrapper):
    def __init__(self, bertForSequenceClassifierPath, tfModelPath, jspark):
        super(_MedicalBertForSequenceClassificationLoaderOpensource, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalBertForSequenceClassification.loadSavedModelOpenSource",
            bertForSequenceClassifierPath, tfModelPath, jspark)





class _MedicalDistilBertForSequenceClassificationLoader(ExtendedJavaWrapper):
    def __init__(self, path, jspark):
        super(_MedicalDistilBertForSequenceClassificationLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalDistilBertForSequenceClassification.loadSavedModel",
            path, jspark)


class _MedicalDistilBertForSequenceClassificationLoaderOpensource(ExtendedJavaWrapper):
    def __init__(self, destilbertForSequenceClassifierPath, tfModelPath, jspark):
        super(_MedicalDistilBertForSequenceClassificationLoaderOpensource, self).__init__(
            "com.johnsnowlabs.nlp.annotators.classification.MedicalDistilBertForSequenceClassification.loadSavedModelOpenSource",
            destilbertForSequenceClassifierPath, tfModelPath, jspark)

class _BertSentenceEmbeddingsToBertSentenceChunkEmbeddingsLoader(ExtendedJavaWrapper):
    def __init__(self, path):
        super(_BertSentenceEmbeddingsToBertSentenceChunkEmbeddingsLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.embeddings.BertSentenceChunkEmbeddings.load", path)

class _ZeroShotRelationExtractionModelLoader(ExtendedJavaWrapper):
    def __init__(self, path, jspark):
        super(_ZeroShotRelationExtractionModelLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.re.ZeroShotRelationExtractionModel.loadSavedModel", path, jspark)

class _EntityWeights(ExtendedJavaWrapper):
    def __init__(self, weights):
        super(_EntityWeights, self).__init__("com.johnsnowlabs.nlp.param.EntityWeights.fromJava", weights)


class _TargetEntities(ExtendedJavaWrapper):
    def __init__(self, entities):
        super(_TargetEntities, self).__init__("com.johnsnowlabs.nlp.param.TargetEntities.fromJava", entities)


class _CustomLabels(ExtendedJavaWrapper):
    def __init__(self, labels):
        super(_CustomLabels, self).__init__("com.johnsnowlabs.nlp.param.CustomLabels.fromJava", labels)

class _RelationalCategories(ExtendedJavaWrapper):
    def __init__(self, categories):
        super(_RelationalCategories, self).__init__(
            "com.johnsnowlabs.nlp.param.RelationalCategories.fromJava", categories)


class _ShowUnCategorizedResources(ExtendedJavaWrapper):
    def __init__(self):
        super(_ShowUnCategorizedResources, self).__init__(
            "com.johnsnowlabs.nlp.pretrained.PythonResourceDownloader.showUnCategorizedResources")


class _ShowPrivatePipelines(ExtendedJavaWrapper):
    def __init__(self, lang, version):
        super(_ShowPrivatePipelines, self).__init__(
            "com.johnsnowlabs.nlp.pretrained.InternalsPythonResourceDownloader.showPrivatePipelines", lang, version)


class _ShowPrivateModels(ExtendedJavaWrapper):
    def __init__(self, annotator, lang, version):
        super(_ShowPrivateModels, self).__init__(
            "com.johnsnowlabs.nlp.pretrained.InternalsPythonResourceDownloader.showPrivateModels", annotator, lang, version)

class _ShowAvailableAnnotators(ExtendedJavaWrapper):
    def __init__(self):
        super(_ShowAvailableAnnotators, self).__init__(
            "com.johnsnowlabs.nlp.pretrained.InternalsPythonResourceDownloader.showAvailableAnnotators")



class _MedicalNerGraphBuilder(ExtendedJavaWrapper):
    def __init__(self, dataset, input_col, label_col):
        super(_MedicalNerGraphBuilder, self).__init__(
            "com.johnsnowlabs.nlp.annotators.ner.MedicalNerApproach.getGraphParams",
            dataset, input_col, label_col)

class _RelationExtractionGraphBuilder(ExtendedJavaWrapper):
    def __init__(self, dataset):
        super(_RelationExtractionGraphBuilder, self).__init__(
            "com.johnsnowlabs.nlp.annotators.re.RelationExtractionApproach.getGraphParams", dataset)


def EntityWeights(weights):
    return _EntityWeights(weights).apply()


def TargetEntities(entities):
    return _TargetEntities(entities).apply()


def CustomLabels(labels):
    return _CustomLabels(labels).apply()

def RelationalCategories(categories):
    return _RelationalCategories(categories).apply()


