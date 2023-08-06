from sparknlp.common import *

class DateNormalizer(AnnotatorModel):
    """
    Try to normalize dates in chunks annotations.
    The expected format for the date will be YYYY/MM/DD.
    If the date is normalized then field normalized in metadata will be true else will be false.


    ====================== ======================
    Input Annotation types Output Annotation type
    ====================== ======================
    ``CHUNK``              ``CHUNK``
    ====================== ======================

    Parameters
    ----------
    anchorDateYear
        Add an anchor year for the relative dates such as a day after tomorrow.
        If not set it will use the current year. Example: 2021
    anchorDateMonth
        Add an anchor month for the relative dates such as a day after tomorrow.
        If not set it will use the current month. Example: 1 which means January
    anchorDateDay
        Add an anchor day of the day for the relative dates such as a day after
        tomorrow. If not set it will use the current day. Example: 11

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
    >>>document_assembler = DocumentAssembler().setInputCol('ner_chunk').setOutputCol('document')
    >>>chunksDF = document_assembler.transform(df)
    >>>aa = map_annotations_col(chunksDF.select("document"),
    ...                    lambda x: [Annotation('chunk', a.begin, a.end, a.result, a.metadata, a.embeddings) for a in x], "document",
    ...                    "chunk_date", "chunk")
    >>>dateNormalizer = DateNormalizer().setInputCols('chunk_date').setOutputCol('date').setAnchorDateYear(2000).setAnchorDateMonth(3).setAnchorDateDay(15)
    >>> result = dateNormalizer.transform(aa)
    >>> data = spark.createDataFrame([["Fri, 21 Nov 1997"], ["next week at 7.30"], ["see you a day after"]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    >>> result.selectExpr("date.result","text")
    +-------------+-----------+
    |       result|       text|
    +-------------+-----------+
    | [08/02/2018]| 08/02/2018|
    |    [11/2018]|    11/2018|
    | [11/01/2018]| 11/01/2018|
    |[next monday]|next monday|
    |      [today]|      today|
    |  [next week]|  next week|
    +-------------+-----------+
    """
    name = "DateNormalizer"

    anchorDateYear = Param(Params._dummy(),
                           "anchorDateYear",
                           "Add an anchor year for the relative dates such as a day after tomorrow. If not set it "
                           "will use the current year. Example: 2021",
                           typeConverter=TypeConverters.toInt
                           )

    anchorDateMonth = Param(Params._dummy(),
                            "anchorDateMonth",
                            "Add an anchor month for the relative dates such as a day after tomorrow. If not set it "
                            "will use the current month. Example: 1 which means January",
                            typeConverter=TypeConverters.toInt
                            )

    anchorDateDay = Param(Params._dummy(),
                          "anchorDateDay",
                          "Add an anchor day of the day for the relative dates such as a day after tomorrow. If not "
                          "set it will use the current day. Example: 11",
                          typeConverter=TypeConverters.toInt
                          )

    def setAnchorDateYear(self, value):
        """Sets an anchor year for the relative dates such as a day after
        tomorrow. If not set it will use the current year.

        Example: 2021

        Parameters
        ----------
        value : int
            The anchor year for relative dates
        """
        return self._set(anchorDateYear=value)

    def setAnchorDateMonth(self, value):
        """Sets an anchor month for the relative dates such as a day after
        tomorrow. If not set it will use the current month.

        Example: 1 which means January

        Parameters
        ----------
        value : int
            The anchor month for relative dates
        """
        normalized_value = value - 1
        return self._set(anchorDateMonth=normalized_value)

    def setAnchorDateDay(self, value):
        """Sets an anchor day of the day for the relative dates such as a day
        after tomorrow. If not set it will use the current day.

        Example: 11

        Parameters
        ----------
        value : int
            The anchor day for relative dates
        """
        return self._set(anchorDateDay=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.normalizer.DateNormalizer", java_model=None):
        super(DateNormalizer, self).__init__(
            classname=classname,
            java_model=java_model
        )
