from sparknlp.common import *

class GenericClassifierApproach(AnnotatorApproach):
    """
    Trains a TensorFlow model for generic classification of feature vectors. It takes FEATURE_VECTOR annotations from
    FeaturesAssembler` as input, classifies them and outputs CATEGORY annotations.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``FEATURE_VECTOR``                        ``CATEGORY``
    ========================================= ======================

    Parameters
    ----------

    labelColumn
        Column with one label per document
    batchSize
        Size for each batch in the optimization process
    epochsN
        Number of epochs for the optimization process
    learningRate
        Learning rate for the optimization proces
    dropou
        Dropout at the output of each laye
    validationSplit
        Validaiton split - how much data to use for validation
    modelFile
        File name to load the mode from
    fixImbalance
        A flag indicating whenther to balance the trainig set
    featureScaling
        Feature scaling method. Possible values are 'zscore', 'minmax' or empty (no scaling)
    outputLogsPath
        Path to folder where logs will be saved. If no path is specified, no logs are generated

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
    >>> features_asm = FeaturesAssembler() \
    ...    .setInputCols(["feature_1", "feature_2", "...", "feature_n"]) \
    ...    .setOutputCol("features")
    ...
    >>> gen_clf = GenericClassifierApproach() \\
    ...    .setLabelColumn("target") \\
    ...    .setInputCols(["features"]) \\
    ...    .setOutputCol("prediction") \\
    ...    .setModelFile("/path/to/graph_file.pb") \\
    ...    .setEpochsNumber(50) \\
    ...    .setBatchSize(100) \\
    ...    .setFeatureScaling("zscore") \\
    ...    .setlearningRate(0.001) \\
    ...    .setFixImbalance(True) \\
    ...    .setOutputLogsPath("logs") \\
    ...    .setValidationSplit(0.2) # keep 20% of the data for validation purposes
    ...
    >>> pipeline = Pipeline().setStages([
    ...    features_asm,
    ...    gen_clf
    ...])
    ...
    >>> clf_model = pipeline.fit(data)

    """

    labelColumn = Param(Params._dummy(), "labelColumn", "Column with one label per document",
                        typeConverter=TypeConverters.toString)

    batchSize = Param(Params._dummy(), "batchSize", "Size for each batch in the optimization process",
                      TypeConverters.toInt)
    epochsN = Param(Params._dummy(), "epochsN", "Number of epochs for the optimization process", TypeConverters.toInt)
    learningRate = Param(Params._dummy(), "learningRate", "Learning rate for the optimization process",
                         TypeConverters.toFloat)
    dropout = Param(Params._dummy(), "dropout", "Dropout at the output of each layer", TypeConverters.toFloat)
    validationSplit = Param(Params._dummy(), "validationSplit",
                            "Validaiton split - how much data to use for validation", TypeConverters.toFloat)

    modelFile = Param(Params._dummy(), "modelFile", "File name to load the mode from", TypeConverters.toString)

    fixImbalance = Param(Params._dummy(), "fixImbalance",
                         "A flag indicating whenther to balance the trainig set", TypeConverters.toBoolean)

    featureScaling = Param(Params._dummy(), "featureScaling",
                           "Feature scaling method. Possible values are 'zscore', 'minmax' or empty (no scaling)",
                           TypeConverters.toString)

    outputLogsPath = Param(Params._dummy(), "outputLogsPath",
                           "Path to folder where logs will be saved. If no path is specified, no logs are generated",
                           TypeConverters.toString)

    def setLabelCol(self, label_column):
        """Sets  Size for each batch in the optimization process

        Parameters
        ----------
        label : str
            Column with the value result we are trying to predict.

        """
        return self._set(labelColumn=label_column)

    def setBatchSize(self, size):
        """Size for each batch in the optimization process

        Parameters
        ----------
        size : int
             Size for each batch in the optimization process

        """
        return self._set(batchSize=size)

    def setEpochsNumber(self, epochs):
        """Sets number of epochs for the optimization process

        Parameters
        ----------
        epochs : int
            Number of epochs for the optimization process

        """
        return self._set(epochsN=epochs)

    def setLearningRate(self, lamda):
        """Sets learning rate for the optimization process

        Parameters
        ----------
        lamda : float
            Learning rate for the optimization process

        """
        return self._set(learningRate=lamda)

    def setDropout(self, dropout):
        """Sets drouptup

        Parameters
        ----------
        dropout : float
             Dropout at the output of each layer

        """
        return self._set(dropout=dropout)

    def setValidationSplit(self, validation_split):
        """Sets validaiton split - how much data to use for validation

        Parameters
        ----------
        validation_split : float
            Validaiton split - how much data to use for validation

        """
        return self._set(validationSplit=validation_split)

    def setModelFile(self, mode_file):
        """Sets file name to load the mode from"

        Parameters
        ----------
        label : str
            File name to load the mode from"

        """
        return self._set(modelFile=mode_file)

    def setFixImbalance(self, fix_imbalance):
        """Sets A flag indicating whenther to balance the trainig set.

        Parameters
        ----------
        fix_imbalance : bool
            A flag indicating whenther to balance the trainig set.

        """
        return self._set(fixImbalance=fix_imbalance)

    def setFeatureScaling(self, feature_scaling):
        """Sets Feature scaling method. Possible values are 'zscore', 'minmax' or empty (no scaling

        Parameters
        ----------
        feature_scaling : str
            Feature scaling method. Possible values are 'zscore', 'minmax' or empty (no scaling

        """
        return self._set(featureScaling=feature_scaling)

    def setOutputLogsPath(self, output_logs_path):
        """Sets path to folder where logs will be saved. If no path is specified, no logs are generated

        Parameters
        ----------
        label : str
            Path to folder where logs will be saved. If no path is specified, no logs are generated

        """
        return self._set(outputLogsPath=output_logs_path)

    def _create_model(self, java_model):
        return GenericClassifierModel(java_model=java_model)

    @keyword_only
    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.generic_classifier.GenericClassifierApproach"):
        super(GenericClassifierApproach, self).__init__(classname=classname)
        self._setDefault(
            labelColumn="label",
            batchSize=32,
            epochsN=10,
            learningRate=0.001,
            dropout=0.05,
            fixImbalance=False,
            featureScaling="",
            outputLogsPath=""
        )


class GenericClassifierModel(AnnotatorModel):
    """
    Generic classifier of feature vectors. It takes FEATURE_VECTOR annotations from
    FeaturesAssembler` as input, classifies them and outputs CATEGORY annotations.

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``FEATURE_VECTOR``                        ``CATEGORY``
    ========================================= ======================

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
    >>> features_asm = FeaturesAssembler() \\
    ...    .setInputCols(["feature_1", "feature_2", "...", "feature_n"]) \\
    ...    .setOutputCol("features")
    ...
    >>> gen_clf = GenericClassifierModel.pretrained() \\
    ...    .setInputCols(["features"]) \\
    ...    .setOutputCol("prediction") \\
    ...
    >>> pipeline = Pipeline().setStages([
    ...    features_asm,
    ...    gen_clf
    ...])
    ...
    >>> clf_model = pipeline.fit(data)

    """
    name = "GenericClassifierModel"

    classes = Param(Params._dummy(), "classes", "Categorization classes", TypeConverters.toListString)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.generic_classifier.GenericClassifierModel",
                 java_model=None):
        super(GenericClassifierModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name, lang="en", remote_loc=None):
        from sparknlp_jsl.pretrained import InternalResourceDownloader
        return InternalResourceDownloader.downloadModel(GenericClassifierModel, name, lang, remote_loc,
                                                        j_dwn='InternalsPythonResourceDownloader')

