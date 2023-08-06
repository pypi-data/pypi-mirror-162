from sparknlp.common import *
from sparknlp_jsl.annotator.deid import DeIdentificationModel as M
from sparknlp_jsl.annotator.deid import DeIdentification as A
class DeIdentification(A):
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

    @keyword_only
    def __init__(self):
        super(DeIdentification, self).__init__(classname="com.johnsnowlabs.extensions.finance.chunk_classification.deid.DeIdentification")

    def _create_model(self, java_model):
        return DeIdentificationModel(java_model=java_model)


class DeIdentificationModel(M):
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

    def __init__(self, classname="com.johnsnowlabs.extensions.finance.chunk_classification.deid.DeIdentificationModel", java_model=None):
        super(DeIdentificationModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        return ResourceDownloader.downloadModel(DeIdentificationModel, name, lang, remote_loc,
                                                j_dwn='InternalsPythonResourceDownloader')