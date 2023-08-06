from sparknlp.common import *

class AverageEmbeddings(AnnotatorModel):
    name = "AverageEmbeddings"

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.embeddings.AverageEmbeddings", java_model=None):
        super(AverageEmbeddings, self).__init__(
            classname=classname,
            java_model=java_model
        )