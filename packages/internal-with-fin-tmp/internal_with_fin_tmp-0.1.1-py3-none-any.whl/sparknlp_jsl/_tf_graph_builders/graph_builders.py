import os
import re

from sparknlp_jsl.internal import _HadoopOperations


class WrongTFVersion(Exception):
    pass


class TensorflowAddonsNeeded(Exception):
    pass


class TFGraphBuilder:
    """
    Generic class to create the tensorflow graphs for 'ner_dl', 'generic_classifier', 'assertion_dl', 'relation_extraction' annotators in spark-nlp healthcare. In version 1.1
    Examples
    --------
    >>> from sparknlp_jsl.training import tf_graph
    >>>
    >>> tf_graph.get_models()

    """

    def supports_auto_file_name(self):
        return False

    def get_model_filename(self):
        raise Exception("Not implemented.")

    def check_build_params(self):

        build_params = self.get_build_params()
        required_params = self.get_model_build_params()

        for req_param in required_params:
            if req_param not in build_params:
                if required_params[req_param] is None:
                    raise Exception(f"You need to specify a value for {req_param} in the build parameters.")

    def get_build_params(self):
        return self.__build_params

    def get_build_params_with_defaults(self):
        build_params = self.get_build_params()
        req_build_params = self.get_model_build_params()

        for req_param in req_build_params:
            if (req_param not in build_params) and (req_build_params[req_param] is not None):
                build_params[req_param] = req_build_params[req_param]

        return build_params

    def get_build_param(self, build_param):
        build_params = self.get_build_params()

        if build_param in build_params:
            return build_params[build_param]

        required_params = self.get_model_build_params()

        if (build_param in required_params) and (required_params[build_param] is not None):
            return required_params[build_param]

        raise Exception(f"No value for {build_param} found.")

    def get_model_build_params(self):
        return {}

    def get_model_build_param_explanations(self):
        return {}

    def __init__(self, build_params):
        self.__build_params = build_params


class GenericClassifierTFGraphBuilder(TFGraphBuilder):
    """
    Class to create the the TF graphs for GenericClassifierApproach

    Examples
    --------
    >>> from sparknlp_jsl.training import tf_graph
    >>> from sparknlp_jsl.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> dataframe = pd.read_csv('petfinder-mini.csv')
    >>> DL_params = {"input_dim": 302,"output_dim": 2,"hidden_layers": [300, 200, 100], "hidden_act": "tanh",'hidden_act_l2':1,'batch_norm':1}
    >>> tf_graph.build("generic_classifier",build_params=DL_params, model_location="/content/gc_graph", model_filename="auto")
    >>> gen_clf = GenericClassifierApproach() \\
    ...    .setLabelColumn("target") \\
    ...    .setInputCols(["features"]) \\
    ...    .setOutputCol("prediction") \\
    ...    .setModelFile('/content/gc_graph/gcl.302.2.pb') \\
    ...    .setEpochsNumber(50) \\
    ...    .setBatchSize(100) \\
    ...    .setFeatureScaling("zscore") \\
    ...    .setFixImbalance(True) \\
    ...    .setLearningRate(0.001) \\
    ...    .setOutputLogsPath("logs") \\
    ...    .setValidationSplit(0.2)

    >>> clf_Pipeline = Pipeline(stages=[features_asm,gen_clf])
    """

    def supports_auto_file_name(self):
        return True

    def get_model_filename(self):
        return "gcl.{}.{}.pb".format(
            self.get_build_param("input_dim"),
            self.get_build_param("output_dim"),
        )

    def get_model_build_params(self):
        return {
            "hidden_layers": [200],
            "input_dim": None,
            "output_dim": None,
            "hidden_act": "relu",
            "hidden_act_l2": 0,
            "hidden_weights_l2": 0,
            "batch_norm": False,
        }

    def get_model_build_param_explanations(self):
        return {
            "hidden_layers": "List of integers indicating the size of each hidden layer. For example: [100, 200, 300].",
            "input_dim": "Input dimension.",
            "output_dim": "Output dimension.",
            "hidden_act": "Activation function of hidden layers: relu, sigmoid, tanh or linear.",
            "hidden_act_l2": "L2 regularization of hidden layer activations. Boolean (0 or 1).",
            "hidden_weights_l2": "L2 regularization of hidden layer weights. Boolean (0 or 1).",
            "batch_norm": "Batch normalization. Boolean (0 or 1)."
        }

    def build(self, model_location, model_filename):
        from .generic_classifier.generic_classifier_model import GenericClassifierModel

        model = GenericClassifierModel()

        model.build(self.get_build_params_with_defaults())
        if (re.match(r'(\w+)://.*', model_location)):
            tmp_location = "/tmp/generic_classifier_model"
            model.export_graph(model_location=tmp_location, model_filename=model_filename)

            file_location = os.path.join(tmp_location, model_filename)
            _HadoopOperations(file_location, model_location).apply()

        else:
            model.export_graph(model_location=model_location, model_filename=model_filename)


class AssertionTFGraphBuilder(TFGraphBuilder):
    """
    Class to build the the TF graphs for AssertionDLApproach

    Examples
    --------
    >>> from sparknlp_jsl.training import tf_graph
    >>> from sparknlp_jsl.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>>feat_size = 200
    >>>n_classes = 6
    >>> tf_graph.build("assertion_dl",build_params={"n_classes": n_classes}, model_location= "./tf_graphs", model_filename="blstm_34_32_30_{}_{}.pb".format(feat_size, n_classes))
    >>> assertion = AssertionDLApproach() \\
    >>>               .setLabelCol("label") \\
    >>>               .setInputCols("document", "chunk", "embeddings") \\
    >>>               .setOutputCol("assertion") \\
    >>>               .setBatchSize(128) \\
    >>>               .setDropout(0.1) \\
    >>>               .setLearningRate(0.001) \\
    >>>               .setEpochs(50) \\
    >>>               .setValidationSplit(0.2) \\
    >>>               .setStartCol("start") \\
    >>>               .setEndCol("end") \\
    >>>               .setMaxSentLen(250) \\
    >>>               .setEnableOutputLogs(True) \\
    >>>               .setOutputLogsPath('training_logs/') \\
    >>>               .setGraphFolder('tf_graphs')
    """

    def supports_auto_file_name(self):
        return True

    def get_model_filename(self):
        return "blstm_{}_32_30_{}_{}.pb".format(
            self.get_build_param("n_hidden"),
            self.get_build_param("feat_size"),
            self.get_build_param("n_classes")
        )

    def get_model_build_params(self):
        return {
            "max_seq_len": 250,
            "feat_size": 200,
            "n_classes": None,
            "device": "/cpu:0",
            "n_hidden": 34,
        }

    def get_model_build_param_explanations(self):
        return {
            "max_seq_len": "Maximum sequence length.",
            "feat_size": "Feature size.",
            "n_classes": "Number of classes.",
            "device": "Device for training.",
            "n_hidden": "Number of hidden units.",
        }

    def build(self, model_location, model_filename):
        from sparknlp_jsl._tf_graph_builders.assertion_dl.assertion_model import AssertionModel

        model = AssertionModel(
            seq_max_len=self.get_build_param("max_seq_len"),
            feat_size=self.get_build_param("feat_size") + 10,
            n_classes=self.get_build_param("n_classes"),
            device=self.get_build_param("device"))

        # Network Parameters
        model.add_bidirectional_lstm(self.get_build_param("n_hidden"))
        model.add_optimizer()
        if (re.match(r'(\w+)://.*', model_location)):
            tmp_location = "/tmp/assertionModel"
            model.persist_graph(model_location=tmp_location, model_filename=model_filename)

            file_location = os.path.join(tmp_location, model_filename)
            _HadoopOperations(file_location, model_location).apply()

        else:
            model.persist_graph(model_location=model_location, model_filename=model_filename)


class NerTFGraphBuilder(TFGraphBuilder):
    """
    Class to build the the TF graphs for MedicalNerApproach.

    Examples
    --------

    >>> from sparknlp_jsl.training import tf_graph
    >>> from sparknlp_jsl.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>>feat_size = 200
    >>>n_classes = 6
    >>> tf_graph.build("ner_dl", build_params={"embeddings_dim": 200, "nchars": 83,"ntags": 12,"is_medical": 1},model_location="./medical_ner_graphs",model_filename="auto")
    >>> nerTagger = MedicalNerApproach()\
    >>>                     .setInputCols(["sentence", "token", "embeddings"])\
    >>>                     .setLabelColumn("label")\
    >>>                     .setOutputCol("ner")\
    >>>                     .setMaxEpochs(2)\
    >>>                     .setBatchSize(64)\
    >>>                     .setRandomSeed(0)\
    >>>                     .setVerbose(1)\
    >>>                     .setValidationSplit(0.2)\
    >>>                     .setEvaluationLogExtended(True) \
    >>>                     .setEnableOutputLogs(True)\
    >>>                     .setIncludeConfidence(True)\
    >>>                     .setOutputLogsPath('ner_logs')\
    >>>                     .setGraphFolder('medical_ner_graphs')\
    >>>                     .setEnableMemoryOptimizer(True)
    """

    def supports_auto_file_name(self):
        return True

    def get_model_filename(self):
        return "blstm_{}_{}_{}_{}.pb".format(
            self.get_build_param("ntags"),
            self.get_build_param("embeddings_dim"),
            self.get_build_param("lstm_size"),
            self.get_build_param("nchars"),
        )

    def get_model_build_params(self):
        return {
            "ntags": None,
            "embeddings_dim": 200,
            "nchars": 100,
            "lstm_size": 128,
            "gpu_device": 0,
            "is_medical": False
        }

    def get_model_build_param_explanations(self):
        return {
            "ntags": "Number of tags.",
            "embeddings_dim": "Embeddings dimension.",
            "nchars": "Number of chars.",
            "gpu_device": "Device for training.",
            "lstm_size": "Number of LSTM units.",
            "is_medical": "Build a Medical Ner graph.",
        }

    def build(self, model_location, model_filename):
        from sparknlp_jsl._tf_graph_builders.ner_dl.create_graph import create_graph
        if (re.match(r'(\w+)://.*', model_location)):
            tmp_location = "/tmp/nerModel"
            create_graph(
                model_location=tmp_location,
                model_filename=model_filename,
                ntags=self.get_build_param("ntags"),
                embeddings_dim=self.get_build_param("embeddings_dim"),
                nchars=self.get_build_param("nchars"),
                lstm_size=self.get_build_param("lstm_size"),
                gpu_device=self.get_build_param("gpu_device"),
                is_medical=self.get_build_param("is_medical"),
            )

            file_location = os.path.join(tmp_location, model_filename)
            _HadoopOperations(file_location, model_location).apply()

        else:
            create_graph(
                model_location=model_location,
                model_filename=model_filename,
                ntags=self.get_build_param("ntags"),
                embeddings_dim=self.get_build_param("embeddings_dim"),
                nchars=self.get_build_param("nchars"),
                lstm_size=self.get_build_param("lstm_size"),
                gpu_device=self.get_build_param("gpu_device"),
                is_medical=self.get_build_param("is_medical"),
            )


class RelationExtractionTFGraphBuilder(GenericClassifierTFGraphBuilder):
    """
    Class to build the the TF graphs for RelationExtractionApproach

    Examples
    --------

    >>> from sparknlp_jsl.training import tf_graph
    >>> from sparknlp_jsl.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> tf_graph.build("relation_extraction", build_params={"input_dim": 6000, "output_dim": 3, 'batch_norm':1, "hidden_layers": [300, 200], "hidden_act": "relu", 'hidden_act_l2':1}, model_location=".", model_filename="re_with_BN")
    >>> re_approach = RelationExtractionApproach() \\
    ...    .setLabelColumn("rel") \\
    ...    .setInputCols(["embeddings", "pos_tags", "train_ner_chunks", "dependencies"]) \\
    ...    .setOutputCol("relations") \\
    ...    .setModelFile('./re_with_BN') \\
    ...    .setEpochsNumber(70) \\
    ...    .setBatchSize(200) \\
    ...    .setFixImbalance(True) \\
    ...    .setLearningRate(0.001) \\
    ...    .setFromEntity("begin1i", "end1i", "label1") \\
    ...    .setToEntity("begin2i", "end2i", "label2") \\
    ...    .setValidationSplit(0.2)
    """

    def get_model_filename(self):
        return "rel_e.in{}.out{}.pb".format(
            self.get_build_param("input_dim"),
            self.get_build_param("output_dim"),
        )


class TFGraphBuilderFactory:
    """
    Factory class to create the the different tensorflow graphs for ner_dl, generic_classifier, assertion_dl, relation_extraction annotators in spark-nlp healthcare
    """

    __model_builders = {
        "ner_dl": NerTFGraphBuilder,
        "generic_classifier": GenericClassifierTFGraphBuilder,
        "assertion_dl": AssertionTFGraphBuilder,
        "relation_extraction": RelationExtractionTFGraphBuilder
    }

    @staticmethod
    def get_models():
        """
        Method that return the available tf models in  spark-nlp healthcare
        Examples
        --------
        >>> from sparknlp_jsl.training import tf_graph
        >>> tf_graph.get_models()
        """
        return list(TFGraphBuilderFactory.__model_builders.keys())

    @staticmethod
    def build(model_name, build_params, model_location, model_filename="auto"):
        """
        Method that create the tf graph.

        Parameters
        ----------
        model_name: str
            The name of the tf model that you want to build.Model availables ner_dl,generic_classifier,assertion_dl and relation_extraction
        build_params: dict
            Configuration params to build the tf graph for the specific model.
        model_location: str
            Path where the model will be saved
        model_filename: str
            Name of the .rb file. If you put auto the filename will be generated.

        Examples
        --------
        >>> from sparknlp_jsl.training import tf_graph
        >>> tf_graph.build("assertion_dl",build_params={"n_classes": 10}, model_location="/tmp", model_filename="assertion_dl.pb")

        """
        try:
            import tensorflow as tf

            if tf.__version__[0] == '2':

                try:
                    import tensorflow_addons

                except ModuleNotFoundError:
                    raise TensorflowAddonsNeeded()

            if not (tf.__version__.startswith("1.15") or tf.__version__[0] == '2'):
                raise WrongTFVersion()

        except WrongTFVersion:
            print(tf.version)
            raise Exception("Tensorflow 2.xx or 1.15 is required to build model graphs.")

        except ModuleNotFoundError:
            raise Exception("You need to install Tensorflow 2.xx or 1.15 to be able to build model graphs")

        except TensorflowAddonsNeeded:
            raise Exception("You need to install tensorflow_addons to be able to generate graphs in Tensorflow 2.x")

        if model_name not in TFGraphBuilderFactory.__model_builders:
            raise Exception(f"Can't build a graph for {model_name}: model not supported.")

        model = TFGraphBuilderFactory.__model_builders[model_name](build_params)
        model.check_build_params()

        if model_filename == "auto":
            if not model.supports_auto_file_name():
                msg = f"""
                    {model_name} doesn't support automatic filename generation, please specify the filename of the
                    output graph
                """.strip()
                raise Exception(msg)
            else:
                model_filename = model.get_model_filename()

        model.build(model_location, model_filename)

        if (re.match(r'(\w+)://.*', model_location)):
            tmp_location = "/tmp/relationModel"
            model.build(tmp_location, model_filename)

            file_location = os.path.join(tmp_location, model_filename)
            _HadoopOperations(file_location, model_location).apply()

        else:
            model.build(model_location, model_filename)

        print("{} graph exported to {}/{}".format(model_name, model_location, model_filename))

    @staticmethod
    def print_model_params(model_name):
        """
        Method that return the params allowed for the tf model.This method return the params with the description for every param.

        Parameters
        ----------
        model_name: str
            The name of the tf model name.Model availables ner_dl,generic_classifier,assertion_dl and relation_extraction

        Examples
        --------
        >>> from sparknlp_jsl.training import tf_graph
        >>> tf_graph.print_model_params("assertion_dl")
        """
        if model_name not in TFGraphBuilderFactory.get_models():
            raise Exception(f"Model {model_name} not supported.")

        model = TFGraphBuilderFactory.__model_builders[model_name]({})
        model_params = model.get_model_build_params()
        model_params_descr = model.get_model_build_param_explanations()

        print(f"{model_name} parameters.")
        print("{:<20} {:<10} {:<20} {}".format("Parameter", "Required", "Default value", "Description"))
        for param in model_params:
            if type(model_params[param]) in [list, tuple]:
                default_value = "[" + ", ".join(map(str, model_params[param])) + "]"
            else:
                default_value = model_params[param]

            print("{:<20} {:<10} {:<20} {}".format(
                param,
                "yes" if default_value is None else "no",
                default_value if default_value is not None else "-",
                model_params_descr[param] if param in model_params_descr else ""
            ))
