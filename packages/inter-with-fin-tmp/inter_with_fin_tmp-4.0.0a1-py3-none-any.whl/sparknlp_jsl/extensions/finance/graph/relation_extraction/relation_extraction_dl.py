from sparknlp.common import *
from sparknlp.internal import ExtendedJavaWrapper


class _RelationExtractionDLModelLoader(ExtendedJavaWrapper):
    def __init__(self, path, jspark):
        super(_RelationExtractionDLModelLoader, self).__init__(
            "com.johnsnowlabs.nlp.annotators.re.RelationExtractionDLModel.loadSavedModel", path, jspark)


class RelationExtractionDLModel(AnnotatorModel):
    """
    Extracts and classifies instances of relations between named entities.
    In contrast with RelationExtractionModel, RelationExtractionDLModel is based on BERT.
    For pretrained models please see the

    ==========================================  ======================
    Input Annotation types                      Output Annotation type
    ==========================================  ======================
    ``CHUNK, DOCUMENT``                         ``CATEGORY``
    ==========================================  ======================

    Parameters
    ----------
    predictionThreshold
        Minimal activation of the target unit to encode a new relation instance
    batchSize
        Number of relations to process at once

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
    ...   .setInputCol("text") \\
    ...   .setOutputCol("document")
    ...
    >>> tokenizer = Tokenizer() \\
    ...   .setInputCols(["document"]) \\
    ...   .setOutputCol("tokens")
    ...
    >>> embedder = WordEmbeddingsModel \
    ...   .pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens"]) \\
    ...   .setOutputCol("embeddings")
    ...
    >>> posTagger = PerceptronModel \\
    ...   .pretrained("pos_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens"]) \\
    ...   .setOutputCol("posTags")
    ...
    >>> nerTagger = MedicalNerModel \\
    ...   .pretrained("ner_events_clinical", "en", "clinical/models") \\
    ...   .setInputCols(["document", "tokens", "embeddings"]) \\
    ...   .setOutputCol("ner_tags")
    ...
    >>> nerConverter = NerConverter() \\
    ...   .setInputCols(["document", "tokens", "ner_tags"]) \\
    ...   .setOutputCol("nerChunks")
    ...
    >>> depencyParser = DependencyParserModel \\
    ...   .pretrained("dependency_conllu", "en") \\
    ...   .setInputCols(["document", "posTags", "tokens"]) \\
    ...   .setOutputCol("dependencies")
    ...
    >>> relationPairs = [
    ...   "direction-external_body_part_or_region",
    ...   "external_body_part_or_region-direction",
    ...   "direction-internal_organ_or_component",
    ...   "internal_organ_or_component-direction"
    ... ]
    >>> re_ner_chunk_filter = RENerChunksFilter()\\
    ...   .setInputCols(["ner_chunks", "dependencies"])\\
    ...   .setOutputCol("re_ner_chunks")\\
    ...   .setMaxSyntacticDistance(4)\\
    ...   .setRelationPairs(["internal_organ_or_component-direction"])
    ...
    >>> re_model = RelationExtractionDLModel.pretrained("redl_bodypart_direction_biobert", "en", "clinical/models") \\
    ...     .setInputCols(["re_ner_chunks", "sentences"]) \\
    ...     .setOutputCol("relations") \\
    ...     .setPredictionThreshold(0.5)
    ...
    >>> pipeline = Pipeline(stages=[
    ...     documentAssembler,
    ...     tokenizer,
    ...     embedder,
    ...     posTagger,
    ...     nerTagger,
    ...     nerConverter,
    ...     depencyParser,
    ...     re_ner_chunk_filter ,
    ...     re_model])

    >>> model = pipeline.fit(trainData)
    >>> data = spark.createDataFrame([["MRI demonstrated infarction in the upper brain stem , left cerebellum and  right basil ganglia"]]).toDF("text")
    >>> result = pipeline.fit(data).transform(data)
    ...
    >>> result.selectExpr("explode(relations) as relations")
    ...  .select(
    ...    "relations.metadata.chunk1",
    ...    "relations.metadata.entity1",
    ...    "relations.metadata.chunk2",
    ...    "relations.metadata.entity2",
    ...    "relations.result"
    ...  )
    ...  .where("result != 0")
    ...  .show(truncate=False)
    ...
    ... # Show results
    ... result.selectExpr("explode(relations) as relations") \\
    ...   .select(
    ...      "relations.metadata.chunk1",
    ...      "relations.metadata.entity1",
    ...      "relations.metadata.chunk2",
    ...      "relations.metadata.entity2",
    ...      "relations.result"
    ...   ).where("result != 0") \
    ...   .show(truncate=False)
    +------+---------+-------------+---------------------------+------+
    |chunk1|entity1  |chunk2       |entity2                    |result|
    +------+---------+-------------+---------------------------+------+
    |upper |Direction|brain stem   |Internal_organ_or_component|1     |
    |left  |Direction|cerebellum   |Internal_organ_or_component|1     |
    |right |Direction|basil ganglia|Internal_organ_or_component|1     |
    +------+---------+-------------+---------------------------+------+

    """
    name = "RelationExtractionDLModel"

    predictionThreshold = Param(Params._dummy(), "predictionThreshold",
                                "Minimal activation of the target unit to encode a new relation instance",
                                TypeConverters.toFloat)
    batchSize = Param(Params._dummy(), "batchSize", "Number of relations to process at once", TypeConverters.toInt)

    classes = Param(Params._dummy(), "classes", "Categorization classes", TypeConverters.toListString)
    customLabels = Param(Params._dummy(), "customLabels",
                         "Custom relation labels",
                         TypeConverters.identity)

    def setPredictionThreshold(self, threshold):
        """Sets maximum syntactic distance between a pair of named entities to consider them as a relation

        Parameters
        ----------
        threshold : float
           maximum syntactic distance between a pair of named entities to consider them as a relation
        """
        return self._set(predictionThreshold=threshold)

    # TODO set up this value
    def setCaseSensitive(self, value):
        return self._set(caseSensitive=value)

    def setBatchSize(self, value):
        """Sets number of relations to process at once

        Parameters
        ----------
        value : int
           Number of relations to process at once
        """
        return self._set(batchSize=value)

    def setCustomLabels(self, labels):
        """Sets custom relation labels

        Parameters
        ----------
        labels : dict[str, str]
            Dictionary which maps old to new labels
        """
        self._call_java("setCustomLabels",labels)
        return self

    def getClasses(self):
        """
        Returns labels used to train this model
        """
        return self._call_java("getClasses")

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.re.RelationExtractionDLModel",
                 java_model=None):
        super(RelationExtractionDLModel, self).__init__(
            classname=classname,
            java_model=java_model
        )
        self._setDefault(
            batchSize=10
        )

    @staticmethod
    def loadSavedModel(folder, spark_session):
        jModel = _RelationExtractionDLModelLoader(folder, spark_session._jsparkSession)._java_obj
        return RelationExtractionDLModel(java_model=jModel)

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(RelationExtractionDLModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

