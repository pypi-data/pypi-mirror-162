from sparknlp.common import *

class ResolverMerger(AnnotatorModel):
    """
        Merge Label dependencies entities and the Sentence enitity resolver returning the sentence entity resolver.

        ===============================  =======================
        Input Annotation types            Output Annotation type
        ===============================  =======================
        ``ENTITY``,``LABEL_DEPENDENCY``  ``ENTITY``
        ===============================  =======================

    """

    name = "ResolverMerger"


    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.resolution.ResolverMerger", java_model=None):
        super(ResolverMerger, self).__init__(
            classname=classname,
            java_model=java_model
        )