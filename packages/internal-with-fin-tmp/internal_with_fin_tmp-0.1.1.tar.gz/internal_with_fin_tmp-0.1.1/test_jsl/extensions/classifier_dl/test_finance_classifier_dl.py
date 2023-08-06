from pyspark.ml import Pipeline, PipelineModel
import unittest
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from sparknlp_jsl.annotator import *

def get_spark_session():
    jar_base = '/home/ckl/old_home/ckl/Documents/freelance/jsl/jsl_internal_latest69696/lib'
    nlp_jar = jar_base + '/spark-nlp-assembly-4.0.0.jar'
    hc_jar = jar_base + '/spark-nlp-jsl-assembly-4.0.0.jar'
    spark = SparkSession.builder \
        .master("local[*]") \
        .config("spark.driver.memory", "16G") \
        .config("spark.jars", ','.join([nlp_jar, hc_jar])) \
        .getOrCreate()
    return spark


class FinanceClassifierDLSuite(unittest.TestCase):
    spark = get_spark_session()
    pipeSavePath = "/home/ckl/old_home/ckl/Documents/freelance/jsl/jsl_internal_latest69696/tmp/trained_models/FinPipe"
    modelSavePath = "/home/ckl/old_home/ckl/Documents/freelance/jsl/jsl_internal_latest69696/tmp/trained_models/FinModel"
    use_path = '/home/ckl/cache_pretrained/tfhub_use_en_2.4.0_2.4_1587136330099'
    data = spark.createDataFrame(
        [["I'm ready!"], ["If I could put into words how much I love waking up at 6 am on Mondays I would."]]).toDF(
        "text")

    def test_pretrained_model(self):
        model = FinanceClassifierDLModel.load(self.modelSavePath)
        useEmbeddings = UniversalSentenceEncoder.load(self.use_path) \
            .setInputCols("document") \
            .setOutputCol("sentence_embeddings")

        documentAssembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        sentence = SentenceDetector() \
            .setInputCols("document") \
            .setOutputCol("sentence")

        pipeline = Pipeline() \
            .setStages([
            documentAssembler,
            sentence,
            useEmbeddings,
            model
        ])

        result = pipeline.fit(self.data).transform(self.data)
        result.show()
        print(model)

    def test_pipe(self):
        PipelineModel.load(self.pipeSavePath).transform(self.data).show()


if __name__ == '__main__':
    unittest.main()
