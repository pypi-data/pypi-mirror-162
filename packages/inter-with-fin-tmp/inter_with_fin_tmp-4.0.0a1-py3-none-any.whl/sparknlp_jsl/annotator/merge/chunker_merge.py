from sparknlp.common import *

class ChunkMergeApproach(AnnotatorApproach):
    """
    Merges two chunk columns coming from two annotators(NER, ContextualParser or any other annotator producing
    chunks). The merger of the two chunk columns is made by selecting one chunk from one of the columns according
    to certain criteria.
    The decision on which chunk to select is made according to the chunk indices in the source document.
    (chunks with longer lengths and highest information will be kept from each source)
    Labels can be changed by setReplaceDictResource.

    =========================== ======================
    Input Annotation types      Output Annotation type
    =========================== ======================
    ``CHUNK,CHUNK``               ``CHUNK``
    =========================== ======================

    Parameters
    ----------
    mergeOverlapping
        whether to merge overlapping matched chunks. Defaults false
    falsePositivesResource
        file with false positive pairs
    replaceDictResource
        replace dictionary pairs
    chunkPrecedence
        Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]
    blackList
        If defined, list of entities to ignore. The rest will be proccessed.

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
    Define a pipeline with 2 different NER models with a ChunkMergeApproach at the end
    >>> data = spark.createDataFrame([["A 63-year-old man presents to the hospital ..."]]).toDF("text")
    >>> pipeline = Pipeline(stages=[
    ...  DocumentAssembler().setInputCol("text").setOutputCol("document"),
    ...  SentenceDetector().setInputCols(["document"]).setOutputCol("sentence"),
    ...  Tokenizer().setInputCols(["sentence"]).setOutputCol("token"),
    ...   WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models").setOutputCol("embs"),
    ...   MedicalNerModel.pretrained("ner_jsl", "en", "clinical/models") \\
    ...     .setInputCols(["sentence", "token", "embs"]).setOutputCol("jsl_ner"),
    ...  NerConverter().setInputCols(["sentence", "token", "jsl_ner"]).setOutputCol("jsl_ner_chunk"),
    ...   MedicalNerModel.pretrained("ner_bionlp", "en", "clinical/models") \\
    ...     .setInputCols(["sentence", "token", "embs"]).setOutputCol("bionlp_ner"),
    ...  NerConverter().setInputCols(["sentence", "token", "bionlp_ner"]) \\
    ...     .setOutputCol("bionlp_ner_chunk"),
    ...  ChunkMergeApproach().setInputCols(["jsl_ner_chunk", "bionlp_ner_chunk"]).setOutputCol("merged_chunk")
    >>> ])
    >>> result = pipeline.fit(data).transform(data).cache()
    >>> result.selectExpr("explode(merged_chunk) as a") \\
    ...   .selectExpr("a.begin","a.end","a.result as chunk","a.metadata.entity as entity") \\
    ...   .show(5, False)
    +-----+---+-----------+---------+
    |begin|end|chunk      |entity   |
    +-----+---+-----------+---------+
    |5    |15 |63-year-old|Age      |
    |17   |19 |man        |Gender   |
    |64   |72 |recurrent  |Modifier |
    |98   |107|cellulitis |Diagnosis|
    |110  |119|pneumonias |Diagnosis|
    +-----+---+-----------+---------+
    """
    name = "ChunkMergeApproach"

    mergeOverlapping = Param(Params._dummy(),
                             "mergeOverlapping",
                             "whether to merge overlapping matched chunks. Defaults false",
                             typeConverter=TypeConverters.toBoolean)

    falsePositivesResource = Param(Params._dummy(),
                                   "falsePositivesResource",
                                   "file with false positive pairs",
                                   typeConverter=TypeConverters.identity)

    replaceDictResource = Param(Params._dummy(),
                                "replaceDictResource",
                                "replace dictionary pairs",
                                typeConverter=TypeConverters.identity)

    chunkPrecedence = Param(Params._dummy(),
                            "chunkPrecedence",
                            "Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]",
                            typeConverter=TypeConverters.toString)
    blackList = Param(Params._dummy(), "blackList",
                      "If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels",
                      TypeConverters.toListString)

    def setMergeOverlapping(self, b):
        """Sets whether to merge overlapping matched chunks. Defaults false

        Parameters
        ----------
        b : bool
            whether to merge overlapping matched chunks. Defaults false

        """
        return self._set(mergeOverlapping=b)

    def setFalsePositivesResource(self, path, read_as=ReadAs.TEXT, options=None):
        """Sets file with false positive pairs

        Parameters
        ----------
        path : str
            Path to the external resource
        read_as : str, optional
            How to read the resource, by default ReadAs.TEXT
        options : dict, optional
            Options for reading the resource, by default {"format": "text"}

        """
        if options is None:
            options = {"delimiter": "\t"}
        return self._set(falsePositivesResource=ExternalResource(path, read_as, options))


    def setReplaceDictResource(self, path, read_as=ReadAs.TEXT, options={"delimiter": ","}):
        """Sets replace dictionary pairs

        Parameters
        ----------
        path : str
            Path to the external resource

        read_as : str, optional
            How to read the resource, by default ReadAs.TEXT
        options : dict, optional
            Options for reading the resource, by default {"format": "text"}
        """

        return self._set(replaceDictResource=ExternalResource(path, read_as, options))

    def setChunkPrecedence(self, b):
        """Sets what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]

        Parameters
        ----------
        b : str
            Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]

        """
        return self._set(chunkPrecedence=b)

    def setBlackList(self, entities):
        """If defined, list of entities to ignore. The rest will be processed.

        Parameters
        ----------
        entities : list
           If defined, list of entities to ignore. The rest will be processed.
        """
        return self._set(blackList=entities)

    @keyword_only
    def __init__(self):
        super(ChunkMergeApproach, self).__init__(classname="com.johnsnowlabs.nlp.annotators.merge.ChunkMergeApproach")

    def _create_model(self, java_model):
        return ChunkMergeModel(java_model=java_model)


class ChunkMergeModel(AnnotatorModel):
    """
    The model produced by ChunkMergerAproach.

    =========================== ======================
    Input Annotation types      Output Annotation type
    =========================== ======================
    ``CHUNK,CHUNK``             ``CHUNK``
    =========================== ======================

    Parameters
    ----------

    mergeOverlapping
        whether to merge overlapping matched chunks. Defaults false
    chunkPrecedence
        Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]
    blackList
        If defined, list of entities to ignore. The rest will be proccessed.
    """
    name = "ChunkMergeModel"

    mergeOverlapping = Param(Params._dummy(),
                             "mergeOverlapping",
                             "whether to merge overlapping matched chunks. Defaults false",
                             typeConverter=TypeConverters.toBoolean)

    falsePositives = Param(Params._dummy(), "falsePositives", "list of false positive tuples (text, entity)",
                           typeConverter=TypeConverters.identity)
    replaceDict = Param(Params._dummy(), "replaceDict", "dictionary of entities to replace",
                        typeConverter=TypeConverters.identity)

    chunkPrecedence = Param(Params._dummy(),
                            "chunkPrecedence",
                            "Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]",
                            typeConverter=TypeConverters.toString)
    blackList = Param(Params._dummy(), "blackList",
                      "If defined, list of entities to ignore. The rest will be processed. Do not include IOB prefix on labels",
                      TypeConverters.toListString)

    def setMergeOverlapping(self, b):
        """Sets whether to merge overlapping matched chunks. Defaults false

        Parameters
        ----------
        v : bool
            Whether to merge overlapping matched chunks. Defaults false

        """
        return self._set(mergeOverlapping=b)

    def setChunkPrecedence(self, b):
        """Sets what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]

        Parameters
        ----------
        b : str
            Select what is the precedence when two chunks have the same start and end indices. Possible values are [entity|identifier|field]

        """
        return self._set(chunkPrecedence=b)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.merge.ChunkMergeModel",
                 java_model=None):
        super(ChunkMergeModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(ChunkMergeModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

