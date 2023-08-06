from sparknlp.common import *

class AssertionFilterer(AnnotatorModel):
    """Filters entities coming from ASSERTION type annotations and returns the CHUNKS.
    Filters can be set via a white list on the extracted chunk, the assertion or a regular expression.
    White list for assertion is enabled by default. To use chunk white list, ``criteria`` has to be set to ``isin``.
    For regex, ``criteria`` has to be set to ``regex``.

    ==============================  ======================
    Input Annotation types          Output Annotation type
    ==============================  ======================
    ``DOCUMENT, CHUNK, ASSERTION``  ``CHUNK``
    ==============================  ======================

    Parameters
    ----------
    whiteList
        If defined, list of entities to process. The rest will be ignored
    regex
        If defined, list of entities to process. The rest will be ignored.
    criteria
           Tag representing what is the criteria to filter the chunks. possibles values (assertion|isIn|regex)
                assertion: Filter by the assertion
                isIn : Filter by the chunk
                regex : Filter using a regex
    entitiesConfidence
        Entity pairs to remove based on the confidence level

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
     To see how the assertions are extracted, see the example for AssertionDLModel.
     Define an extra step where the assertions are filtered
    >>> assertionFilterer = AssertionFilterer() \\
    ...   .setInputCols(["sentence","ner_chunk","assertion"]) \\
    ...    .setOutputCol("filtered") \\
    ...   .setCriteria("assertion") \\
    ...   .setWhiteList(["present"])
    ...
    >>> assertionPipeline = Pipeline(stages=[
    ...   documentAssembler,
    ...   sentenceDetector,
    ...   tokenizer,
    ...   embeddings,
    ...   nerModel,
    ...   nerConverter,
    ...   clinicalAssertion,
    ...   assertionFilterer
    ... ])
    ...
    >>> assertionModel = assertionPipeline.fit(data)
    >>> result = assertionModel.transform(data)


    >>> result.selectExpr("ner_chunk.result", "assertion.result").show(3, truncate=False)
    +--------------------------------+--------------------------------+
    |result                          |result                          |
    +--------------------------------+--------------------------------+
    |[severe fever, sore throat]     |[present, present]              |
    |[stomach pain]                  |[absent]                        |
    |[an epidural, PCA, pain control]|[present, present, hypothetical]|
    +--------------------------------+--------------------------------+

    >>> result.select("filtered.result").show(3, truncate=False)
    +---------------------------+
    |result                     |
    +---------------------------+
    |[severe fever, sore throat]|
    |[]                         |
    |[an epidural, PCA]         |
    +---------------------------+
    """
    name = "ChunksFilter"

    whiteList = Param(
        Params._dummy(),
        "whiteList",
        "If defined, list of entities to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    regex = Param(
        Params._dummy(),
        "regex",
        "If defined, list of regex to process. The rest will be ignored.",
        typeConverter=TypeConverters.toListString
    )

    criteria = Param(Params._dummy(), "criteria",
                     "Assertion find by assertion",
                     TypeConverters.toString)

    entitiesConfidence = Param(Params._dummy(),
                               "entitiesConfidence",
                               "Entity pairs to remove based on the confidence level",
                               typeConverter=TypeConverters.identity)

    def setWhiteList(self, value):
        """Sets list of entities to process. The rest will be ignored.

        Parameters
        ----------
        value : list
           If defined, list of entities to process. The rest will be ignored.
        """
        return self._set(whiteList=value)

    def setRegex(self, value):
        """Sets llist of regex to process. The rest will be ignored.

        Parameters
        ----------
        value : list
           List of dash-separated pairs of named entities
        """
        return self._set(regex=value)

    def setCriteria(self, s):
        """Set tag representing what is the criteria to filter the chunks. possibles values (assertion|isIn|regex)

        Parameters
        ----------
        pairs : list
           List of dash-separated pairs of named entities
        """
        return self._set(criteria=s)

    # TODO set confidence

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.AssertionFilterer", java_model=None):
        super(AssertionFilterer, self).__init__(
            classname=classname,
            java_model=java_model
        )
