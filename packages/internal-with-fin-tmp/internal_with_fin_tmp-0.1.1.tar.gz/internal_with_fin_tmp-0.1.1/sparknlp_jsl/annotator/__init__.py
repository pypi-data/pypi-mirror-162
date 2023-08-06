

print('lol')
from sparknlp_jsl.annotator.assertion import *
from sparknlp_jsl.annotator.chunker import *
from sparknlp_jsl.annotator.classification import *
from sparknlp_jsl.annotator.context import *
from sparknlp_jsl.annotator.deid import *
from sparknlp_jsl.annotator.disambiguation import *
from sparknlp_jsl.annotator.embeddings import *
from sparknlp_jsl.annotator.generic_classifier import *
from sparknlp_jsl.annotator.merge import *
from sparknlp_jsl.annotator.ner import *
from sparknlp_jsl.annotator.normalizer import *
from sparknlp_jsl.annotator.re import *
from sparknlp_jsl.annotator.resolution import *
from sparknlp_jsl.annotator.annotation_merger import *
from sparknlp_jsl.annotator.router import *
from sparknlp_jsl.annotator.tf_graph_builder import *


from sparknlp_jsl.extensions.finance import *


from sparknlp.annotator import *

if sys.version_info[0] == 2:
    raise ImportError(
        "Spark NLP only supports Python 3.6 and above. "
        "Please use Python 3.6 or above that is compatible with both Spark NLP and PySpark"
    )
else:
    __import__("com.johnsnowlabs.nlp")
    __import__("com.johnsnowlabs.extensions.finance")

sparknlp.annotator.assertion = sys.modules[__name__]
sparknlp.annotator.assertion.dl = sys.modules[__name__]
sparknlp.annotator.assertion.logreg = sys.modules[__name__]
sparknlp.annotator.resolution = sys.modules[__name__]
sparknlp.annotator.classification = sys.modules[__name__]
sparknlp.annotator.deid = sys.modules[__name__]
sparknlp.annotator.disambiguation = sys.modules[__name__]
sparknlp.annotator.keyword = sys.modules[__name__]
sparknlp.annotator.context = sys.modules[__name__]
sparknlp.annotator.merge = sys.modules[__name__]
sparknlp.annotator.ner = sys.modules[__name__]
sparknlp.annotator.generic_classifier = sys.modules[__name__]
sparknlp.annotator.re = sys.modules[__name__]
sparknlp.annotator.chunker = sys.modules[__name__]


sparknlp.annotator.finance_classifier_dl = sys.modules[__name__]

sparknlp.extensions = sys.modules[__name__]
sparknlp.extensions.finance = sys.modules[__name__]
sparknlp.extensions.finance_classifier_dl = sys.modules[__name__]


finance = sys.modules[__name__]
extensions = sys.modules[__name__]
extensions.finance = [__name__]


finance_classifier_dl = sys.modules[__name__]


assertion = sys.modules[__name__]
assertion.dl = sys.modules[__name__]
assertion.logreg = sys.modules[__name__]
resolution = sys.modules[__name__]
classification = sys.modules[__name__]
deid = sys.modules[__name__]
disambiguation = sys.modules[__name__]
keyword = sys.modules[__name__]
context = sys.modules[__name__]
merge = sys.modules[__name__]
ner = sys.modules[__name__]
generic_classifier = sys.modules[__name__]
re = sys.modules[__name__]
chunker = sys.modules[__name__]