from pyspark import SparkContext
from pyspark.sql.column import Column, _to_java_column


def profile(code_array, age, sex, elig="CNA", orec="0", medicaid=False):
    sc = SparkContext._active_spark_context
    jc = sc._jvm.com.johnsnowlabs.nlp.jsl.HCC.profileApply(_to_java_column(code_array), _to_java_column(age),
                                                           _to_java_column(sex), _to_java_column(elig),
                                                           _to_java_column(orec), _to_java_column(medicaid))
    return Column(jc)


def profileV23(code_array, age, sex, elig="CNA", orec="0", medicaid=False):
    sc = SparkContext._active_spark_context
    jc = sc._jvm.com.johnsnowlabs.nlp.jsl.HCC.profileApplyV23(_to_java_column(code_array), _to_java_column(age),
                                                              _to_java_column(sex), _to_java_column(elig),
                                                              _to_java_column(orec), _to_java_column(medicaid))
    return Column(jc)


def profileV22(code_array, age, sex, elig="CNA", orec="0", medicaid=False):
    sc = SparkContext._active_spark_context
    jc = sc._jvm.com.johnsnowlabs.nlp.jsl.HCC.profileApplyV22(_to_java_column(code_array), _to_java_column(age),
                                                              _to_java_column(sex), _to_java_column(elig),
                                                              _to_java_column(orec), _to_java_column(medicaid))
    return Column(jc)
