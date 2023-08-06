from sparknlp.common import *


class DrugNormalizer(AnnotatorModel):
    """Annotator which normalizes raw text from clinical documents, e.g. scraped web pages or xml documents, from document type columns into Sentence.
       Removes all dirty characters from text following one or more input regex patterns.
       Can apply non wanted character removal which a specific policy.
       Can apply lower case normalization.

    ==============================  ======================
    Input Annotation types          Output Annotation type
    ==============================  ======================
    ``DOCUMENT``                    ``DOCUMENT``
    ==============================  ======================

    Parameters
    ----------
    lowercase
        whether to convert strings to lowercase
    policy
        policy to remove patterns from text. Defaults "all"

    Examples
    --------

    >>> data = spark.createDataFrame([
    ...   ["Sodium Chloride/Potassium Chloride 13bag"],
    ...   ["interferon alfa-2b 10 million unit ( 1 ml ) injec"],
    ...   ["aspirin 10 meq/ 5 ml oral sol"]
    ... ]).toDF("text")
    >>> document = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> drugNormalizer = DrugNormalizer().setInputCols(["document"]).setOutputCol("document_normalized")
    >>> trainingPipeline = Pipeline(stages=[document, drugNormalizer])
    >>> result = trainingPipeline.fit(data).transform(data)
    >>> result.selectExpr("explode(document_normalized.result) as normalized_text").show(truncate=False)
    +----------------------------------------------------+
    |normalized_text                                     |
    +----------------------------------------------------+
    |Sodium Chloride / Potassium Chloride 13 bag         |
    |interferon alfa - 2b 10000000 unt ( 1 ml ) injection|
    |aspirin 2 meq/ml oral solution                      |
    +----------------------------------------------------+


    """
    lowercase = Param(Params._dummy(),
                      "lowercase",
                      "whether to convert strings to lowercase",
                      typeConverter=TypeConverters.toBoolean)

    policy = Param(Params._dummy(),
                   "policy",
                   "policy to remove patterns from text. Defaults \"all\"",
                   typeConverter=TypeConverters.toString)

    @keyword_only
    def __init__(self):
        super(DrugNormalizer, self).__init__(classname="com.johnsnowlabs.nlp.annotators.DrugNormalizer")
        self._setDefault(
            lowercase=False,
            policy="all"
        )

    def setLowercase(self, value):
        """Sets whether to convert strings to lowercase

        Parameters
        ----------
        p : bool
            Whether to convert strings to lowercase
        """
        return self._set(lowercase=value)

    def setPolicy(self, value):
        """Sets policy to remove patterns from text.

        Parameters
        ----------
        p : str
            policy to remove patterns from text.
        """
        return self._set(policy=value)

