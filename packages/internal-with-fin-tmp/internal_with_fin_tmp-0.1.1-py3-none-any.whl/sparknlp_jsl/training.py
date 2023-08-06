from pyspark.ml import PipelineModel
from pyspark.sql import DataFrame
from sparknlp.internal import ExtendedJavaWrapper

from ._tf_graph_builders.graph_builders import TFGraphBuilderFactory
from ._tf_graph_builders_1x.graph_builders import TFGraphBuilderFactory as TFGraphBuilderFactory1x


class AnnotationToolJsonReader(ExtendedJavaWrapper):
    """
    Class to This a reader that generate a assertion train set from the json from annotations labs exports.

    Examples
    --------
    >>> from sparknlp_jsl.training import AnnotationToolJsonReader
    >>> assertion_labels = ["AsPresent","Absent"]
    >>> excluded_labels = ["Treatment"]
    >>> split_chars = [" ", "\\-"]
    >>> context_chars = [".", ",", ";"]
    >>> SDDLPath = ""
    >>> rdr = AnnotationToolJsonReader(assertion_labels = assertion_labels, excluded_labels = excluded_labels, split_chars = split_chars, context_chars = context_chars,SDDLPath=SDDLPath)
    >>> path = "src/test/resources/anc-pos-corpus-small/test-training.txt"
    >>> df = rdr.readDataset(spark, json_path)
    >>> assertion_df = rdr.generateAssertionTrainSet(df)
    >>> assertion_df.show()

    """

    def __init__(self, pipeline_model=None, assertion_labels=None, excluded_labels=None, cleanup_mode="disabled",
                 split_chars=None, context_chars=None, scheme="IOB", min_chars_tol=2, align_chars_tol=1,
                 merge_overlapping=True, SDDLPath=""):
        """
        Attributes
        ----------
        pipeline_model: str
             The pipeline model that is used to create the documents the sentences and the tokens.That pipeline model
             needs to have a DocumentAssembler, SentenceDetector and Tokenizer.The input column of the document assembler
             needs to be named a 'text'.The output of the sentence detector needs to be named a 'sentence'.
             The output of the tokenizer needs to be named a 'token'.
        assertion_labels: list
            The assertions labels are used for the training dataset creation.
        excluded_labels: list
            The assertions labels that are excluded for the training dataset creation.
        cleanup_mode: str
            The clean mode that is used in the DocumentAssembler transformer.
        split_chars: list
            The split chars that are used in the default tokenizer.
        context_chars: list
            The context chars that are used in the default tokenizer.
        scheme: str
             The schema that will use to create the IOB_tagger (IOB or BIOES).
        merge_overlapping: bool
            Whether merge the chunks when they are in the same position

        """
        if assertion_labels is None:
            assertion_labels = []
        if excluded_labels is None:
            excluded_labels = []
        if type(pipeline_model) == PipelineModel:
            if scheme is None:
                scheme = "IOB"
            if min_chars_tol is None:
                min_chars_tol = 2
            if min_chars_tol is None:
                min_chars_tol = 1
            if merge_overlapping is None:
                merge_overlapping = True
            super(AnnotationToolJsonReader, self).__init__("com.johnsnowlabs.nlp.training.AnnotationToolJsonReader",
                                                           pipeline_model._to_java(), assertion_labels, excluded_labels,
                                                           scheme, min_chars_tol, align_chars_tol, merge_overlapping)
        else:
            if split_chars is None:
                split_chars = [" "]
            if context_chars is None:
                context_chars = [".", ",", ";", ":", "!", "?", "*", "-", "(", ")", "\"", "'"]

            super(AnnotationToolJsonReader, self).__init__("com.johnsnowlabs.nlp.training.AnnotationToolJsonReader",
                                                           assertion_labels, excluded_labels, cleanup_mode,
                                                           split_chars, context_chars, scheme,
                                                           min_chars_tol, align_chars_tol, merge_overlapping, SDDLPath)

    def readDataset(self, spark, path):

        # ToDo Replace with std pyspark
        jSession = spark._jsparkSession

        jdf = self._java_obj.readDataset(jSession, path)
        return DataFrame(jdf, spark._wrapped)

    def generateAssertionTrainSet(self, df, sentenceCol="sentence", assertionCol="assertion_label"):

        jdf = self._java_obj.generateAssertionTrainSet(df._jdf, sentenceCol, assertionCol)
        return DataFrame(jdf, df.sql_ctx)

    def generateConll(self, df, path: str, taskColumn: str = "task_id", tokenCol: str = "token",
                      nerLabel: str = "ner_label"):
        jdf = self._java_obj.generateConll(df._jdf, path, taskColumn, tokenCol, nerLabel)

    def generatePlainAssertionTrainSet(self, df, taskColumn: str = "task_id", tokenCol: str = "token",
                                       nerLabel: str = "ner_label", assertion_label: str = "assertion_label"):
        jdf = self._java_obj.generatePlainAssertionTrainSet(df._jdf, taskColumn, tokenCol, nerLabel, assertion_label)
        return DataFrame(jdf, df.sql_ctx)


class CodiEspReader(ExtendedJavaWrapper):
    def __init__(self, scheme="IOB"):
        super(CodiEspReader, self).__init__("com.johnsnowlabs.nlp.training.CodiEspReader", scheme)

    def readDatasetTaskX(self, spark, path, textFolder, sep="\t"):
        # ToDo Replace with std pyspark
        jSession = spark._jsparkSession

        jdf = self._java_obj.readDatasetTaskX(jSession, path, textFolder, sep)
        return DataFrame(jdf, spark._wrapped)


class CantemistReader(ExtendedJavaWrapper):
    def __init__(self, scheme="IOB"):
        super(CantemistReader, self).__init__("com.johnsnowlabs.nlp.training.CantemistReader", scheme)

    def readDatasetTaskNer(self, spark, textFolder):
        # ToDo Replace with std pyspark
        jSession = spark._jsparkSession

        jdf = self._java_obj.readDatasetTaskNer(jSession, textFolder)
        return DataFrame(jdf, spark._wrapped)


tf_graph = TFGraphBuilderFactory()
tf_graph_1x = TFGraphBuilderFactory1x()
