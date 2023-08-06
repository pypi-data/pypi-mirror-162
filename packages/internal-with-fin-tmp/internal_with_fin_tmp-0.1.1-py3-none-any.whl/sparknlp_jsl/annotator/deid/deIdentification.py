from sparknlp.common import *

class DeIdentification(AnnotatorApproach):
    """Contains all the methods for training a DeIdentificationModel model.
    This module can obfuscate or mask the entities that contains personal information. These can be set with a file of
    regex patterns with setRegexPatternsDictionary, where each line is a mapping of entity to regex

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, TOKEN``                ``DOCUMENT``
    ========================================= ======================

    Parameters
    ----------
    regexPatternsDictionary
        ictionary with regular expression patterns that match some protected entity
    mode
        Mode for Anonimizer ['mask'|'obfuscate']
    obfuscateDate
        When mode=='obfuscate' whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible. When setting to ``true``, make sure dateFormats param fits the needs (default: false)
    obfuscateRefFile
        File with the terms to be used for Obfuscation
    refFileFormat
        Format of the reference file
    refSep
        Sep character in refFile
    dateTag
        Tag representing dates in the obfuscate reference file (default: DATE)
    days
        Number of days to obfuscate the dates by displacement. If not provided a random integer between 1 and 60 will be used
    dateToYear
        True if we want the model to transform dates into years, False otherwise.
    minYear
        Minimum year to be used when transforming dates into years.
    dateFormats
        List of date formats to automatically displace if parsed
    consistentObfuscation
        Whether to replace very similar entities in a document with the same randomized term (default: true)
        The similarity is based on the Levenshtein Distance between the words.
    sameEntityThreshold
        Similarity threshold [0.0-1.0] to consider two appearances of an entity as ``the same`` (default: 0.9).
    obfuscateRefSource
        The source of obfuscation of to obfuscate the entities.For dates entities doesnt apply tha method.
        The values ar the following:
        file: Takes the entities from the obfuscatorRefFile
        faker: Takes the entities from the Faker module
        both : Takes the entities from the obfuscatorRefFile and the faker module randomly.

    regexOverride
        If is true prioritize the regex entities, if is false prioritize the ner.
    seed
        It is the seed to select the entities on obfuscate mode.With the seed you can reply a execution several times with the same ouptut.
    ignoreRegex
       Select if you want to use regex file loaded in the model.If true the default regex file will be not used.The default value is false.
    isRandomDateDisplacement
        Use a random displacement days in dates entities,that random number is based on the [[DeIdentificationParams.seed]]
        If true use random displacement days in dates entities,if false use the [[DeIdentificationParams.days]]
        The default value is false.
    mappingsColumn
        This is the mapping column that will return the Annotations chunks with the fake entities.
    returnEntityMappings
        With this property you select if you want to return mapping column
    blackList
        List of entities ignored for masking or obfuscation.The default values are: "SSN","PASSPORT","DLN","NPI","C_CARD","IBAN","DEA"

    maskingPolicy
        Select the masking policy:
            same_length_chars: Replace the obfuscated entity with a masking sequence composed of asterisks and surrounding squared brackets, being the total length of the masking sequence of the same length as the original sequence.
            Example, Smith -> [***].
            If the entity is less than 3 chars (like Jo, or 5), asterisks without brackets will be returned.
            entity_labels: Replace the values with the corresponding entity labels.
            fixed_length_chars: Replace the obfuscated entity with a masking sequence composed of a fixed number of asterisks.

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
    ...
    >>>  sentenceDetector = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence") \\
    ...     .setUseAbbreviations(True)
    ...
    >>> tokenizer = Tokenizer() \
    ...     .setInputCols(["sentence"]) \
    ...     .setOutputCol("token")
    ...
    >> embeddings = WordEmbeddingsModel \
    ...     .pretrained("embeddings_clinical", "en", "clinical/models") \
    ...     .setInputCols(["sentence", "token"]) \
    ...     .setOutputCol("embeddings")
    ...
     Ner entities
    >>> clinical_sensitive_entities = MedicalNerModel \\
    ...     .pretrained("ner_deid_enriched", "en", "clinical/models") \\
    ...     .setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    ...
    >>> nerConverter = NerConverter() \\
    ...     .setInputCols(["sentence", "token", "ner"]) \\
    ...     .setOutputCol("ner_con")
     Deidentification
    >>> deIdentification = DeIdentification() \\
    ...     .setInputCols(["ner_chunk", "token", "sentence"]) \\
    ...     .setOutputCol("dei") \\
    ...     # file with custom regex pattern for custom entities\
    ...     .setRegexPatternsDictionary("path/to/dic_regex_patterns_main_categories.txt") \\
    ...     # file with custom obfuscator names for the entities\
    ...     .setObfuscateRefFile("path/to/obfuscate_fixed_entities.txt") \\
    ...     .setRefFileFormat("csv") \\
    ...     .setRefSep("#") \\
    ...     .setMode("obfuscate") \\
    ...     .setDateFormats(Array("MM/dd/yy","yyyy-MM-dd")) \\
    ...     .setObfuscateDate(True) \\
    ...     .setDateTag("DATE") \\
    ...     .setDays(5) \\
    ...     .setObfuscateRefSource("file")
    Pipeline
    >>> data = spark.createDataFrame([
    ...     ["# 7194334 Date : 01/13/93 PCP : Oliveira , 25 years-old , Record date : 2079-11-09."]
    ...     ]).toDF("text")
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     sentenceDetector,
    ...     tokenizer,
    ...     embeddings,
    ...     clinical_sensitive_entities,
    ...     nerConverter,
    ...     deIdentification
    ... ])
    >>> result = pipeline.fit(data).transform(data)
    >>> result.select("dei.result").show(truncate = False)
     +--------------------------------------------------------------------------------------------------+
     |result                                                                                            |
     +--------------------------------------------------------------------------------------------------+
     |[# 01010101 Date : 01/18/93 PCP : Dr. Gregory House , <AGE> years-old , Record date : 2079-11-14.]|
     +--------------------------------------------------------------------------------------------------+

    """

    name = "DeIdentification"

    regexPatternsDictionary = Param(Params._dummy(),
                                    "regexPatternsDictionary",
                                    "dictionary with regular expression patterns that match some protected entity",
                                    typeConverter=TypeConverters.identity)
    mode = Param(Params._dummy(), "mode", "Mode for Anonimizer ['mask'|'obfuscate']", TypeConverters.toString)

    maskingPolicy = Param(Params._dummy(), "maskingPolicy",
                          "Select the masking policy:'same_length_chars' or 'entity_labels'.", TypeConverters.toString)
    fixedMaskLength = Param(Params._dummy(), "fixedMaskLength",
                            "This is the length of the masking sequence that will be used when the 'fixed_length_chars' masking policy is selected.",
                            TypeConverters.toInt)

    obfuscateDate = Param(Params._dummy(), "obfuscateDate",
                          "When mode=='obfuscate' whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible. When setting to ``true``, make sure dateFormats param fits the needs (default: false)",
                          typeConverter=TypeConverters.toBoolean)
    obfuscateRefFile = Param(Params._dummy(), "obfuscateRefFile", "File with the terms to be used for Obfuscation",
                             TypeConverters.toString)
    refFileFormat = Param(Params._dummy(), "refFileFormat", "Format of the reference file", TypeConverters.toString)
    refSep = Param(Params._dummy(), "refSep", "Sep character in refFile", TypeConverters.toString)
    dateTag = Param(Params._dummy(), "dateTag",
                    "Tag representing dates in the obfuscate reference file (default: DATE)", TypeConverters.toString)
    days = Param(Params._dummy(), "days", "Number of days to obfuscate by displacement the dates.",
                 TypeConverters.toInt)
    dateToYear = Param(Params._dummy(), "dateToYear",
                       "True if we want the model to transform dates into years, False otherwise.",
                       TypeConverters.toBoolean)
    minYear = Param(Params._dummy(), "minYear", "Minimum year to be used when transforming dates into years.",
                    TypeConverters.toInt)
    dateFormats = Param(Params._dummy(), "dateFormats",
                        "List of date formats to automatically displace if parsed",
                        typeConverter=TypeConverters.toListString)
    consistentObfuscation = Param(Params._dummy(), "consistentObfuscation",
                                  "Whether to replace very similar entities in a document with the same randomized term (default: true).",
                                  TypeConverters.toBoolean)
    sameEntityThreshold = Param(Params._dummy(), "sameEntityThreshold",
                                "Similarity threshold [0.0-1.0] to consider two appearances of an entity as ``the same`` (default: 0.9).",
                                TypeConverters.toFloat)
    obfuscateRefSource = Param(Params._dummy(), "obfuscateRefSource",
                               "Mode for select obfuscate source ['both'|'faker'| 'file]", TypeConverters.toString)

    regexOverride = Param(Params._dummy(), "regexOverride", "Prioritice regex over ner entities",
                          TypeConverters.toBoolean)

    seed = Param(Params._dummy(), "seed", "It is the seed to select the entities on obfuscate mode",
                 TypeConverters.toInt)

    ignoreRegex = Param(Params._dummy(), "ignoreRegex", "Select if you want to use regex",
                        TypeConverters.toBoolean)

    isRandomDateDisplacement = Param(Params._dummy(), "isRandomDateDisplacement",
                                     "Select if you want to use random displacement in dates",
                                     TypeConverters.toBoolean)

    mappingsColumn = Param(Params._dummy(), "mappingsColumn",
                           "This is the mapping column that will return the Annotations chunks with the fake entities",
                           TypeConverters.toString)

    returnEntityMappings = Param(Params._dummy(), "returnEntityMappings",
                                 "With this property you select if you want to return mapping column",
                                 TypeConverters.toBoolean)
    blackList = Param(Params._dummy(), "blackList",
                      "List of entities ignored for masking or obfuscation.The default values are: \"SSN\",\"PASSPORT\",\"DLN\",\"NPI\",\"C_CARD\",\"IBAN\",\"DEA\"",
                      TypeConverters.toListString)
    language = Param(Params._dummy(), "language", "The language used to select the regex file and some faker entities",
                     TypeConverters.toString)

    @keyword_only
    def __init__(self):
        super(DeIdentification, self).__init__(classname="com.johnsnowlabs.nlp.annotators.deid.DeIdentification")

    def getBlackList(self):
        self.getOrDefault(self.blackList)

    def setLanguage(self, l):
        """The language used to select the regex file and some faker entities.'en'(english),'de'() or 'es'(Spanish)

        Parameters
        ----------
        l : str
          The language used to select the regex file and some faker entities.'en'(english),'de'() or 'es'(Spanish)
        """
        return self._set(language=l)

    def setRegexPatternsDictionary(self, path, read_as=ReadAs.TEXT, options=None):
        """Sets dictionary with regular expression patterns that match some protected entity

        Parameters
        ----------
        path : str
            Path wher is de dictionary
        read_as: ReadAs
            Format of the file
        options: dict
            Dictionary with the options to read the file.

        """
        if options is None:
            options = {"delimiter": " "}
        return self._set(regexPatternsDictionary=ExternalResource(path, read_as, options))

    def setMode(self, m):
        """Sets mode for Anonimizer ['mask'|'obfuscate']

        Parameters
        ----------
        m : str
            Mode for Anonimizer ['mask'|'obfuscate']
        """
        return self._set(mode=m)

    def setMaskingPolicy(self, m):
        """Sets the masking policy:
            same_length_chars: Replace the obfuscated entity with a masking sequence composed of asterisks and surrounding squared brackets, being the total length of the masking sequence of the same length as the original sequence.
            Example, Smith -> [***].
            If the entity is less than 3 chars (like Jo, or 5), asterisks without brackets will be returned.
            entity_labels: Replace the values with the corresponding entity labels.
            fixed_length_chars: Replace the obfuscated entity with a masking sequence composed of a fixed number of asterisks.

        Parameters
        ----------
        m : str
            The masking policy
        """
        return self._set(maskingPolicy=m)

    def setFixedMaskLength(self, length):
        """ Fixed mask length: this is the length of the masking sequence that will be used when the 'fixed_length_chars' masking
            policy is selected.
        Parameters
        ----------
        length : int
           The mask length
        """
        return self._set(fixedMaskLength=length)

    def setObfuscateRefFile(self, f):
        """Set file with the terms to be used for Obfuscation
        Parameters
        ----------
        f : str
            File with the terms to be used for Obfuscation
        """
        return self._set(obfuscateRefFile=f)

    def setRefFileFormat(self, f):
        """Sets format of the reference file

        Parameters
        ----------
        f : str
            Format of the reference file
        """
        return self._set(refFileFormat=f)

    def setRefSep(self, c):
        """Sets separator character in refFile

        Parameters
        ----------
        f : str
            Separator character in refFile
        """
        return self._set(refSep=c)

    def setDateTag(self, t):
        """Sets tag representing dates in the obfuscate reference file (default: DATE)

        Parameters
        ----------
        f : str
            Tag representing dates in the obfuscate reference file (default: DATE)
        """
        return self._set(dateTag=t)

    def setObfuscateDate(self, value):
        """Sets auxiliary label which maps resolved entities to additional labels

        Parameters
        ----------
        value : str
            When mode=="obfuscate" whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible.
            When setting to `true`, make sure dateFormats param fits the needs (default: false)
            WHen setting to 'false' then the date will be mask to <DATE>
        """
        return self._set(obfuscateDate=value)

    def setDays(self, d):
        """Sets number of days to obfuscate by displacement the dates.

        Parameters
        ----------
        d : int
            Number of days to obfuscate by displacement the dates.
        """
        return self._set(days=d)

    def setDateToYear(self, s):
        """Sets transform dates into years.

        Parameters
        ----------
        s : bool
            True if we want the model to transform dates into years, False otherwise.
        """
        return self._set(dateToYear=s)

    def setMinYear(self, s):
        """Sets minimum year to be used when transforming dates into years.

        Parameters
        ----------
        s : int
            Minimum year to be used when transforming dates into years.
        """
        return self._set(minYear=s)

    def setDateFormats(self, s):
        """Sets list of date formats to automatically displace if parsed

        Parameters
        ----------
        name : str
            List of date formats to automatically displace if parsed
        """
        return self._set(dateFormats=s)

    def setConsistentObfuscation(self, s):
        """Sets whether to replace very similar entities in a document with the same randomized term (default: true).The similarity is based on the Levenshtein Distance between the words.

        Parameters
        ----------
        s : str
            Whether to replace very similar entities in a document with the same randomized term .The similarity is based on the Levenshtein Distance between the words.
        """
        return self._set(consistentObfuscation=s)

    def setSameEntityThreshold(self, s):
        """Sets similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).

        Parameters
        ----------
        s : float
            Similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).
        """
        return self._set(sameEntityThreshold=s)

    def setObfuscateRefSource(self, s):
        """Sets mode for select obfuscate source ['both'|'faker'| 'file]

        Parameters
        ----------
        s : str
            Mode for select obfuscate source ['both'|'faker'| 'file]
        """
        return self._set(obfuscateRefSource=s)

    def setRegexOverride(self, s):
        """Sets whether to prioritize regex over ner entities

        Parameters
        ----------
        s : bool
            Whether to prioritize regex over ner entities
        """
        return self._set(regexOverride=s)

    def setIgnoreRegex(self, s):
        """Sets if you want to use regex.

        Parameters
        ----------
        s : bool
            Whether to use regex.
        """
        return self._set(ignoreRegex=s)

    def setSeed(self, s):
        """Sets the seed to select the entities on obfuscate mode

        Parameters
        ----------
        s : int
            The seed to select the entities on obfuscate mode
        """
        return self._set(seed=s)

    def setIsRandomDateDisplacement(self, s):
        """Sets if you want to use random displacement in dates

        Parameters
        ----------
        s : bool
            Boolean value to select if you want to use random displacement in dates
        """
        return self._set(isRandomDateDisplacement=s)

    def setMappingsColumn(self, s):
        """Sets the name of mapping column that will return the Annotations chunks with the fake entities

        Parameters
        ----------
        name : str
            Mapping column that will return the Annotations chunks with the fake entities
        """
        return self._set(mappingsColumn=s)

    def setReturnEntityMappings(self, s):
        """Sets if you want to return mapping column

        Parameters
        ----------
        s : bool
            Whether to return the mappings column.
        """
        return self._set(returnEntityMappings=s)

    def setBlackList(self, s):
        """List of entities ignored for masking or obfuscation.
        Parameters
        ----------
        s : list
            List of entities ignored for masking or obfuscation.The default values are: values are "SSN","PASSPORT","DLN","NPI","C_CARD","IBAN","DEA"
        """
        return self._set(blackList=s)

    def _create_model(self, java_model):
        return DeIdentificationModel(java_model=java_model)


class DeIdentificationModel(AnnotatorModel):
    """ The DeIdentificationModel model can obfuscate or mask the entities that contains personal information. These can be set with a file of
    regex patterns with setRegexPatternsDictionary, where each line is a mapping of entity to regex

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, TOKEN``                ``DOCUMENT``
    ========================================= ======================

    Parameters
    ----------
    regexPatternsDictionary
        ictionary with regular expression patterns that match some protected entity
    mode
        Mode for Anonimizer ['mask'|'obfuscate']
    obfuscateDate
        When mode=='obfuscate' whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible. When setting to `true`, make sure dateFormats param fits the needs (default: false)
    dateTag
        Tag representing dates in the obfuscate reference file (default: DATE)
    days
        Number of days to obfuscate the dates by displacement. If not provided a random integer between 1 and 60 will be used
    dateToYear
        True if we want the model to transform dates into years, False otherwise.
    minYear
        Minimum year to be used when transforming dates into years.
    dateFormats
        List of date formats to automatically displace if parsed
    consistentObfuscation
        Whether to replace very similar entities in a document with the same randomized term (default: true)
        The similarity is based on the Levenshtein Distance between the words.
    sameEntityThreshold
        Similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).
    obfuscateRefSource
        The source of obfuscation of to obfuscate the entities.For dates entities doesnt apply tha method.
        The values ar the following:
        file: Takes the entities from the obfuscatorRefFile
        faker: Takes the entities from the Faker module
        both: Takes the entities from the obfuscatorRefFile and the faker module randomly.
    regexOverride
        If is true prioritize the regex entities, if is false prioritize the ner.
    seed
        It is the seed to select the entities on obfuscate mode.With the seed you can reply a execution several times with the same ouptut.
    ignoreRegex
       Select if you want to use regex file loaded in the model.If true the default regex file will be not used.The default value is false.
    isRandomDateDisplacement
        Use a random displacement days in dates entities,that random number is based on the [[DeIdentificationParams.seed]]
        If true use random displacement days in dates entities,if false use the [[DeIdentificationParams.days]]
        The default value is false.
    mappingsColumn
        This is the mapping column that will return the Annotations chunks with the fake entities.
    returnEntityMappings
        With this property you select if you want to return mapping column
    blackList
        List of entities ignored for masking or obfuscation.The default values are: "SSN","PASSPORT","DLN","NPI","C_CARD","IBAN","DEA"
    regexEntities
        Keep the regex entities used in the regexPatternDictionary
    maskingPolicy
        Select the masking policy:
            same_length_chars: Replace the obfuscated entity with a masking sequence composed of asterisks and surrounding squared brackets, being the total length of the masking sequence of the same length as the original sequence.
            Example, Smith -> [***].
            If the entity is less than 3 chars (like Jo, or 5), asterisks without brackets will be returned.
            entity_labels: Replace the values with the corresponding entity labels.
            fixed_length_chars: Replace the obfuscated entity with a masking sequence composed of a fixed number of asterisks.

    fixedMaskLength: this is the length of the masking sequence that will be used when the 'fixed_length_chars' masking policy is selected.

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
    ...
    >>>  sentenceDetector = SentenceDetector() \\
    ...     .setInputCols(["document"]) \\
    ...     .setOutputCol("sentence") \\
    ...     .setUseAbbreviations(True)
    ...
    >>> tokenizer = Tokenizer() \
    ...     .setInputCols(["sentence"]) \
    ...     .setOutputCol("token")
    ...
    >> embeddings = WordEmbeddingsModel \
    ...     .pretrained("embeddings_clinical", "en", "clinical/models") \
    ...     .setInputCols(["sentence", "token"]) \
    ...     .setOutputCol("embeddings")
    ...
     Ner entities
    >>> clinical_sensitive_entities = MedicalNerModel \\
    ...     .pretrained("ner_deid_enriched", "en", "clinical/models") \\
    ...     .setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    ...
    >>> nerConverter = NerConverter() \\
    ...     .setInputCols(["sentence", "token", "ner"]) \\
    ...     .setOutputCol("ner_con")
    ...
     Deidentification
    >>> deIdentification = DeIdentificationModel.pretrained("deidentify_large", "en", "clinical/models") \\
    ...     .setInputCols(["ner_chunk", "token", "sentence"]) \\
    ...     .setOutputCol("dei") \\
    ...     .setMode("obfuscate") \\
    ...     .setDateFormats(Array("MM/dd/yy","yyyy-MM-dd")) \\
    ...     .setObfuscateDate(True) \\
    ...     .setDateTag("DATE") \\
    ...     .setDays(5) \\
    ...     .setObfuscateRefSource("both")
    >>> data = spark.createDataFrame([
    ...     ["# 7194334 Date : 01/13/93 PCP : Oliveira , 25 years-old , Record date : 2079-11-09."]
    ...     ]).toDF("text")
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     sentenceDetector,
    ...     tokenizer,
    ...     embeddings,
    ...     clinical_sensitive_entities,
    ...     nerConverter,
    ...     deIdentification
    ... ])
    >>> result = pipeline.fit(data).transform(data)
    >>> result.select("dei.result").show(truncate = False)
     +--------------------------------------------------------------------------------------------------+
     |result                                                                                            |
     +--------------------------------------------------------------------------------------------------+
     |[# 01010101 Date : 01/18/93 PCP : Dr. Gregory House , <AGE> years-old , Record date : 2079-11-14.]|
     +--------------------------------------------------------------------------------------------------+
    """
    name = "DeIdentificationModel"

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.deid.DeIdentificationModel", java_model=None):
        super(DeIdentificationModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    dateFormats = Param(Params._dummy(), "dateFormats",
                        "List of date formats to automatically displace if parsed",
                        typeConverter=TypeConverters.toListString)

    mode = Param(Params._dummy(), "mode", "Mode for Anonimizer ['mask'|'ofuscate']", TypeConverters.toString)

    maskingPolicy = Param(Params._dummy(), "maskingPolicy",
                          "Select the masking policy:'same_length_chars' or 'entity_labels'.", TypeConverters.toString)
    fixedMaskLength = Param(Params._dummy(), "fixedMaskLength",
                            "This is the length of the masking sequence that will be used when the 'fixed_length_chars' masking policy is selected.",
                            TypeConverters.toInt)
    obfuscateDate = Param(Params._dummy(), "obfuscateDate",
                          "When mode=='obfuscate' whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible. When setting to `true`, make sure dateFormats param fits the needs (default: false)",
                          typeConverter=TypeConverters.toBoolean)
    dateTag = Param(Params._dummy(), "dateTag",
                    "Tag representing dates in the obfuscate reference file (default: DATE)", TypeConverters.toString)
    days = Param(Params._dummy(), "days", "Number of days to obfuscate by displacement the dates.",
                 TypeConverters.toInt)
    dateToYear = Param(Params._dummy(), "dateToYear",
                       "Y if we want the model to transform dates into years, N otherwise.", TypeConverters.toBoolean)
    minYear = Param(Params._dummy(), "minYear", "Minimum year to be used when transforming dates into years.",
                    TypeConverters.toInt)
    dateFormats = Param(Params._dummy(), "dateFormats",
                        "List of date formats to automatically displace if parsed",
                        typeConverter=TypeConverters.toListString)
    consistentObfuscation = Param(Params._dummy(), "consistentObfuscation",
                                  "Whether to replace very similar entities in a document with the same randomized term (default: true).",
                                  TypeConverters.toBoolean)
    sameEntityThreshold = Param(Params._dummy(), "sameEntityThreshold",
                                "Similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).",
                                TypeConverters.toFloat)
    obfuscateRefSource = Param(Params._dummy(), "obfuscateRefSource",
                               "Mode for select obfuscate source ['both'|'faker'| 'file]", TypeConverters.toString)

    regexOverride = Param(Params._dummy(), "regexOverride", "Prioritice regex over ner entities",
                          TypeConverters.toBoolean)

    seed = Param(Params._dummy(), "seed", "It is the seed to select the entities on obfuscate mode",
                 TypeConverters.toInt)

    ignoreRegex = Param(Params._dummy(), "ignoreRegex", "Select if you want to use regex",
                        TypeConverters.toBoolean)

    isRandomDateDisplacement = Param(Params._dummy(), "isRandomDateDisplacement",
                                     "Select if you want to use random displacement in dates",
                                     TypeConverters.toBoolean)

    mappingsColumn = Param(Params._dummy(), "mappingsColumn",
                           "This is the mapping column that will return the Annotations chunks with the fake entities",
                           TypeConverters.toString)

    returnEntityMappings = Param(Params._dummy(), "returnEntityMappings",
                                 "With this property you select if you want to return mapping column",
                                 TypeConverters.toBoolean)

    blackList = Param(Params._dummy(), "blackList",
                      "List of entities ignored for masking or obfuscation.The default values are: \"SSN\",\"PASSPORT\",\"DLN\",\"NPI\",\"C_CARD\",\"IBAN\",\"DEA\"",
                      TypeConverters.toListString)

    regexEntities = Param(Params._dummy(), "regexEntities",
                          "Keep the regex entities used in the regexPatternDictionary",
                          TypeConverters.toListString)
    mode = Param(Params._dummy(), "mode", "Mode for Anonimizer ['mask'|'ofuscate']", TypeConverters.toString)

    language = Param(Params._dummy(), "language",
                     "The language used to select the regex file and some faker entities.'en'(english),'de'() or 'es'(Spanish)",
                     TypeConverters.toString)

    def getBlackList(self):
        self.getOrDefault(self.blackList)

    def setLanguage(self, l):
        """The language used to select the regex file and some faker entities.'en'(english),'de'() or 'es'(Spanish)

        Parameters
        ----------
        l : str
          The language used to select the regex file and some faker entities.'en'(english),'de'() or 'es'(Spanish)
        """
        return self._set(language=l)

    def setMode(self, m):
        """Sets mode for Anonimizer ['mask'|'obfuscate']

        Parameters
        ----------
        m : str
            Mode for Anonimizer ['mask'|'obfuscate']
        """
        return self._set(mode=m)

    def setMaskingPolicy(self, m):
        """Sets the masking policy:
            same_length_chars: Replace the obfuscated entity with a masking sequence composed of asterisks and surrounding squared brackets, being the total length of the masking sequence of the same length as the original sequence.
            Example, Smith -> [***].
            If the entity is less than 3 chars (like Jo, or 5), asterisks without brackets will be returned.
            entity_labels: Replace the values with the corresponding entity labels.
            fixed_length_chars: Replace the obfuscated entity with a masking sequence composed of a fixed number of asterisks.

        Parameters
        ----------
        m : str
            The masking policy
        """
        return self._set(maskingPolicy=m)

    def setFixedMaskLength(self, length):
        """ Fixed mask length: this is the length of the masking sequence that will be used when the 'fixed_length_chars' masking
            policy is selected.
        Parameters
        ----------
        length : int
           The mask length
        """
        return self._set(fixedMaskLength=length)

    def setDateTag(self, t):
        """Set file with the terms to be used for Obfuscation

        Parameters
        ----------
        f : str
            File with the terms to be used for Obfuscation
        """
        return self._set(dateTag=t)

    def setObfuscateDate(self, value):
        """Sets auxiliary label which maps resolved entities to additional labels

        Parameters
        ----------
        value : str
            When mode=="obfuscate" whether to obfuscate dates or not. This param helps in consistency to make dateFormats more visible.
            When setting to `true`, make sure dateFormats param fits the needs (default: false)
            WHen setting to 'false' then the date will be mask to <DATE>
        """
        return self._set(obfuscateDate=value)

    def setDays(self, d):
        """Sets number of days to obfuscate by displacement the dates.

        Parameters
        ----------
        d : int
            Number of days to obfuscate by displacement the dates.
        """
        return self._set(days=d)

    def setDateToYear(self, s):
        """Sets transform dates into years.

        Parameters
        ----------
        s : bool
            True if we want the model to transform dates into years, False otherwise.
        """
        return self._set(dateToYear=s)

    def setMinYear(self, s):
        """Sets minimum year to be used when transforming dates into years.

        Parameters
        ----------
        s : int
            Minimum year to be used when transforming dates into years.
        """
        return self._set(minYear=s)

    def setDateFormats(self, s):
        """Sets list of date formats to automatically displace if parsed

        Parameters
        ----------
        s : str
            List of date formats to automatically displace if parsed
        """
        return self._set(dateFormats=s)

    def setConsistentObfuscation(self, s):
        """Sets whether to replace very similar entities in a document with the same randomized term (default: true).The similarity is based on the Levenshtein Distance between the words.

        Parameters
        ----------
        s : str
            Whether to replace very similar entities in a document with the same randomized term (default: true).The similarity is based on the Levenshtein Distance between the words.
        """
        return self._set(consistentObfuscation=s)

    def setSameEntityThreshold(self, s):
        """Sets similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).

        Parameters
        ----------
        s : float
            Similarity threshold [0.0-1.0] to consider two appearances of an entity as `the same` (default: 0.9).
        """
        return self._set(sameEntityThreshold=s)

    def setObfuscateRefSource(self, s):
        """Sets mode for select obfuscate source ['both'|'faker'| 'file]

        Parameters
        ----------
        s : str
            Mode for select obfuscate source ['both'|'faker'| 'file]
        """
        return self._set(obfuscateRefSource=s)

    def setRegexOverride(self, s):
        """Sets whether to prioritize regex over ner entities

        Parameters
        ----------
        s : bool
            Whether to prioritize regex over ner entities
        """
        return self._set(regexOverride=s)

    def setSeed(self, s):
        """Sets the seed to select the entities on obfuscate mode

        Parameters
        ----------
        s : int
            The seed to select the entities on obfuscate mode
        """
        return self._set(seed=s)

    def setIgnoreRegex(self, s):
        """Sets if you want to use regex.

        Parameters
        ----------
        s : bool
            Whether to use regex.
        """
        return self._set(ignoreRegex=s)

    def setIsRandomDateDisplacement(self, s):
        """Sets if you want to use random displacement in dates

        Parameters
        ----------
        s : bool
            Boolean value to select if you want to use random displacement in dates
        """
        return self._set(isRandomDateDisplacement=s)

    def setMappingsColumn(self, s):
        """Sets the name of mapping column that will return the Annotations chunks with the fake entities

        Parameters
        ----------
        name : str
            Mapping column that will return the Annotations chunks with the fake entities
        """
        return self._set(mappingsColumn=s)

    def setBlackList(self, s):
        """List of entities ignored for masking or obfuscation.
        Parameters
        ----------
        s : list
            List of entities ignored for masking or obfuscation.The default values are: "SSN","PASSPORT","DLN","NPI","C_CARD","IBAN","DEA"
        """
        return self._set(blackList=s)

    def setReturnEntityMappings(self, s):
        """Sets if you want to return mapping column

        Parameters
        ----------
        s : bool
            Whether to save the mappings column.
        """
        return self._set(returnEntityMappings=s)

    def getRegexEntities(self):
        return self.getOrDefault(self.regexEntities)

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        return ResourceDownloader.downloadModel(DeIdentificationModel, name, lang, remote_loc,
                                                j_dwn='InternalsPythonResourceDownloader')