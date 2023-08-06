from pyspark.ml import Model, Estimator
from pyspark.ml.util import DefaultParamsWritable, DefaultParamsReadable
from sparknlp.common import *
from pyspark.sql import functions as F

class MedicalGraphBuilderModel(Model, DefaultParamsWritable, DefaultParamsReadable):
    def _transform(self, dataset):
        return dataset

class TFGraphBuilder(Estimator, DefaultParamsWritable, DefaultParamsReadable):

    modelName = Param(Params._dummy(),
                      "modelName",
                      "Model name",
                      typeConverter=TypeConverters.toString)

    labelColumn = Param(Params._dummy(),
                        "labelColumn",
                        "Labels",
                        typeConverter=TypeConverters.toString)

    inputCols = Param(Params._dummy(),
                      "inputCols",
                      "Input columns",
                      typeConverter=TypeConverters.toListString)

    graphFolder = Param(Params._dummy(), "graphFolder", "Folder path that contain external graph files",
                        TypeConverters.toString)

    graphFile = Param(Params._dummy(), "graphFile", "Graph file name. If empty, default name is generated.",
                      TypeConverters.toString)

    hiddenUnitsNumber = Param(Params._dummy(),
                              "hiddenUnitsNumber",
                              "Number of hidden units, used in AssertionDLApproach and MedicalNerAprroach",
                              typeConverter=TypeConverters.toInt)
    hiddenLayers = Param(Params._dummy(),
                         "hiddenLayers",
                         "A list of hidden layer sizes, used in RelationExtractionApproach",
                         typeConverter=TypeConverters.toListInt)

    maxSequenceLength = Param(Params._dummy(),
                              "maxSequenceLength",
                              "Maximal sequence length, used in AssertionDLApproach",
                              typeConverter=TypeConverters.toInt)

    hiddenAct = Param(Params._dummy(),
                      "hiddenAct",
                      "Activation function for hidden layers, used in RelationExtractionApproach. Possible value are: relu, sigmoid, tanh, linear",
                      typeConverter=TypeConverters.toString)

    hiddenActL2 = Param(Params._dummy(),
                        "hiddenActL2",
                        "L2 regularization of hidden layer activations, used in RelationExtractionApproach.",
                        typeConverter=TypeConverters.toBoolean)

    hiddenWeightsL2 = Param(Params._dummy(),
                            "hiddenWeightsL2",
                            "L2 regularization of hidden layer weights, used in RelationExtractionApproach.",
                            typeConverter=TypeConverters.toBoolean)

    batchNorm = Param(Params._dummy(),
                      "batchNorm",
                      "Batch normalization, used in RelationExtractionApproach.",
                      typeConverter=TypeConverters.toBoolean)

    isMedical = Param(Params._dummy(),
                      "isMedical",
                      "Medical model, used in MedicalNerAprroach and NerDLApproach.",
                      typeConverter=TypeConverters.toBoolean)

    def setHiddenAct(self, value):
        """Activation function for hidden layers, used in RelationExtractionApproach.

        Parameters
        ----------
        value : string
            Activation function for hidden layers, used in RelationExtractionApproach.
            Possible value are: relu, sigmoid, tanh, linear
        """
        return self._set(hiddenAct=value)

    def getHiddenAct(self):
        """Activation function for hidden layers, used in RelationExtractionApproach."""

        return self.getOrDefault(self.hiddenAct)

    def setHiddenActL2(self, value):
        """L2 regularization of hidden layer weights, used in RelationExtractionApproach

        Parameters
        ----------
        value : boolean
            L2 regularization of hidden layer activations, used in RelationExtractionApproach
        """
        return self._set(hiddenActL2=value)

    def getHiddenActL2(self):
        """L2 regularization of hidden layer activations, used in RelationExtractionApproach"""

        return self.getOrDefault(self.hiddenActL2)

    def setHiddenWeightsL2(self, value):
        """L2 regularization of hidden layer weights, used in RelationExtractionApproach

        Parameters
        ----------
        value : boolean
            L2 regularization of hidden layer weights, used in RelationExtractionApproach
        """
        return self._set(hiddenWeightsL2=value)

    def getHiddenWeightsL2(self):
        """L2 regularization of hidden layer weights, used in RelationExtractionApproach"""

        return self.getOrDefault(self.hiddenWeightsL2)

    def setBatchNorm(self, value):
        """Batch normalization, used in RelationExtractionApproach.

        Parameters
        ----------
        value : boolean
            Batch normalization for RelationExtractionApproach
        """
        return self._set(batchNorm=value)

    def getBatchNorm(self):
        """Batch normalization, used in RelationExtractionApproach."""

        return self.getOrDefault(self.batchNorm)

    def setIsMedical(self, value):
        """Medical model, used in MedicalNerAprroach and NerDLApproach.
        Parameters
        ----------
        value : boolean
            Where medical model or not (default is True)
        """
        return self._set(isMedical=value)

    def getIsMedical(self):
        """Medical model, used in MedicalNerAprroach and NerDLApproach."""

        return self.getOrDefault(self.isMedical)

    def setHiddenLayers(self, value):
        """A list of hidden layer sizes for RelationExtractionApproach

        Parameters
        ----------
        *value : int
            A list of hidden layer sizes for RelationExtractionApproach
        """
        return self._set(hiddenLayers=value)

    def getHiddenLayers(self):
        """Gets the list of hiudden layer sizes for RelationExtractionApproach."""

        return self.getOrDefault(self.hiddenLayers)

    def setMaxSequenceLength(self, value):
        """Sets the maximum sequence length for AssertionDLApproach

        Parameters
        ----------
        value : int
            Maximum sequence length for AssertionDLApproach
        """
        return self._set(maxSequenceLength=value)

    def getMaxSequenceLength(self):
        """Gets the maximum sequence length for AssertionDLApproach."""

        return self.getOrDefault(self.maxSequenceLength)

    def setHiddenUnitsNumber(self, value):
        """Sets the number of hidden units for AssertionDLApproach and MedicalNerApproach

        Parameters
        ----------
        value : int
            Number of hidden units for AssertionDLApproach and MedicalNerApproach
        """
        return self._set(hiddenUnitsNumber=value)

    def getHiddenUnitsNumber(self):
        """Gets the number of hidden units for AssertionDLApproach and MedicalNerApproach."""
        return self.getOrDefault(self.hiddenUnitsNumber)

    def setModelName(self, value):
        """Sets the model name

        Parameters
        ----------
        value : str
            Model name
        """
        return self._set(modelName=value)

    def getModelName(self):
        """Gets the name of the model."""
        return self.getOrDefault(self.modelName)

    def setLabelColumn(self, value):
        """Sets the name of the column for data labels.

        Parameters
        ----------
        value : str
            Column for data labels
        """
        return self._set(labelColumn=value)

    def getLabelColumn(self):
        """Gets the name of the label column."""
        return self.getOrDefault(self.labelColumn)

    def setInputCols(self, *value):
        """Sets column names of input annotations.

        Parameters
        ----------
        *value : str
            Input columns for the annotator
        """
        if len(value) == 1 and type(value[0]) == list:
            return self._set(inputCols=value[0])
        else:
            return self._set(inputCols=list(value))

    def getInputCols(self):
        """Gets current column names of input annotations."""
        return self.getOrDefault(self.inputCols)

    def setGraphFolder(self, value):
        """Sets folder path that contain external graph files.

        Parameters
        ----------
        value : srt
            Folder path that contain external graph files.
        """
        return self._set(graphFolder=value)

    def getGraphFolder(self):
        """Gets the graph folder."""
        return self.getOrDefault(self.graphFolder)

    def setGraphFile(self, value):
        """Sets the graph file name.

        Parameters
        ----------
        value : srt
            Greaph file name. If set to "auto", then the graph builder will use the model specific default graph
            file name.
        """
        return self._set(graphFile=value)

    def getGraphFile(self):
        """Gets the graph file name."""
        return self.getOrDefault(self.graphFile)

    def _fit(self, dataset):
        from ..training import tf_graph, tf_graph_1x
        if self.getModelName() is not None:
            model_name = self.getModelName()
        else:
            raise Exception("No model name specified in MedicalGraphBuilder. Use setModelName to select a model.")
        model_names = tf_graph.get_models()
        build_params = {}
        if model_name == "ner_dl":
            from sparknlp_jsl.internal import _MedicalNerGraphBuilder

            params_java = _MedicalNerGraphBuilder(
                dataset,
                self.getInputCols(),
                self.getLabelColumn())._java_obj
            params = list(map(int, params_java.toString().replace("(", "").replace(")", "").split(",")))
            build_params["ntags"] = params[0]
            build_params["embeddings_dim"] = params[1]
            build_params["nchars"] = params[2]
            build_params["is_medical"] = self.getIsMedical() if (self.getIsMedical() is not None) else True
            if self.getHiddenUnitsNumber() is not None:
                build_params["lstm_size"] = self.getHiddenUnitsNumber()
        elif model_name == "assertion_dl":
            labels_count = len(dataset.select(self.getLabelColumn()).distinct().collect())
            embeddings_dim = None
            for f in dataset.schema.fields:
                if f.name in self.getInputCols():
                    if "annotatorType" in f.metadata:
                        if f.metadata["annotatorType"].lower() == "word_embeddings":
                            embeddings_dim = int(f.metadata["dimension"])
            if not embeddings_dim:
                raise("Can't infer embeddings dimension.")
            build_params["n_classes"] = labels_count
            build_params["feat_size"] = embeddings_dim
            build_params["max_seq_len"] = True
            if self.getHiddenUnitsNumber() is not None:
                build_params["n_hidden"] = self.getHiddenUnitsNumber()
            if self.getMaxSequenceLength() is not None:
                build_params["max_seq_len"] = self.getMaxSequenceLength()
        elif model_name == "relation_extraction":
            from sparknlp_jsl.internal import _RelationExtractionGraphBuilder

            labels_count = len(dataset.select(self.getLabelColumn()).distinct().collect())
            params_java = _RelationExtractionGraphBuilder(dataset)._java_obj
            feature_vector_dim = int(params_java)
            build_params["input_dim"] = feature_vector_dim
            build_params["output_dim"] = labels_count
            if self.getHiddenLayers() is not None:
                build_params["hidden_layers"] = self.getHiddenLayers()
            if self.getHiddenAct() is not None:
                build_params["hidden_act"] = self.getHiddenAct()
            if self.getHiddenActL2() is not None:
                build_params["hidden_act_l2"] = self.getHiddenActL2()
            if self.getHiddenWeightsL2() is not None:
                build_params["hidden_weights_l2"] = self.getHiddenWeightsL2()
            if self.getBatchNorm() is not None:
                build_params["batch_norm"] = self.getBatchNorm()
        elif model_name == "generic_classifier":
            feature_column = self.getInputCols()[0]
            try:
                feature_vector_annos = dataset \
                    .where(F.size(F.col(feature_column)) > 0) \
                    .select(feature_column) \
                    .take(1)[0][feature_column]
                build_params["input_dim"] = len(feature_vector_annos[0].embeddings)
            except Exception:
                raise("Can't infer the size of the Generic Clasasier input feature vector")
            labels_count = len(dataset.select(self.getLabelColumn()).distinct().collect())
            build_params["output_dim"] = labels_count
            if self.getHiddenLayers() is not None:
                build_params["hidden_layers"] = self.getHiddenLayers()
            if self.getHiddenAct() is not None:
                build_params["hidden_act"] = self.getHiddenAct()
            if self.getHiddenActL2() is not None:
                build_params["hidden_act_l2"] = self.getHiddenActL2()
            if self.getHiddenWeightsL2() is not None:
                build_params["hidden_weights_l2"] = self.getHiddenWeightsL2()
            if self.getBatchNorm() is not None:
                build_params["batch_norm"] = self.getBatchNorm()

        elif model_name == "":
            raise Exception("No model name specified.")
        else:
            models = ", ".join(model_names)
            raise Exception(f"Unsupported model. Support models are: {models}")

        graph_file = "auto"
        if self.getGraphFile() is not None:
            graph_file = self.getGraphFile()

        graph_folder = ""
        if self.getGraphFolder() is not None:
            graph_folder = self.getGraphFolder()

        print("Medical Graph Builder configuration:")
        print("Model name: {}".format(model_name))
        print("Graph folder: {}".format(graph_folder))
        print("Graph file name: {}".format(graph_file))
        print("Build params: ", end="")
        print(build_params)

        try:
            tf_graph.build(model_name, build_params=build_params, model_location=self.getGraphFolder(), model_filename=graph_file)
        except Exception:
            print("Can't build the tensorflow graph with TF 2 graph factory, attempting TF 1.15 factory")
            try:
                tf_graph_1x.build(model_name, build_params=build_params, model_location=self.getGraphFolder())
            except Exception:
                raise Exception("The tensorflow graphs can't be build.")

        return MedicalGraphBuilderModel()

    def __init__(self):
        super(TFGraphBuilder, self).__init__()
        self._setDefault(
            modelName=None,
            labelColumn=None,
            inputCols=None,
            graphFolder=None,
            graphFile=None,
            hiddenUnitsNumber=None,
            hiddenLayers=None,
            maxSequenceLength=None,
            hiddenAct=None,
            hiddenActL2=None,
            hiddenWeightsL2=None,
            batchNorm=None,
            isMedical=True
        )
