from sparknlp.common import *

class DocumentLogRegClassifierApproach(AnnotatorApproach):
    """Trains a model to classify documents with a Logarithmic Regression algorithm. Training data requires columns for
    text and their label. The result is a trained GenericClassifierModel.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``TOKEN``                       `         ``CATEGORY``
    ========================================= ======================

    Parameters
    ----------
    labelCol
        Column with the value result we are trying to predict.
    maxIter
        maximum number of iterations.
    tol
        convergence tolerance after each iteration.
    fitIntercept
        whether to fit an intercept term, default is true.
    labels
        array to output the label in the original form.
    vectorizationModelPath
        specify the vectorization model if it has been already trained.
    classificationModelPath
        specify the classification model if it has been already trained.

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

    An example pipeline could then be defined like this

    >>> tokenizer = Tokenizer() \\
    ...    .setInputCols("document") \\
    ...    .setOutputCol("token")
    ...
    >>> normalizer = Normalizer() \\
    ...    .setInputCols("token") \\
    ...    .setOutputCol("normalized")
    ...
    >>> stopwords_cleaner = StopWordsCleaner()\\
    ...    .setInputCols("normalized")\\
    ...    .setOutputCol("cleanTokens")\\
    ...    .setCaseSensitive(False)
    ...
    ...stemmer = Stemmer() \
    ...    .setInputCols("cleanTokens") \
    ...    .setOutputCol("stem")
    ...
    >>> gen_clf = DocumentLogRegClassifierApproach() \\
    ...    .setLabelColumn("category") \\
    ...    .setInputCols("stem") \\
    ...    .setOutputCol("prediction")
    ...
    >>> pipeline = Pipeline().setStages([
    ...    document_assembler,
    ...    tokenizer,
    ...    normalizer,
    ...    stopwords_cleaner,
    ...    stemmer,
    ...    logreg
    ...])
    ...
    >>> clf_model = pipeline.fit(data)
    """

    labelCol = Param(Params._dummy(), "labelCol", "column with the value result we are trying to predict.",
                     typeConverter=TypeConverters.toString)
    maxIter = Param(Params._dummy(), "maxIter", "maximum number of iterations.", TypeConverters.toInt)
    tol = Param(Params._dummy(), "tol", "convergence tolerance after each iteration.", TypeConverters.toFloat)
    fitIntercept = Param(Params._dummy(), "fitIntercept", "whether to fit an intercept term, default is true.",
                         typeConverter=TypeConverters.toBoolean)
    labels = Param(Params._dummy(), "labels", "array to output the label in the original form.",
                   typeConverter=TypeConverters.toListString)
    vectorizationModelPath = Param(Params._dummy(), "vectorizationModelPath",
                                   "specify the vectorization model if it has been already trained.",
                                   typeConverter=TypeConverters.toString)
    classificationModelPath = Param(Params._dummy(), "classificationModelPath",
                                    "specify the classification model if it has been already trained.",
                                    typeConverter=TypeConverters.toString)

    def setLabelColumn(self, label):
        """Sets column with the value result we are trying to predict.

        Parameters
        ----------
        label : str
            Column with the value result we are trying to predict.

        """
        return self._set(labelCol=label)

    def setMaxIter(self, k):
        """Sets maximum number of iterations.

        Parameters
        ----------
        k : int
             Maximum number of iterations.

        """
        return self._set(maxIter=k)

    def setTol(self, dist):
        """Sets  convergence tolerance after each iteration.

        Parameters
        ----------
        dist : float
            Convergence tolerance after each iteration.

        """
        return self._set(tol=dist)

    def setFitIntercept(self, merge):
        """Sets whether to fit an intercept term, default is true.

        Parameters
        ----------
        label : str
            Whether to fit an intercept term, default is true.

        """
        return self._set(fitIntercept=merge)

    def setVectorizationModelPath(self, value):
        """Sets a path to the the classification model if it has been already trained.

        Parameters
        ----------
        label : str
          Path to the the classification model if it has been already trained.

        """
        return self._set(vectorizationModelPath=value)

    def setClassificationModelPath(self, value):
        """Sets a path to the the classification model if it has been already trained.

        Parameters
        ----------
        label : str
            Path to the the classification model if it has been already trained.

        """
        return self._set(classificationModelPath=value)

    def setLabels(self, value):
        """Sets array to output the label in the original form.

        Parameters
        ----------
        label : list
           array to output the label in the original form.

        """
        return self._set(labels=value)

    def _create_model(self, java_model):
        return DocumentLogRegClassifierModel(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(DocumentLogRegClassifierApproach, self).__init__(
            classname="com.johnsnowlabs.nlp.annotators.classification.DocumentLogRegClassifierApproach")
        self._setDefault(
            labelCol="selector",
            maxIter=10,
            tol=1e-6,
            fitIntercept=True,
            vectorizationModelPath="",
            classificationModelPath="")


class DocumentLogRegClassifierModel(AnnotatorModel):
    """ Classifies documents with a Logarithmic Regression algorithm.


    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``TOKEN``                                 ``CATEGORY``
    ========================================= ======================

    Parameters
    ----------
    mergeChunks
        Whether to merge all chunks in a document or not (Default: false)
    labels
        Array to output the label in the original form.
    vectorizationModel
       Vectorization model if it has been already trained.
    classificationModel
        Classification model if it has been already trained.
    """
    name = "DocumentLogRegClassifierModel"

    vectorizationModel = Param(Params._dummy(), "vectorizationModel", "wrapped vectorization model.",
                               typeConverter=TypeConverters.identity)
    classificationModel = Param(Params._dummy(), "classificationModel", "wrapped classification model.",
                                typeConverter=TypeConverters.identity)
    labels = Param(Params._dummy(), "labels", "array to output the label in the original form.",
                   typeConverter=TypeConverters.toListString)
    mergeChunks = Param(Params._dummy(), "mergeChunks", "whether or not to combine all chunks and make a single query",
                        typeConverter=TypeConverters.toBoolean)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.classification.DocumentLogRegClassifierModel",
                 java_model=None):
        super(DocumentLogRegClassifierModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    def setLabels(self, value):
        """Sets array to output the label in the original form.

        Parameters
        ----------
        label : list
           array to output the label in the original form.

        """
        return self._set(labels=value)

    def setMergeChunks(self, merge):
        """Sets whether to merge all chunks in a document or not (Default: false)

        Parameters
        ----------
        merge : list
           whether to merge all chunks in a document or not (Default: false)
        """
        return self._set(mergeChunks=merge)

    def setVectorizationModel(self, model):
        """Sets a path to the classification model if it has been already trained.

        Parameters
        ----------
        model: :class:`pyspark.ml.PipelineModel`
            Classification model if it has been already trained.

        """
        return self._set(vectorizationModel=model)

    def setClassificationModel(self, model):
        """Sets a path to the the classification model if it has been already trained.

        Parameters
        ----------
        model: :class:`pyspark.ml.PipelineModel`
            Classification model if it has been already trained.

        """
        return self._set(classificationModel=model)

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(DocumentLogRegClassifierModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

