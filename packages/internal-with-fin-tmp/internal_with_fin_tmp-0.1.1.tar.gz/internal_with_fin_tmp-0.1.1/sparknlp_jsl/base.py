"""
The FeaturesAssembler is used to collect features from different columns. It can collect features from single value
columns (anything which can be cast to a float, if casts fails then the value is set to 0), array columns or
SparkNLP annotations (if the annotation is an embedding, it takes the embedding, otherwise tries to cast the
`result` field). The output of the transformer is a `FEATURE_VECTOR` annotation (the numeric vector is in the
`embeddings` field).



Example:

>>> import sparknlp
>>> from sparknlp.base import *
>>> from sparknlp.common import *
>>> from sparknlp.training import *
>>> import sparknlp_jsl
>>> from sparknlp_jsl.base import *
>>> data = spark.read.option("header", "true").option("timestampFormat", "yyyy/MM/dd HH:mm:ss ZZ") \\
...            .csv("./test_jsl/resources/relfeatures.csv") \\
...            .withColumn("array_column", F.array("words_in_ent1", "words_in_ent2"))
...
>>> features_asm1 = sparknlp_jsl.base.FeaturesAssembler()\
...                    .setInputCols(["words_in_ent1", "words_in_ent2", "words_between", "array_column"]) \
...                    .setOutputCol("features_t")


>>>  results = Pipeline().setStages([features_asm1]).fit(self.__data).transform(self.__data).cache()
"""

from pyspark import keyword_only
from pyspark.ml.param.shared import Param, Params, TypeConverters
from sparknlp.internal import AnnotatorTransformer


class FeaturesAssembler(AnnotatorTransformer):
    inputCols = Param(Params._dummy(), "inputCols", "input column names", typeConverter=TypeConverters.toListString)
    outputCol = Param(Params._dummy(), "outputCol", "output column name", typeConverter=TypeConverters.toString)
    name = 'FeaturesAssembler'

    @keyword_only
    def __init__(self):
        super(FeaturesAssembler, self).__init__(classname="com.johnsnowlabs.nlp.FeaturesAssembler")
        self._setDefault(outputCol="feature_vector")

    @keyword_only
    def setParams(self):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def setInputCols(self, value):
        """Sets input columns name.

        Parameters
        ----------
        value : str
            Name of the input column
        """
        return self._set(inputCols=value)

    def setOutputCol(self, value):
        """Sets output column name.

        Parameters
        ----------
        value : str
            Name of the Output Column
        """
        return self._set(outputCol=value)
