from sparknlp.common import *
from sparknlp_jsl.annotator.classification.medical_bert_for_token_classifier import MedicalBertForTokenClassifier as M

class FinanceBertForTokenClassification(M):
    """
    FinanceBertForTokenClassifier can load Bert Models with a token
    classification head on top (a linear layer on top of the hidden-states
    output) e.g. for Named-Entity-Recognition (NER) tasks.

    Pretrained models can be loaded with :meth:`.pretrained` of the companion
    object:

    >>> embeddings = FinanceBertForTokenClassification.pretrained() \\
    ...     .setInputCols(["token", "document"]) \\
    ...     .setOutputCol("label")

    The default model is ``"bert_token_classifier_ner_bionlp"``, if no name is
    provided.

    For available pretrained models please see the `Models Hub
    <https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition>`__.

    Models from the HuggingFace 🤗 Transformers library are also compatible with
    Spark NLP 🚀. To see which models are compatible and how to import them see
    `Import Transformers into Spark NLP 🚀
    <https://github.com/JohnSnowLabs/spark-nlp/discussions/5669>`_.

    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``DOCUMENT, TOKEN``    ``NAMED_ENTITY``
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
    >>> tokenClassifier = FinanceBertForTokenClassifier.pretrained() \\
    ...     .setInputCols(["token", "document"]) \\
    ...     .setOutputCol("label") \\
    ...     .setCaseSensitive(True)
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     tokenizer,
    ...     tokenClassifier
    ... ])
    >>> data = spark.createDataFrame([["Both the erbA IRES and the erbA/myb virus constructs transformed erythroid cells after infection of bone marrow or blastoderm cultures."]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    >>> result.select("label.result").show(truncate=False)
    +------------------------------------------------------------------------------------+
    |result
    |
    +------------------------------------------------------------------------------------+
    |[O, O, B-Organism, I-Organism, O, O, B-Organism, I-Organism, O, O, B-Cell, I-Cell, O,
    O, O, B-Multi-tissue_structure, I-Multi-tissue_structure, O, B-Cell, I-Cell, O]|
    +------------------------------------------------------------------------------------+
    """
    name = "FinanceBertForTokenClassification"

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.extensions.finance.token_classification.ner.FinanceBertForTokenClassification",
                 java_model=None):
        super(FinanceBertForTokenClassification, self).__init__(
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
        """Loads a locally saved model.

        Parameters
        ----------
        folder : str
            Folder of the saved model
        spark_session : pyspark.sql.SparkSession
            The current SparkSession

        Returns
        -------
        MedicalBertForTokenClassifier
            The restored model
        """
        from sparknlp_jsl.internal import _MedicalBertTokenClassifierLoader
        jModel = _MedicalBertTokenClassifierLoader(folder, spark_session._jsparkSession)._java_obj
        return FinanceBertForTokenClassification(java_model=jModel)

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
        MedicalBertForTokenClassifier
            The restored model
        """
        from sparknlp_jsl.internal import _MedicalBertTokenClassifierLoaderOpensource
        jModel = _MedicalBertTokenClassifierLoaderOpensource(bertForTokenClassifierPath, tfModelPath,
                                                             spark_session._jsparkSession)._java_obj
        return FinanceBertForTokenClassification(java_model=jModel)

    @staticmethod
    def pretrained(name="bert_token_classifier_ner_bionlp", lang="en", remote_loc="clinical/models"):
        """Downloads and loads a pretrained model.

        Parameters
        ----------
        name : str, optional
            Name of the pretrained model, by default
            "bert_base_token_classifier_conll03"
            lang : str, optional
            Language of the pretrained model, by default "en"
            remote_loc : str, optional
            Optional remote address of the resource, by default None. Will use
            Spark NLPs repositories otherwise.

        Returns
        -------
        MedicalBertForTokenClassifier
            The restored model
        """
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(FinanceBertForTokenClassification, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')