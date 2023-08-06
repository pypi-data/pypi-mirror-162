from sparknlp.common import *

class SentenceResolverParams(HasCaseSensitiveProperties):
    """
    Class used to have a common interface Sentence Resolver family.


    Parameters
    ----------
    distanceFunction
        What distance function to use for WMD: 'EUCLIDEAN' or 'COSINE'.
    neighbours
        Number of neighbours to consider in the KNN query to calculate WMD
    threshold
        Threshold value for the last distance calculated.
    confidenceFunction
        What function to use to calculate confidence: INVERSE or SOFTMAX.
    missAsEmpty
        Whether or not to return an empty annotation on unmatched chunks.

    """

    distanceFunction = Param(Params._dummy(), "distanceFunction",
                             "What distance function to use for WMD: 'EUCLIDEAN' or 'COSINE'", TypeConverters.toString)
    neighbours = Param(Params._dummy(), "neighbours",
                       "Number of neighbours to consider in the KNN query to calculate WMD", TypeConverters.toInt)
    threshold = Param(Params._dummy(), "threshold", "Threshold value for the last distance calculated",
                      TypeConverters.toFloat)
    confidenceFunction = Param(Params._dummy(), "confidenceFunction",
                               "what function to use to calculate confidence: INVERSE or SOFTMAX",
                               typeConverter=TypeConverters.toString)
    missAsEmpty = Param(Params._dummy(), "missAsEmpty",
                        "whether or not to return an empty annotation on unmatched chunks",
                        typeConverter=TypeConverters.toBoolean)

    def setDistanceFunction(self, dist):
        """Sets distance function to use for WMD: 'EUCLIDEAN' or 'COSINE'.

        Parameters
        ----------
        dist : str
            Value that selects what distance function to use for WMD: 'EUCLIDEAN' or 'COSINE'.
        """
        return self._set(distanceFunction=dist)

    def setNeighbours(self, k):
        """Sets number of neighbours to consider in the KNN query to calculate WMD.

        Parameters
        ----------
        k : int
            Number of neighbours to consider in the KNN query to calculate WMD.
        """
        return self._set(neighbours=k)

    def setThreshold(self, thres):
        """Sets Threshold value for the last distance calculated.

        Parameters
        ----------
        thres : float
            Threshold value for the last distance calculated.
        """
        return self._set(threshold=thres)

    def setConfidenceFunction(self, s):
        """What function to use to calculate confidence: INVERSE or SOFTMAX.

        Parameters
        ----------
        s : str
            What function to use to calculate confidence: INVERSE or SOFTMAX.
        """
        return self._set(confidenceFunction=s)

    def setMissAsEmpty(self, value):
        """Sets whether or not to return an empty annotation on unmatched chunks.

        Parameters
        ----------
        value : bool
            whether or not to return an empty annotation on unmatched chunks.
        """
        return self._set(missAsEmpty=value)


class SentenceEntityResolverApproach(AnnotatorApproach, SentenceResolverParams):
    """Thius class contains all the parameters and methods to train a SentenceEntityResolverModel.
       The model transforms a dataset with Input Annotation type SENTENCE_EMBEDDINGS, coming from e.g.
       [BertSentenceEmbeddings](/docs/en/transformers#bertsentenceembeddings)
       and returns the normalized entity for a particular trained ontology / curated dataset.
       (e.g. ICD-10, RxNorm, SNOMED etc.)

       ========================================= ======================
       Input Annotation types                    Output Annotation type
       ========================================= ======================
       ``SENTENCE_EMBEDDINGS``                    ``ENTITY``
       ========================================= ======================

       Parameters
       ----------
       labelCol
            Column name for the value we are trying to resolve
       normalizedCol
            Column name for the original, normalized description
       pretrainedModelPath
            Path to an already trained SentenceEntityResolverModel, which is used as a starting point for training the new model.
       overrideExistingCodes
            Whether to override the existing codes with new data while continue the training from a pretrained model. Default value is false(keep all the codes).
       returnCosineDistances
            Extract Cosine Distances. TRUE or False
       aux_label_col
            Auxiliary label which maps resolved entities to additional labels
       useAuxLabel
            Use AuxLabel Col or not
       overrideExistingCodes
            Whether to override the codes present in a pretrained model with new codes when the training process begins with a pretrained model
       dropCodesList
            A list of codes in a pretrained model that will be omitted when the training process begins with a pretrained model


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
       >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
       >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
       >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
       >>> bertEmbeddings = BertSentenceEmbeddings.pretrained("sent_biobert_pubmed_base_cased") \\
       ...  .setInputCols(["sentence"]) \\
       ...  .setOutputCol("embeddings")
       >>> snomedTrainingPipeline = Pipeline(stages=[
       ...  documentAssembler,
       ...  sentenceDetector,
       ...  bertEmbeddings,
       ... ])
       >>> snomedTrainingModel = snomedTrainingPipeline.fit(data)
       >>> snomedData = snomedTrainingModel.transform(data).cache()
       >>> assertionModel = assertionPipeline.fit(data)
       >>> assertionModel = assertionPipeline.fit(data)

       >>> bertExtractor = SentenceEntityResolverApproach() \\
       ...   .setNeighbours(25) \\
       ...   .setThreshold(1000) \\
       ...   .setInputCols(["bert_embeddings"]) \\
       ...   .setNormalizedCol("normalized_text") \\
       ...   .setLabelCol("label") \\
       ...   .setOutputCol("snomed_code") \\
       ...   .setDistanceFunction("EUCLIDIAN") \\
       ...   .setCaseSensitive(False)

       >>> snomedModel = bertExtractor.fit(snomedData)
       """
    labelCol = Param(Params._dummy(), "labelCol", "Column name for the value we are trying to resolve",
                     typeConverter=TypeConverters.toString)
    normalizedCol = Param(Params._dummy(), "normalizedCol", "Column name for the original, normalized description",
                          typeConverter=TypeConverters.toString)

    pretrainedModelPath = Param(Params._dummy(), "pretrainedModelPath",
                                "Path to an already trained SentenceEntityResolverModel, which is used as a starting point for training the new model.",
                                typeConverter=TypeConverters.toString)

    overrideExistingCodes = Param(Params._dummy(), "overrideExistingCodes",
                                  "Whether to override the existing codes with new data while continue the training from a pretrained model. Default value is false(keep all the codes).",
                                  typeConverter=TypeConverters.toBoolean)

    dropCodesList = Param(Params._dummy(), "dropCodesList",
                          "List of codes in a pretrained model to leave out when continue training with new data.",
                          typeConverter=TypeConverters.toListString)

    returnCosineDistances = Param(Params._dummy(), "returnCosineDistances",
                                  "Extract Cosine Distances. TRUE or False",
                                  typeConverter=TypeConverters.toBoolean)
    aux_label_col = Param(Params._dummy(), "aux_label_col",
                          "Auxiliary label which maps resolved entities to additional labels",
                          typeConverter=TypeConverters.toString)

    useAuxLabel = Param(Params._dummy(), "useAuxLabel",
                        "Use AuxLabel Col or not",
                        typeConverter=TypeConverters.toBoolean)

    def setUseAuxLabel(self, name):
        """Sets Use AuxLabel Col or not.

        Parameters
        ----------
        name : bool
            Use AuxLabel Col or not.
        """
        return self._set(useAuxLabel=name)

    def setAuxLabelCol(self, name):
        """Sets auxiliary label which maps resolved entities to additional labels

        Parameters
        ----------
        name : str
            Auxiliary label which maps resolved entities to additional labels
        """
        return self._set(aux_label_col=name)

    def setExtractCosineDistances(self, name):
        """Extract Cosine Distances. TRUE or False.

        Parameters
        ----------
        name : bool
            Extract Cosine Distances. TRUE or False
        """
        return self._set(returnCosineDistances=name)

    def setLabelCol(self, name):
        """Sets column name for the value we are trying to resolve

        Parameters
        ----------
        s : bool
            Column name for the value we are trying to resolve
        """
        return self._set(labelCol=name)

    def setNormalizedCol(self, name):
        """Sets column name for the original, normalized description

        Parameters
        ----------
        s : bool
            Column name for the original, normalized description
        """
        return self._set(normalizedCol=name)

    def setPretrainedModelPath(self, path):
        return self._set(pretrainedModelPath=path)

    def setOverrideExistingCodes(self, value):
        return self._set(overrideExistingCodes=value)

    def setDropCodesList(self, value):
        return self._set(dropCodesList=value)

    def _create_model(self, java_model):
        return SentenceEntityResolverModel(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(SentenceEntityResolverApproach, self).__init__(
            classname="com.johnsnowlabs.nlp.annotators.resolution.SentenceEntityResolverApproach")
        self._setDefault(labelCol="code", normalizedCol="code", distanceFunction="EUCLIDEAN", neighbours=500,
                         threshold=5, missAsEmpty=True, returnCosineDistances=True)


class SentenceEntityResolverModel(AnnotatorModel, HasEmbeddingsProperties, HasStorageModel, SentenceResolverParams):
    """Thius class contains all the parameters and methods to train a SentenceEntityResolverModel.
       The model transforms a dataset with Input Annotation type SENTENCE_EMBEDDINGS, coming from e.g.
       [BertSentenceEmbeddings](/docs/en/transformers#bertsentenceembeddings)
       and returns the normalized entity for a particular trained ontology / curated dataset.
       (e.g. ICD-10, RxNorm, SNOMED etc.)

       ========================================= ======================
       Input Annotation types                    Output Annotation type
       ========================================= ======================
       ``SENTENCE_EMBEDDINGS``                   ``ENTITY``
       ========================================= ======================

       Parameters
       ----------
       returnCosineDistances
            Extract Cosine Distances. TRUE or False
       aux_label_col
            Auxiliary label which maps resolved entities to additional labels
       useAuxLabel
            Use AuxLabel Col or not

       searchTree
            Search tree for resolution

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
       >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
       >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
       >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
       >>> bertEmbeddings = BertSentenceEmbeddings.pretrained("sent_biobert_pubmed_base_cased") \\
       ...  .setInputCols(["sentence"]) \\
       ...  .setOutputCol("embeddings")
       >>> snomedTrainingPipeline = Pipeline(stages=[
       ...  documentAssembler,
       ...  sentenceDetector,
       ...  bertEmbeddings,
       ... ])
       >>> snomedTrainingModel = snomedTrainingPipeline.fit(data)
       >>> snomedData = snomedTrainingModel.transform(data).cache()
       >>> assertionModel = assertionPipeline.fit(data)
       >>> assertionModel = assertionPipeline.fit(data)

       >>> bertExtractor = SentenceEntityResolverApproach() \\
       ...   .setNeighbours(25) \\
       ...   .setThreshold(1000) \\
       ...   .setInputCols(["bert_embeddings"]) \\
       ...   .setNormalizedCol("normalized_text") \\
       ...   .setLabelCol("label") \\
       ...   .setOutputCol("snomed_code") \\
       ...   .setDistanceFunction("EUCLIDIAN") \\
       ...   .setCaseSensitive(False)

       >>> snomedModel = bertExtractor.fit(snomedData)
       """
    name = "SentenceEntityResolverModel"
    returnCosineDistances = Param(Params._dummy(), "returnCosineDistances",
                                  "Extract Cosine Distances. TRUE or False",
                                  typeConverter=TypeConverters.toBoolean)
    aux_label_col = Param(Params._dummy(), "aux_label_col",
                          "Auxiliary label which maps resolved entities to additional labels",
                          typeConverter=TypeConverters.toString)

    useAuxLabel = Param(Params._dummy(), "useAuxLabel",
                        "Use AuxLabel Col or not",
                        typeConverter=TypeConverters.toBoolean)
    searchTree = Param(Params._dummy(), "searchTree", "Search tree for resolution", TypeConverters.identity)

    ##TODO add SetreturnCosineDistances.

    def setUseAuxLabel(self, name):
        """Sets Use AuxLabel Col or not.

        Parameters
        ----------
        name : bool
            Use AuxLabel Col or not.
        """
        return self._set(useAuxLabel=name)

    def setAuxLabelCol(self, name):
        """Sets auxiliary label which maps resolved entities to additional labels

        Parameters
        ----------
        name : str
            Auxiliary label which maps resolved entities to additional labels
        """
        return self._set(aux_label_col=name)

    def setSearchTree(self, s):
        """Sets auxiliary label which maps resolved entities to additional labels

        Parameters
        ----------
        name : str
            Auxiliary label which maps resolved entities to additional labels
        """
        return self._set(searchTree=s)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.resolution.SentenceEntityResolverModel",
                 java_model=None):
        super(SentenceEntityResolverModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(SentenceEntityResolverModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

