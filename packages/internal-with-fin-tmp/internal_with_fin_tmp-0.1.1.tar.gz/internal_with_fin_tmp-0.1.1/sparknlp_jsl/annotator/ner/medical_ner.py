import sys

from sparknlp.common import *
import sparknlp
from sparknlp.internal import ExtendedJavaWrapper


class MedicalNerApproach(AnnotatorApproach, sparknlp.annotators.NerApproach):
    """This Named Entity recognition annotator allows to train generic NER model
    based on Neural Networks.

    The architecture of the neural network is a Char CNNs - BiLSTM - CRF that
    achieves state-of-the-art in most datasets.

    For instantiated/pretrained models, see :class:`.NerDLModel`.

    The training data should be a labeled Spark Dataset, in the format of
    :class:`.CoNLL` 2003 IOB with `Annotation` type columns. The data should
    have columns of type ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` and an additional
    label column of annotator type ``NAMED_ENTITY``.

    Excluding the label, this can be done with for example:

    - a SentenceDetector,
    - a Tokenizer and
    - a WordEmbeddingsModel (any embeddings can be chosen, e.g. BertEmbeddings
      for BERT based embeddings).

    For extended examples of usage, see the `Spark NLP Workshop <https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/training/english/dl-ner>`__.

    ==================================== ======================
    Input Annotation types               Output Annotation type
    ==================================== ======================
    ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` ``NAMED_ENTITY``
    ==================================== ======================

    Parameters
    ----------
    labelColumn
        Column with label per each token
    entities
        Entities to recognize
    minEpochs
        Minimum number of epochs to train, by default 0
    maxEpochs
        Maximum number of epochs to train, by default 50
    verbose
        Level of verbosity during training, by default 2
    randomSeed
        Random seed
    lr
        Learning Rate, by default 0.001
    po
        Learning rate decay coefficient. Real Learning Rage = lr / (1 + po *
        epoch), by default 0.005
    batchSize
        Batch size, by default 8
    dropout
        Dropout coefficient, by default 0.5
    graphFolder
        Folder path that contain external graph files
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    useContrib
        whether to use contrib LSTM Cells. Not compatible with Windows. Might
        slightly improve accuracy
    validationSplit
        Choose the proportion of training dataset to be validated against the
        model on each Epoch. The value should be between 0.0 and 1.0 and by
        default it is 0.0 and off, by default 0.0
    evaluationLogExtended
        Whether logs for validation to be extended, by default False.
    testDataset
        Path to test dataset. If set used to calculate statistic on it during
        training.
    includeConfidence
        whether to include confidence scores in annotation metadata, by default
        False
    includeAllConfidenceScores
        whether to include all confidence scores in annotation metadata or just
        the score of the predicted tag, by default False
    enableOutputLogs
        Whether to use stdout in addition to Spark logs, by default False
    outputLogsPath
        Folder path to save training logs
    enableMemoryOptimizer
        Whether to optimize for large datasets or not. Enabling this option can
        slow down training, by default False

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

    First extract the prerequisites for the NerDLApproach

    >>> documentAssembler = DocumentAssembler() \\
    ...     .setInputCol("text") \\
    ...     .setOutputCol("document")
    >>> sentence = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...     .setInputCols(["sentence"]) \\
    ...     .setOutputCol("token")
    >>> embeddings = BertEmbeddings.pretrained() \\
    ...     .setInputCols(["sentence", "token"]) \\
    ...     .setOutputCol("embeddings")

    Then the training can start

    >>> nerTagger = MedicalNerApproach() \\
    ...     .setInputCols(["sentence", "token", "embeddings"]) \\
    ...     .setLabelColumn("label") \\
    ...     .setOutputCol("ner") \\
    ...     .setMaxEpochs(1) \\
    ...     .setRandomSeed(0) \\
    ...     .setVerbose(0)
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     sentence,
    ...     tokenizer,
    ...     embeddings,
    ...     nerTagger
    ... ])
    >>> conll = CoNLL()
    >>> trainingData = conll.readDataset(spark, "src/test/resources/conll2003/eng.train")
    >>> pipelineModel = pipeline.fit(trainingData)
    """

    lr = Param(Params._dummy(), "lr", "Learning Rate", TypeConverters.toFloat)

    po = Param(Params._dummy(), "po", "Learning rate decay coefficient. Real Learning Rage = lr / (1 + po * epoch)",
               TypeConverters.toFloat)

    batchSize = Param(Params._dummy(), "batchSize", "Batch size", TypeConverters.toInt)

    dropout = Param(Params._dummy(), "dropout", "Dropout coefficient", TypeConverters.toFloat)

    graphFolder = Param(Params._dummy(), "graphFolder", "Folder path that contains external graph files",
                        TypeConverters.toString)

    graphFile = Param(Params._dummy(), "graphFile",
                      "Path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.",
                      TypeConverters.toString)

    configProtoBytes = Param(Params._dummy(), "configProtoBytes",
                             "ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()",
                             TypeConverters.toListString)

    useContrib = Param(Params._dummy(), "useContrib",
                       "whether to use contrib LSTM Cells. Not compatible with Windows. Might slightly improve accuracy.",
                       TypeConverters.toBoolean)

    validationSplit = Param(Params._dummy(), "validationSplit",
                            "Choose the proportion of training dataset to be validated against the model on each Epoch. The value should be between 0.0 and 1.0 and by default it is 0.0 and off.",
                            TypeConverters.toFloat)

    evaluationLogExtended = Param(Params._dummy(), "evaluationLogExtended",
                                  "Choose the proportion of training dataset to be validated against the model on each Epoch. The value should be between 0.0 and 1.0 and by default it is 0.0 and off.",
                                  TypeConverters.toBoolean)

    testDataset = Param(Params._dummy(), "testDataset",
                        "Path to test dataset. If set used to calculate statistic on it during training.",
                        TypeConverters.identity)

    includeConfidence = Param(Params._dummy(), "includeConfidence",
                              "whether to include confidence scores in annotation metadata",
                              TypeConverters.toBoolean)

    includeAllConfidenceScores = Param(Params._dummy(), "includeAllConfidenceScores",
                                       "whether to include all confidence scores in annotation metadata or just the score of the predicted tag",
                                       TypeConverters.toBoolean)

    enableOutputLogs = Param(Params._dummy(), "enableOutputLogs",
                             "Whether to use stdout in addition to Spark logs.",
                             TypeConverters.toBoolean)

    outputLogsPath = Param(Params._dummy(), "outputLogsPath", "Folder path to save training logs",
                           TypeConverters.toString)

    logPrefix = Param(Params._dummy(), "logPrefix",
                      "A prefix that will be appended to every log, default value is empty.", TypeConverters.toString)

    enableMemoryOptimizer = Param(Params._dummy(), "enableMemoryOptimizer",
                                  "Whether to optimize for large datasets or not. Enabling this option can slow down training.",
                                  TypeConverters.toBoolean)

    useBestModel = Param(Params._dummy(), "useBestModel",
                         "Whether to restore and use the model from the epoch that has achieved the best performance at the end of the training.",
                         TypeConverters.toBoolean)

    pretrainedModelPath = Param(Params._dummy(), "pretrainedModelPath",
                                "Path to an already trained MedicalNerModel, which is used as a starting point for training the new model.",
                                TypeConverters.toString)

    overrideExistingTags = Param(Params._dummy(), "overrideExistingTags",
                                 "Whether to override already learned tags when using a pretrained model to initialize the new model. Default is 'true'.",
                                 TypeConverters.toBoolean)

    tagsMapping = Param(Params._dummy(), "tagsMapping",
                        "A map specifying how old tags are mapped to new ones. It only works if setOverrideExistingTags "
                        + "is false. The mapping is specified as a list of comma separared strings, "
                          "e.g. [\"B-PER, B-VIP\", \"I-PER, I-VIP\",...]", TypeConverters.toListString)

    earlyStoppingCriterion = Param(Params._dummy(), "earlyStoppingCriterion",
                                   "If set, this param specifies the criterion to stop training if performance is not improving. "
                                   "Default value is 0 which is means that early stopping is not used.",
                                   TypeConverters.toFloat)

    earlyStoppingPatience = Param(Params._dummy(), "earlyStoppingPatience",
                                  "Number of epochs with no performance improvement before training is terminated. "
                                  "Default value is 0.", TypeConverters.toInt)

    def setConfigProtoBytes(self, b):
        """Sets configProto from tensorflow, serialized into byte array.

        Parameters
        ----------
        b : List[str]
            ConfigProto from tensorflow, serialized into byte array
        """
        return self._set(configProtoBytes=b)

    def setGraphFolder(self, p):
        """Sets folder path that contain external graph files.

        Parameters
        ----------
        p : str
            Folder path that contain external graph files
        """
        return self._set(graphFolder=p)

    def setGraphFile(self, ff):
        """Sets path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.

        Parameters
        ----------
        p : str
            Path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.
        """
        return self._set(graphFile=ff)

    def setUseContrib(self, v):
        """Sets whether to use contrib LSTM Cells. Not compatible with Windows.
        Might slightly improve accuracy.

        Parameters
        ----------
        v : bool
            Whether to use contrib LSTM Cells

        Raises
        ------
        Exception
            Windows not supported to use contrib
        """
        if v and sys.version == 'win32':
            raise Exception("Windows not supported to use contrib")
        return self._set(useContrib=v)

    def setLr(self, v):
        """Sets Learning Rate, by default 0.001.

        Parameters
        ----------
        v : float
            Learning Rate
        """
        self._set(lr=v)
        return self

    def setPo(self, v):
        """Sets Learning rate decay coefficient, by default 0.005.

        Real Learning Rage is lr / (1 + po * epoch).

        Parameters
        ----------
        v : float
            Learning rate decay coefficient
        """
        self._set(po=v)
        return self

    def setBatchSize(self, v):
        """Sets batch size, by default 64.

        Parameters
        ----------
        v : int
            Batch size
        """
        self._set(batchSize=v)
        return self

    def setDropout(self, v):
        """Sets dropout coefficient, by default 0.5.

        Parameters
        ----------
        v : float
            Dropout coefficient
        """
        self._set(dropout=v)
        return self

    def _create_model(self, java_model):
        return MedicalNerModel(java_model=java_model)

    def setValidationSplit(self, v):
        """Sets the proportion of training dataset to be validated against the
        model on each Epoch, by default it is 0.0 and off. The value should be
        between 0.0 and 1.0.

        Parameters
        ----------
        v : float
            Proportion of training dataset to be validated
        """
        self._set(validationSplit=v)
        return self

    def setEvaluationLogExtended(self, v):
        """Sets whether logs for validation to be extended, by default False.
        Displays time and evaluation of each label.

        Parameters
        ----------
        v : bool
            Whether logs for validation to be extended

        """
        self._set(evaluationLogExtended=v)
        return self

    def setTestDataset(self, path, read_as=ReadAs.SPARK, options=None):
        """Sets Path to test dataset. If set used to calculate statistic on it
        during training.

        Parameters
        ----------
        path : str
            Path to test dataset
        read_as : str, optional
            How to read the resource, by default ReadAs.SPARK
        options : dict, optional
            Options for reading the resource, by default {"format": "parquet"}
        """
        if options is None:
            options = {"format": "parquet"}
        return self._set(testDataset=ExternalResource(path, read_as, options))

    def setIncludeConfidence(self, value):
        """Sets whether to include confidence scores in annotation metadata, by
        default False.

        Parameters
        ----------
        value : bool
            Whether to include the confidence value in the output.
        """
        return self._set(includeConfidence=value)

    def setIncludeAllConfidenceScores(self, value):
        """Sets whether to include all confidence scores in annotation metadata
        or just the score of the predicted tag, by default False.

        Parameters
        ----------
        value : bool
            Whether to include all confidence scores in annotation metadata or
            just the score of the predicted tag
        """
        return self._set(includeAllConfidenceScores=value)

    def setEnableOutputLogs(self, value):
        """Sets whether to use stdout in addition to Spark logs, by default
        False.

        Parameters
        ----------
        value : bool
            Whether to use stdout in addition to Spark logs
        """
        return self._set(enableOutputLogs=value)

    def setEnableMemoryOptimizer(self, value):
        """Sets Whether to optimize for large datasets or not, by default False.
        Enabling this option can slow down training.

        Parameters
        ----------
        value : bool
            Whether to optimize for large datasets
        """
        return self._set(enableMemoryOptimizer=value)

    def setUseBestModel(self, value):
        """Sets whether to restore and use the model that has achieved the best performance at the end of the training..
        The metric that is being monitored is macro F1 for the following cases(highest precendence first),


        Parameters
        ----------
        value : bool
            Whether to return the model that has achieved the best metrics across epochs.
        """
        return self._set(useBestModel=value)

    def setOutputLogsPath(self, p):
        """Sets folder path to save training logs.

        Parameters
        ----------
        p : str
            Folder path to save training logs
        """
        return self._set(outputLogsPath=p)

    def setLogPrefix(self, s):
        """Sets folder path to save training logs.

        Parameters
        ----------
        p : str
            Folder path to save training logs
        """
        return self._set(logPrefix=s)

    def setPretrainedModelPath(self, value):
        """Sets folder path to save training logs.

        Parameters
        ----------
        value : str
           Path to an already trained MedicalNerModel, which is used as a starting point for training the new model.
        """
        return self._set(pretrainedModelPath=value)

    def setOverrideExistingTags(self, value):
        """Sets whether to override already learned tags when using a pretrained model to initialize the new model. Default is 'true'

        Parameters
        ----------
        value : bool
            Whether to override already learned tags when using a pretrained model to initialize the new model. Default is 'true'
        """
        return self._set(overrideExistingTags=value)

    def setTagsMapping(self, value):
        """Sets a map specifying how old tags are mapped to new ones. It only works if setOverrideExistingTags

        Parameters
        ----------
        value : list
            A map specifying how old tags are mapped to new ones. It only works if setOverrideExistingTags
        """
        return self._set(tagsMapping=value)

    def setEarlyStoppingCriterion(self, criterion):
        """Sets early stopping criterion. A value 0 means no early stopping.

        Parameters
        ----------
        criterion : float
            Early stopping criterion.
        """

        return self._set(earlyStoppingCriterion=criterion)

    def setEarlyStoppingPatience(self, patience):
        """Sets the number of epochs with no performance improvement before training is terminated.

        Parameters
        ----------
        patience : int
            Early stopping patience.
        """

        return self._set(earlyStoppingPatience=patience)

    @keyword_only
    def __init__(self):
        super(MedicalNerApproach, self).__init__(classname="com.johnsnowlabs.nlp.annotators.ner.MedicalNerApproach")
        uc = False if sys.platform == 'win32' else True
        self._setDefault(
            minEpochs=0,
            maxEpochs=50,
            lr=float(0.001),
            po=float(0.005),
            batchSize=8,
            dropout=float(0.5),
            verbose=2,
            useContrib=uc,
            validationSplit=float(0.0),
            evaluationLogExtended=False,
            includeConfidence=False,
            includeAllConfidenceScores=False,
            enableOutputLogs=False,
            enableMemoryOptimizer=False,
            pretrainedModelPath="",
            overrideExistingTags=True,
            earlyStoppingCriterion=0.0,
            earlyStoppingPatience=0
        )


class _MedicalNerModelLoader(ExtendedJavaWrapper):
    def __init__(self, ner_model_path, path, jspark):
        super(_MedicalNerModelLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.ner.MedicalNerModel.loadSavedModel", ner_model_path, path, jspark)


class MedicalNerModel(AnnotatorModel, HasStorageRef, HasBatchedAnnotate):
    """This Named Entity recognition annotator is a generic NER model based on
    Neural Networks.

    Neural Network architecture is Char CNNs - BiLSTM - CRF that achieves
    state-of-the-art in most datasets.

    This is the instantiated model of the :class:`.NerDLApproach`. For training
    your own model, please see the documentation of that class.

    Pretrained models can be loaded with :meth:`.pretrained` of the companion
    object:

    >>> nerModel = MedicalNerDLModel.pretrained() \\
    ...     .setInputCols(["sentence", "token", "embeddings"]) \\
    ...     .setOutputCol("ner")


    The default model is ``"ner_dl"``, if no name is provided.

    For available pretrained models please see the `Models Hub
    <https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition>`__.
    Additionally, pretrained pipelines are available for this module, see
    `Pipelines <https://nlp.johnsnowlabs.com/docs/en/pipelines>`__.

    Note that some pretrained models require specific types of embeddings,
    depending on which they were trained on. For example, the default model
    ``"ner_dl"`` requires the WordEmbeddings ``"glove_100d"``.

    For extended examples of usage, see the `Spark NLP Workshop
    <https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Public/3.SparkNLP_Pretrained_Models.ipynb>`__.

    ==================================== ======================
    Input Annotation types               Output Annotation type
    ==================================== ======================
    ``DOCUMENT, TOKEN, WORD_EMBEDDINGS`` ``NAMED_ENTITY``
    ==================================== ======================

    Parameters
    ----------
    batchSize
        Size of every batch, by default 8
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    includeConfidence
        Whether to include confidence scores in annotation metadata, by default
        False
    includeAllConfidenceScores
        Whether to include all confidence scores in annotation metadata or just
        the score of the predicted tag, by default False
    inferenceBatchSize
        Number of sentences to process in a single batch during inference
    classes
        Tags used to trained this NerDLModel
    labelCasing:
        Setting all labels of the NER models upper/lower case. values upper|lower

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
    ...     .setInputCol("text") \\
    ...     .setOutputCol("document")
    >>> sentence = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...     .setInputCols(["sentence"]) \\
    ...     .setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained() \\
    ...     .setInputCols(["sentence", "token"]) \\
    ...     .setOutputCol("bert")
    >>> nerTagger = MedicalNerDLModel.pretrained() \\
    ...     .setInputCols(["sentence", "token", "bert"]) \\
    ...     .setOutputCol("ner")
    >>> pipeline = Pipeline().setStages([
    ...     documentAssembler,
    ...     sentence,
    ...     tokenizer,
    ...     embeddings,
    ...     nerTagger
    ... ])
    >>> data = spark.createDataFrame([["U.N. official Ekeus heads for Baghdad."]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    """
    name = "MedicalNerModel"

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.ner.MedicalNerModel", java_model=None):
        super(MedicalNerModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            includeConfidence=False,
            includeAllConfidenceScores=False,
            batchSize=8,
            inferenceBatchSize=1
        )

    configProtoBytes = Param(Params._dummy(), "configProtoBytes",
                             "ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()",
                             TypeConverters.toListString)
    includeConfidence = Param(Params._dummy(), "includeConfidence",
                              "whether to include confidence scores in annotation metadata",
                              TypeConverters.toBoolean)
    includeAllConfidenceScores = Param(Params._dummy(), "includeAllConfidenceScores",
                                       "whether to include all confidence scores in annotation metadata or just the score of the predicted tag",
                                       TypeConverters.toBoolean)
    inferenceBatchSize = Param(Params._dummy(), "inferenceBatchSize",
                               "number of sentences to process in a single batch during inference",
                               TypeConverters.toInt)
    classes = Param(Params._dummy(), "classes",
                    "get the tags used to trained this MedicalNerModel",
                    TypeConverters.toListString)

    trainingClassDistribution = Param(Params._dummy(),
                                      "trainingClassDistribution",
                                      "class counts for each of the classes during training",
                                      typeConverter=TypeConverters.identity)

    labelCasing = Param(Params._dummy(), "labelCasing",
                        "Setting all labels of the NER models upper/lower case. values upper|lower",
                        TypeConverters.toString)

    def setConfigProtoBytes(self, b):
        """Sets configProto from tensorflow, serialized into byte array.

        Parameters
        ----------
        b : List[str]
            ConfigProto from tensorflow, serialized into byte array
        """
        return self._set(configProtoBytes=b)

    def setIncludeConfidence(self, value):
        """Sets whether to include confidence scores in annotation metadata, by
        default False.

        Parameters
        ----------
        value : bool
            Whether to include the confidence value in the output.
        """
        return self._set(includeConfidence=value)

    def setIncludeConfidence(self, value):
        """Sets whether to include confidence scores in annotation metadata, by
        default False.

        Parameters
        ----------
        value : bool
            Whether to include the confidence value in the output.
        """
        return self._set(includeConfidence=value)

    def setInferenceBatchSize(self, value):
        """Sets number of sentences to process in a single batch during inference

        Parameters
        ----------
        value : int
           number of sentences to process in a single batch during inference
        """
        return self._set(inferenceBatchSize=value)

    def setLabelCasing(self, value):
        """Setting all labels of the NER models upper/lower case. values upper|lower

        Parameters
        ----------
        value : str
           Setting all labels of the NER models upper/lower case. values upper|lower
        """
        return self._set(labelCasing=value)

    def getTrainingClassDistribution(self):
        return self._call_java('getTrainingClassDistributionJava')

    @staticmethod
    def pretrained(name="ner_dl", lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        return ResourceDownloader.downloadModel(MedicalNerModel, name, lang, remote_loc)

    @staticmethod
    def loadSavedModel(ner_model_path, folder, spark_session):
        jModel = _MedicalNerModelLoader(ner_model_path, folder, spark_session._jsparkSession)._java_obj
        return MedicalNerModel(java_model=jModel)

    @staticmethod
    def pretrained(name="ner_clinical", lang="en", remote_loc="clinical/models"):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(MedicalNerModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')
