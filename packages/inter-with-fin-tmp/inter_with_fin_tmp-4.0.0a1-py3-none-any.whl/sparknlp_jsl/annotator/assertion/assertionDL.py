from sparknlp.common import *

class AssertionDLApproach(AnnotatorApproach):
    """Train a Assertion Model algorithm using deep learning.
    from extracted entities and text. AssertionLogRegModel requires DOCUMENT, CHUNK and WORD_EMBEDDINGS type
    annotator inputs, which can be obtained by e.g a

    The training data should have annotations columns of type ``DOCUMENT``, ``CHUNK``, ``WORD_EMBEDDINGS``, the ``label`` column
    (The assertion status that you want to predict), the ``start`` (the start index for the term that has the assertion status),
    the ``end`` column (the end index for the term that has the assertion status).This model use a deep learning to predict the entity.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    label
        Column with one label per document. Example of possible values: “present”, “absent”, “hypothetical”, “conditional”, “associated_with_other_person”, etc.
    startCol
        Column that contains the token number for the start of the target
    endCol
        olumn that contains the token number for the end of the target
    batchSize
        Size for each batch in the optimization process
    epochs
        Number of epochs for the optimization process
    learningRate
        Learning rate for the optimization process
    dropout
        dropout", "Dropout at the output of each layer
    maxSentLen
        Max length for an input sentence.
    graphFolder
        Folder path that contain external graph files
    graphFile
        Graph file name to use
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()
    validationSplit
        Choose the proportion of training dataset to be validated against the model on each Epoch. The value should be between 0.0 and 1.0 and by default it is 0.0 and off.
    evaluationLogExtended
       Select if you want to have mode eval.
    testDataset
        Path to test dataset. If set used to calculate statistic on it during training.
    includeConfidence
        whether to include confidence scores in annotation metadata
    enableOutputLogs
        whether or not to output logs
    outputLogsPath
        Folder path to save training logs
    verbose
        Level of verbosity during training
    scopeWindow
        The scope window of the assertion expression
    Examples
    --------
    >>> import sparknlp
    >>> from sparknlp.base import *
    >>> from sparknlp.annotator import *
    >>> from sparknlp_jsl.annotator import *
    >>> from sparknlp.training import *
    >>> from pyspark.ml import Pipeline
    >>> document_assembler = DocumentAssembler() \\
    ...    .setInputCol("text") \\
    ...    .setOutputCol("document")
    >>> sentence_detector = SentenceDetector() \\
    ...    .setInputCol("document") \\
    ...    .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...    .setInputCols(["sentence"]) \\
    ...    .setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...    .setInputCols(["sentence", "token"]) \\
    ...    .setOutputCol("word_embeddings") \\
    ...    .setCaseSensitive(False)
    >>> chunk = Chunker() \\
    ...    .setInputCols([sentence]) \\
    ...    .setChunkCol("chunk") \\
    ...    .setOutputCol("chunk")
    >>> assertion = AssertionDLApproach() \\
    ...    .setLabelCol("label") \\
    ...    .setInputCols(["document", "chunk", "word_embeddings"]) \\
    ...    .setOutputCol("assertion") \\
    ...    .setOutputCol("assertion") \\
    ...    .setBatchSize(128) \\
    ...    .setDropout(0.012) \\
    ...    .setLearningRate(0.015) \\
    ...    .setEpochs(1) \\
    ...    .setStartCol("start") \\
    ...    .setScopeWindow([3, 4]) \\
    ...    .setEndCol("end") \\
    ...    .setMaxSentLen(250)
    >>> assertionPipeline = Pipeline(stages=[
    ...    document_assembler,
    ...    sentence_detector,
    ...    tokenizer,
    ...    embeddings,
    ...    chunk,
    ...    assertion])
    >>> assertionModel = assertionPipeline.fit(dataset)
    """

    label = Param(Params._dummy(), "label", "Column with one label per document", typeConverter=TypeConverters.toString)

    startCol = Param(Params._dummy(), "startCol", "Column that contains the token number for the start of the target",
                     typeConverter=TypeConverters.toString)
    endCol = Param(Params._dummy(), "endCol", "Column that contains the token number for the end of the target",
                   typeConverter=TypeConverters.toString)

    batchSize = Param(Params._dummy(), "batchSize", "Size for each batch in the optimization process",
                      TypeConverters.toInt)
    epochs = Param(Params._dummy(), "epochs", "Number of epochs for the optimization process", TypeConverters.toInt)

    learningRate = Param(Params._dummy(), "learningRate", "Learning rate for the optimization process",
                         TypeConverters.toFloat)
    dropout = Param(Params._dummy(), "dropout", "Dropout at the output of each layer", TypeConverters.toFloat)

    maxSentLen = Param(Params._dummy(), "maxSentLen", "Max length for an input sentence.", TypeConverters.toInt)

    graphFolder = Param(Params._dummy(), "graphFolder", "Folder path that contain external graph files",
                        TypeConverters.toString)
    graphFile = Param(Params._dummy(), "graphFile",
                      "Path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.",
                      TypeConverters.toString)
    configProtoBytes = Param(Params._dummy(), "configProtoBytes",
                             "ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()",
                             TypeConverters.toListString)

    validationSplit = Param(Params._dummy(), "validationSplit",
                            "Choose the proportion of training dataset to be validated against the model on each Epoch. The value should be between 0.0 and 1.0 and by default it is 0.0 and off.",
                            TypeConverters.toFloat)

    evaluationLogExtended = Param(Params._dummy(), "evaluationLogExtended",
                                  "",
                                  TypeConverters.toBoolean)

    testDataset = Param(Params._dummy(), "testDataset",
                        "Path to test dataset. If set used to calculate statistic on it during training.",
                        TypeConverters.identity)

    includeConfidence = Param(Params._dummy(), "includeConfidence",
                              "whether to include confidence scores in annotation metadata",
                              TypeConverters.toBoolean)

    enableOutputLogs = Param(Params._dummy(), "enableOutputLogs",
                             "whether or not to output logs",
                             typeConverter=TypeConverters.toBoolean)

    outputLogsPath = Param(Params._dummy(), "outputLogsPath", "Folder path to save training logs",
                           TypeConverters.toString)

    verbose = Param(Params._dummy(), "verbose", "Level of verbosity during training",
                    TypeConverters.toInt)

    scopeWindow = Param(Params._dummy(), "scopeWindow", "The scope window of the assertion expression",
                        TypeConverters.toListInt)

    def setGraphFolder(self, p):
        """Sets folder path that contain external graph files.

        Parameters
        ----------
        p : srt
            Folder path that contain external graph files.
        """
        return self._set(graphFolder=p)

    def setGraphFile(self, value):
        """Sets path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.

        Parameters
        ----------
        value : str
            Path that contains the external graph file. When specified, the provided file will be used, and no graph search will happen.
        """
        return self._set(graphFile=value)

    def setConfigProtoBytes(self, b):
        """Sets  ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()`.

        Parameters
        ----------
        b : bytes
           ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()
        """
        return self._set(configProtoBytes=b)

    def setLabelCol(self, label):
        """Set a column with one label per document. Example of possible values: “present”, “absent”, “hypothetical”, “conditional”, “associated_with_other_person”, etc.

        Parameters
        ----------
        label : str
            label. Column with one label per document. Example of possible values: “present”, “absent”, “hypothetical”, “conditional”, “associated_with_other_person”, etc.

        """
        return self._set(label=label)

    def setStartCol(self, s):
        """Set a column that contains the token number for the start of the target

        Parameters
        ----------
        s : str
           Column that contains the token number for the start of the target

        """
        return self._set(startCol=s)

    def setEndCol(self, e):
        """Set column that contains the token number for the end of the target.

        Parameters
        ----------
        row : str
            Column that contains the token number for the end of the target
        """
        return self._set(endCol=e)

    def setBatchSize(self, size):
        """Set Size for each batch in the optimization process.

        Parameters
        ----------
        size : int
            Size for each batch in the optimization process

        """
        return self._set(batchSize=size)

    def setEpochs(self, number):
        """Sets number of epochs for the optimization process

        Parameters
        ----------
        number : int
           Number of epochs for the optimization process

        """
        return self._set(epochs=number)

    def setLearningRate(self, lamda):
        """Set a learning rate for the optimization process

        Parameters
        ----------
        lamda : float
            Learning rate for the optimization process.

        Returns
        -------
        Annotation
            The new Annotation.
        """
        return self._set(learningRate=lamda)

    def setDropout(self, rate):
        """Set a dropout at the output of each layer

        Parameters
        ----------
        rate : float
           Dropout at the output of each layer

        """
        return self._set(dropout=rate)

    def setMaxSentLen(self, length):
        """Set the max length for an input sentence.

        Parameters
        ----------
        length : int
            Max length for an input sentence.
        """
        return self._set(maxSentLen=length)

    def setValidationSplit(self, v):
        """Set Choose the proportion of training dataset to be validated against the model on each Epoch.
            The value should be between 0.0 and 1.0 and by default it is 0.0 and off.

        Parameters
        ----------
        v : float
            Choose the proportion of training dataset to be validated against the model on each Epoch.
            The value should be between 0.0 and 1.0 and by default it is 0.0 and off.

        """
        self._set(validationSplit=v)
        return self

    def setEvaluationLogExtended(self, v):
        """Creates a Annotation from a Spark `Row`.

        Parameters
        ----------
        v : bool
            Evaluation log extended.
        """
        self._set(evaluationLogExtended=v)
        return self

    def setTestDataset(self, path, read_as=ReadAs.SPARK, options=None):
        """Sets path to test dataset. If set used to calculate statistic on it during training.

        Parameters
        ----------
        path : srt
            Path to test dataset. If set used to calculate statistic on it during training.
        """
        if options is None:
            options = {"format": "parquet"}
        return self._set(testDataset=ExternalResource(path, read_as, options.copy()))

    def setIncludeConfidence(self, value):
        """Sets if you waht to include confidence scores in annotation metadata.

            Parameters
            ----------
            p : bool
            Value that selects if you want to use confidence scores in annotation metadata
        """
        return self._set(includeConfidence=value)

    def setEnableOutputLogs(self, value):
        """Sets if you enable to output to annotators log folder.

        Parameters
        ----------
        value : srt
            Folder path that contain external graph files.
        """

        return self._set(enableOutputLogs=value)

    def setOutputLogsPath(self, value):
        """Sets folder path that contain external graph files.

        Parameters
        ----------
        value : srt
                Folder path that contain external graph files.
        """
        return self._set(outputLogsPath=value)

    def setVerbose(self, value):
        """Sets level of verbosity during training.

        Parameters
        ----------
        value : int
            Level of verbosity during training.
        """
        return self._set(verbose=value)

    def setScopeWindow(self, value):
        """Sets the scope of the window of the assertion expression

        Parameters
        ----------
        value : [int, int]
            Left and right offset if the scope window. Offsets must be non-negative values
        """
        assert(type(value) is list)
        assert(len(value) == 2)

        return self._set(scopeWindow=value)

    def _create_model(self, java_model):
        return AssertionDLModel(java_model=java_model)

    @keyword_only
    def __init__(self):
        super(AssertionDLApproach, self).__init__(
            classname="com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLApproach")
        self._setDefault(label="label", batchSize=64, epochs=5, learningRate=0.0012, dropout=0.05, maxSentLen=250,
                         includeConfidence=False, scopeWindow=[-1, -1])


class AssertionDLModel(AnnotatorModel, HasStorageRef):
    """AssertionDL is a deep Learning based approach used to extract Assertion Status
    from extracted entities and text. AssertionDLModel requires DOCUMENT, CHUNK and WORD_EMBEDDINGS type
    annotator inputs, which can be obtained by e.g a


    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``DOCUMENT, CHUNK, WORD_EMBEDDINGS``      ``ASSERTION``
    ========================================= ======================

    Parameters
    ----------
    maxSentLen
        Max length for an input sentence.
    targetNerLabels
        List of NER labels to mark as target for assertion, must match NER output.
    configProtoBytes
        ConfigProto from tensorflow, serialized into byte array.
    classes
        Tags used to trained this AssertionDLModel
    scopeWindow
        The scope window of the assertion expression
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
    >>> data = spark.createDataFrame([["Patient with severe fever and sore throat"],["Patient shows no stomach pain"],["She was maintained on an epidural and PCA for pain control."]]).toDF("text")
    >>> documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    >>> sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    >>> tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
    >>> embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models") \\
    ...  .setOutputCol("embeddings")
    >>> nerModel = MedicalNerModel.pretrained("ner_clinical", "en", "clinical/models") \\
    ...  .setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    >>> nerConverter = NerConverter().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")
    >>> clinicalAssertion = AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models") \\
    ...  .setInputCols(["sentence", "ner_chunk", "embeddings"]) \\
    ...  .setOutputCol("assertion")
    >>> assertionPipeline = Pipeline(stages=[
    ...  documentAssembler,
    ...  sentenceDetector,
    ...  tokenizer,
    ...  embeddings,
    ...  nerModel,
    ...  nerConverter,
    ...  clinicalAssertion
    ... ])

    >>> assertionModel = assertionPipeline.fit(data)


    >>> result = assertionModel.transform(data)
    >>> result.selectExpr("ner_chunk.result as ner", "assertion.result").show(3, truncate=False)
    +--------------------------------+--------------------------------+
    |ner                             |result                          |
    +--------------------------------+--------------------------------+
    |[severe fever, sore throat]     |[present, present]              |
    |[stomach pain]                  |[absent]                        |
    |[an epidural, PCA, pain control]|[present, present, hypothetical]|
    +--------------------------------+--------------------------------+



    """
    name = "AssertionDLModel"

    maxSentLen = Param(Params._dummy(), "maxSentLen", "Max length for an input sentence.", TypeConverters.toInt)
    targetNerLabels = Param(Params._dummy(), "targetNerLabels",
                            "List of NER labels to mark as target for assertion, must match NER output",
                            typeConverter=TypeConverters.toListString)
    configProtoBytes = Param(Params._dummy(), "configProtoBytes",
                             "ConfigProto from tensorflow, serialized into byte array. Get with config_proto.SerializeToString()",
                             TypeConverters.toListString)

    classes = Param(Params._dummy(), "classes",
                    "get the tags used to trained this AssertionDLModel",
                    TypeConverters.toListString)

    scopeWindow = Param(Params._dummy(), "scopeWindow", "The scope window of the assertion expression",
                        TypeConverters.toListInt)

    includeConfidence = Param(Params._dummy(), "includeConfidence",
                              "whether to include confidence scores in annotation metadata",
                              TypeConverters.toBoolean)

    def setConfigProtoBytes(self, b):
        return self._set(configProtoBytes=b)


    def setIncludeConfidence(self, value):
        """Sets if you waht to include confidence scores in annotation metadata.

            Parameters
            ----------
            p : bool
            Value that selects if you want to use confidence scores in annotation metadata
        """
        return self._set(includeConfidence=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLModel", java_model=None):
        super(AssertionDLModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    def setScopeWindow(self, value):
        """Sets the scope of the window of the assertion expression

        Parameters
        ----------
        value : [int, int]
            Left and right offset if the scope window. Offsets must be non-negative values
        """
        assert (type(value) is list)
        assert (len(value) == 2)
        assert (value[0] >= 0)
        assert (value[1] >= 0)

        return self._set(scopeWindow=value)

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(AssertionDLModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

