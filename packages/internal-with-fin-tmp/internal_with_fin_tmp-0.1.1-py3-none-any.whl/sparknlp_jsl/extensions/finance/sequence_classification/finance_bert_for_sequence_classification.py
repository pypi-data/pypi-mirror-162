from sparknlp.common import *
from sparknlp_jsl.annotator.classification.medical_bert_for_sequence_classification import MedicalBertForSequenceClassification as M

class FinanceBertForSequenceClassification(M):
    """
    FinanceBertForTokenClassification  can load Bert Models with sequence classification/regression head on top
    (a linear layer on top of the pooled output) e.g. for multi-class document classification tasks.

    Pretrained models can be loaded with :meth:`.pretrained` of the companion
    object:

    For available pretrained models please see the `Models Hub
    <https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition>`__.

    Models from the HuggingFace 🤗 Transformers library are also compatible with
    Spark NLP 🚀. To see which models are compatible and how to import them see
    `Import Transformers into Spark NLP 🚀
    <https://github.com/JohnSnowLabs/spark-nlp/discussions/5669>`_.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``DOCUMENT, TOKEN``    ``CATEGORY``
    ====================== ======================

    Parameters
    ----------
    batchSize
        Batch size. Large values allows faster processing but requires more
        memory, by default 8
    caseSensitive
        Whether to ignore case in tokens for embeddings matching, by default
        True
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    maxSentenceLength
        Max sentence length to process, by default 128

    Examples
    --------
    >>> import sparknlp
    >>> from sparknlp.base import *
    >>> from sparknlp.annotator import *
    >>> from pyspark.ml import Pipeline
    >>> documentAssembler = DocumentAssembler() \\
    ...     .setInputCol("text") \\
    ...     .setOutputCol("document")
    >>> tokenizer = Tokenizer() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("token")
    >>> tokenClassifier = FinanceBertForSequenceClassification.pretrained() \\
    ...     .setInputCols(["token", "document"]) \\
    ...     .setOutputCol("label") \\
    ...     .setCaseSensitive(True)
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     tokenizer,
    ...     tokenClassifier
    ... ])
    >>> data = spark.createDataFrame([["I felt a bit drowsy and had blurred vision after taking Aspirin."]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    >>> result.select("label.result").show(truncate=False)
    """
    name = "FinanceBertForSequenceClassification"

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.extensions.finance.sequence_classification.FinanceBertForSequenceClassification",
                 java_model=None):
        super(FinanceBertForSequenceClassification, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            batchSize=8,
            maxSentenceLength=128,
            caseSensitive=True
        )

    @staticmethod
    def loadSavedModel(folder, spark_session):
        """Loads a locally saved model
        Parameters
        ----------
        folder : str
            Folder of the saved model
        spark_session : pyspark.sql.SparkSession
            The current SparkSession

        Returns
        -------
        MedicalBertForSequenceClassification
            The restored model
        """
        from sparknlp_jsl.internal import _MedicalBertForSequenceClassificationLoader
        jModel = _MedicalBertForSequenceClassificationLoader(folder, spark_session._jsparkSession)._java_obj
        return FinanceBertForSequenceClassification(java_model=jModel)

    # TODO!!!
    @staticmethod
    def loadSavedModelOpenSource(bertForTokenClassifierPath, tfModelPath, spark_session):
        """Loads a locally saved model.

        Parameters
        ----------
        bertForTokenClassifierPath : str
            Folder of the bertForTokenClassifier
        tfModelPath : str
            Folder taht contains the tf model
        spark_session : pyspark.sql.SparkSession
            The current SparkSession
        Returns
        -------
        MedicalBertForSequenceClassification
            The restored model
        """
        from sparknlp_jsl.internal import _MedicalBertForSequenceClassificationLoaderOpensource
        jModel = _MedicalBertForSequenceClassificationLoaderOpensource(bertForTokenClassifierPath, tfModelPath,
                                                                       spark_session._jsparkSession)._java_obj
        return FinanceBertForSequenceClassification(java_model=jModel)

    @staticmethod
    def pretrained(name="bert_sequence_classifier_ade", lang="en", remote_loc="clinical/models"):
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
        FinanceBertForSequenceClassification
            The restored model
        """
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(FinanceBertForSequenceClassification, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')