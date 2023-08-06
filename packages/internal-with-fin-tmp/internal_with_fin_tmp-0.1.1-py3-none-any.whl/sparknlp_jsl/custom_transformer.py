from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol
# Available in PySpark >= 2.3.0
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from sparknlp.annotation import Annotation
from sparknlp.functions import map_annotations


class CustomTransformer(
    Transformer, HasInputCol, HasOutputCol,
    DefaultParamsReadable, DefaultParamsWritable):
    f = lambda a: a

    def __init__(self, f):
        super(CustomTransformer, self).__init__()
        self.f = f

    def setInputCol(self, value):
        """
        Sets the value of :py:attr:`inputCol`.
        """
        return self._set(inputCol=value)

    def setOutputCol(self, value):
        """
        Sets the value of :py:attr:`outputCol`.
        """
        return self._set(outputCol=value)

    def _transform(self, dataset):
        t = Annotation.arrayType()
        out_col = self.getOutputCol()
        in_col = dataset[self.getInputCol()]
        return dataset.withColumn(out_col, map_annotations(self.f, t)(in_col))
