from sparknlp.common import *

class NerDisambiguator(AnnotatorApproach):
    """ Links words of interest, such as names of persons, locations and companies, from an input text document to
    a corresponding unique entity in a target Knowledge Base (KB). Words of interest are called Named Entities (NEs),
    mentions, or surface forms.
    Instantiated / pretrained model of the NerDisambiguator.
    Links words of interest, such as names of persons, locations and companies, from an input text document to
    a corresponding unique entity in a target Knowledge Base (KB). Words of interest are called Named Entities (NEs),

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
    ``CHUNK, SENTENCE_EMBEDDINGS``            ``DISAMBIGUATION``
    ========================================= ======================

    Parameters
    ----------
    embeddingTypeParam
        Could be 'bow' for word embeddings or 'sentence' for sentences
    numFirstChars
        How many characters should be considered for initial prefix search in knowledge base
    tokenSearch
        Should we search by token or by chunk in knowledge base (token is recommended)
    narrowWithApproximateMatching
        Should we narrow prefix search results with levenstein distance based matching (true is recommended)
    levenshteinDistanceThresholdParam
        Levenshtein distance threshold to narrow results from prefix search (0.1 is default)
    nearMatchingGapParam
        Puts a limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing,len(candidate) - len(entity chunk) > nearMatchingGap (Default: 4).
    predictionsLimit
        Limit on amount of predictions N for topN predictions
    s3KnowledgeBaseName
        knowledge base name in s3

    Examples
    --------

    >>> data = spark.createDataFrame([["The show also had a contestant named Donald Trump who later defeated Christina Aguilera ..."]]) \
    ...   .toDF("text")
    >>> documentAssembler = DocumentAssembler() \\
    ...   .setInputCol("text") \\
    ...   .setOutputCol("document")
    >>> sentenceDetector = SentenceDetector() \\
    ...   .setInputCols(["document"]) \\
    ...   .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...   .setInputCols(["sentence"]) \\
    ...   .setOutputCol("token")
    >>> word_embeddings = WordEmbeddingsModel.pretrained() \\
    ...   .setInputCols(["sentence", "token"]) \\
    ...   .setOutputCol("embeddings")
    >>> sentence_embeddings = SentenceEmbeddings() \\
    ...   .setInputCols(["sentence","embeddings"]) \\
    ...   .setOutputCol("sentence_embeddings")\
    >>> ner_model = NerDLModel.pretrained() \\
    ...   .setInputCols(["sentence", "token", "embeddings"]) \\
    ...   .setOutputCol("ner")
    >>> ner_converter = NerConverter() \\
    ...   .setInputCols(["sentence", "token", "ner"]) \\
    ...   .setOutputCol("ner_chunk") \\
    ...   .setWhiteList(["PER"])

    Then the extracted entities can be disambiguated.
    >>> disambiguator = NerDisambiguator() \\
    ...   .setS3KnowledgeBaseName("i-per") \\
    ...   .setInputCols(["ner_chunk", "sentence_embeddings"]) \\
    ...   .setOutputCol("disambiguation") \\
    ...   .setNumFirstChars(5)
    ...
    >>> nlpPipeline = Pipeline(stages=[
    ...   documentAssembler,
    ...   sentenceDetector,
    ...   tokenizer,
    ...   word_embeddings,
    ...   sentence_embeddings,
    ...   ner_model,
    ...   ner_converter,
    ...   disambiguator])
    ...
    >>> model = nlpPipeline.fit(data)
    >>> result = model.transform(data)
    >>> result.selectExpr("explode(disambiguation)") \\
    ...  .selectExpr("col.metadata.chunk as chunk", "col.result as result").show(5, False)

    +------------------+------------------------------------------------------------------------------------------------------------------------+
    |chunk             |result                                                                                                                  |
    +------------------+------------------------------------------------------------------------------------------------------------------------+
    |Donald Trump      |http:#en.wikipedia.org/?curid=4848272, http:#en.wikipedia.org/?curid=31698421, http:#en.wikipedia.org/?curid=55907961   |
    |Christina Aguilera|http:#en.wikipedia.org/?curid=144171, http:#en.wikipedia.org/?curid=6636454                                             |
    +------------------+------------------------------------------------------------------------------------------------------------------------+

    """
    embeddingTypeParam = Param(Params._dummy(),
                               "embeddingTypeParam",
                               "Could be 'bow' for word embeddings or 'sentence' for sentences",
                               typeConverter=TypeConverters.toString)

    numFirstChars = Param(Params._dummy(),
                          "numFirstChars",
                          "How many characters should be considered for initial prefix search in knowledge base",
                          typeConverter=TypeConverters.toInt)

    tokenSearch = Param(Params._dummy(),
                        "tokenSearch",
                        "Should we search by token or by chunk in knowledge base (token is recommended)",
                        typeConverter=TypeConverters.toBoolean)

    narrowWithApproximateMatching = Param(Params._dummy(),
                                          "narrowWithApproximateMatching",
                                          "Should we narrow prefix search results with levenstein distance based matching (true is recommended)",
                                          typeConverter=TypeConverters.toBoolean)

    levenshteinDistanceThresholdParam = Param(Params._dummy(),
                                              "levenshteinDistanceThresholdParam",
                                              "Levenshtein distance threshold to narrow results from prefix search (0.1 is default)",
                                              typeConverter=TypeConverters.toFloat)

    nearMatchingGapParam = Param(Params._dummy(),
                                 "nearMatchingGapParam",
                                 "Puts a limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing",
                                 typeConverter=TypeConverters.toInt)

    predictionsLimit = Param(Params._dummy(),
                             "predictionsLimit",
                             "Limit on amount of predictions N for topN predictions",
                             typeConverter=TypeConverters.toInt)

    s3KnowledgeBaseName = Param(Params._dummy(),
                                "s3KnowledgeBaseName",
                                "knowledge base name in s3",
                                typeConverter=TypeConverters.toString)

    def setEmbeddingType(self, value):
        """Sets if we want to use 'bow' for word embeddings or 'sentence' for sentences"

        Parameters
        ----------
        value : str
            Can be 'bow' for word embeddings or 'sentence' for sentences (Default: sentence)
            Can be 'bow' for word embeddings or 'sentence' for sentences (Default: sentence)
        """
        return self._set(embeddingTypeParam=value)

    def setNumFirstChars(self, value):
        """How many characters should be considered for initial prefix search in knowledge base

        Parameters
        ----------
        value : bool
            How many characters should be considered for initial prefix search in knowledge base
        """
        return self._set(numFirstChars=value)

    def setTokenSearch(self, value):
        """Sets whether to search by token or by chunk in knowledge base (Default: true)

        Parameters
        ----------
        value : bool
            Whether to search by token or by chunk in knowledge base (Default: true)
        """
        return self._set(tokenSearch=value)

    def setNarrowWithApproximateMatching(self, value):
        """Sets whether to narrow prefix search results with levenstein distance based matching (Default: true)

        Parameters
        ----------
        value : bool
           Whether to narrow prefix search results with levenstein distance based matching (Default: true)
        """
        return self._set(narrowWithApproximateMatching=value)

    def setLevenshteinDistanceThresholdParam(self, value):
        """Sets Levenshtein distance threshold to narrow results from prefix search (0.1 is default)

        Parameters
        ----------
        value : float
            Levenshtein distance threshold to narrow results from prefix search (0.1 is default)
        """
        return self._set(levenshteinDistanceThresholdParam=value)

    def setNearMatchingGapParam(self, value):
        """Sets a limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing.

        Parameters
        ----------
        value : int
             Limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing
        """
        return self._set(nearMatchingGapParam=value)

    def setPredictionLimit(self, value):
        """Sets limit on amount of predictions N for topN predictions

        Parameters
        ----------
        value : bool
             Limit on amount of predictions N for topN predictions
        """
        return self._set(predictionsLimit=value)

    def setS3KnowledgeBaseName(self, value):
        """Sets knowledge base name in s3

        Parameters
        ----------
        value : str
            knowledge base name in s3 example (i-per)
        """
        return self._set(s3KnowledgeBaseName=value)

    @keyword_only
    def __init__(self):
        super(NerDisambiguator, self).__init__(
            classname="com.johnsnowlabs.nlp.annotators.disambiguation.NerDisambiguator")
        self._setDefault(numFirstChars=4, tokenSearch=True, levenshteinDistanceThresholdParam=0.1,
                         nearMatchingGapParam=4, narrowWithApproximateMatching=True, predictionsLimit=100,
                         embeddingTypeParam="sentence")

    def _create_model(self, java_model):
        return NerDisambiguatorModel(java_model=java_model)


class NerDisambiguatorModel(AnnotatorModel):
    """ Links words of interest, such as names of persons, locations and companies, from an input text document to
    a corresponding unique entity in a target Knowledge Base (KB). Words of interest are called Named Entities (NEs),
    mentions, or surface forms.
    Instantiated / pretrained model of the NerDisambiguator.
    Links words of interest, such as names of persons, locations and companies, from an input text document to
    a corresponding unique entity in a target Knowledge Base (KB). Words of interest are called Named Entities (NEs),

    ========================================= ======================
    Input Annotation types                    Output Annotation type
    ========================================= ======================
     ``CHUNK, SENTENCE_EMBEDDINGS``           ``DISAMBIGUATION``
    ========================================= ======================

    Parameters
    ----------
    embeddingTypeParam
        Could be ``bow`` for word embeddings or ``sentence`` for sentences
    numFirstChars
        How many characters should be considered for initial prefix search in knowledge base
    tokenSearch
        Should we search by token or by chunk in knowledge base (token is recommended)
    narrowWithApproximateMatching
        Should we narrow prefix search results with levenstein distance based matching (true is recommended)
    levenshteinDistanceThresholdParam
        Levenshtein distance threshold to narrow results from prefix search (0.1 is default)
    nearMatchingGapParam
        Puts a limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing,len(candidate) - len(entity chunk) > nearMatchingGap (Default: 4).
    predictionsLimit
        Limit on amount of predictions N for topN predictions
    s3KnowledgeBaseName
        knowledge base name in s3

    Examples
    --------

    >>> data = spark.createDataFrame([["The show also had a contestant named Donald Trump who later defeated Christina Aguilera ..."]]) \
    ...   .toDF("text")
    >>> documentAssembler = DocumentAssembler() \\
    ...   .setInputCol("text") \\
    ...   .setOutputCol("document")
    >>> sentenceDetector = SentenceDetector() \\
    ...   .setInputCols(["document"]) \\
    ...   .setOutputCol("sentence")
    >>> tokenizer = Tokenizer() \\
    ...   .setInputCols(["sentence"]) \\
    ...   .setOutputCol("token")
    >>> word_embeddings = WordEmbeddingsModel.pretrained() \\
    ...   .setInputCols(["sentence", "token"]) \\
    ...   .setOutputCol("embeddings")
    >>> sentence_embeddings = SentenceEmbeddings() \\
    ...   .setInputCols(["sentence","embeddings"]) \\
    ...   .setOutputCol("sentence_embeddings")\
    >>> ner_model = NerDLModel.pretrained() \\
    ...   .setInputCols(["sentence", "token", "embeddings"]) \\
    ...   .setOutputCol("ner")
    >>> ner_converter = NerConverter() \\
    ...   .setInputCols(["sentence", "token", "ner"]) \\
    ...   .setOutputCol("ner_chunk") \\
    ...   .setWhiteList(["PER"])

    Then the extracted entities can be disambiguated.
    >>> disambiguator = NerDisambiguatorModel.pretrained() \\
    ...   .setInputCols(["ner_chunk", "sentence_embeddings"]) \\
    ...   .setOutputCol("disambiguation") \\
    ...   .setNumFirstChars(5)
    ...
    >>> nlpPipeline = Pipeline(stages=[
    ...   documentAssembler,
    ...   sentenceDetector,
    ...   tokenizer,
    ...   word_embeddings,
    ...   sentence_embeddings,
    ...   ner_model,
    ...   ner_converter,
    ...   disambiguator])
    ...
    >>> model = nlpPipeline.fit(data)
    >>> result = model.transform(data)
    >>> result.selectExpr("explode(disambiguation)") \\
    ...  .selectExpr("col.metadata.chunk as chunk", "col.result as result").show(5, False)

    +------------------+------------------------------------------------------------------------------------------------------------------------+
    |chunk             |result                                                                                                                  |
    +------------------+------------------------------------------------------------------------------------------------------------------------+
    |Donald Trump      |http:#en.wikipedia.org/?curid=4848272, http:#en.wikipedia.org/?curid=31698421, http:#en.wikipedia.org/?curid=55907961   |
    |Christina Aguilera|http:#en.wikipedia.org/?curid=144171, http:#en.wikipedia.org/?curid=6636454                                             |
    +------------------+------------------------------------------------------------------------------------------------------------------------+

    """

    name = "NerDisambiguatorModel"

    embeddingTypeParam = Param(Params._dummy(),
                               "embeddingTypeParam",
                               "Could be 'bow' for word embeddings or 'sentence' for sentences",
                               typeConverter=TypeConverters.toString)

    numFirstChars = Param(Params._dummy(),
                          "numFirstChars",
                          "How many characters should be considered for initial prefix search in knowledge base",
                          typeConverter=TypeConverters.toInt)

    tokenSearch = Param(Params._dummy(),
                        "tokenSearch",
                        "Should we search by token or by chunk in knowledge base (token is recommended)",
                        typeConverter=TypeConverters.toBoolean)

    narrowWithApproximateMatching = Param(Params._dummy(),
                                          "narrowWithApproximateMatching",
                                          "Should we narrow prefix search results with levenstein distance based matching (true is recommended)",
                                          typeConverter=TypeConverters.toBoolean)

    levenshteinDistanceThresholdParam = Param(Params._dummy(),
                                              "levenshteinDistanceThresholdParam",
                                              "Levenshtein distance threshold to narrow results from prefix search (0.1 is default)",
                                              typeConverter=TypeConverters.toFloat)

    nearMatchingGapParam = Param(Params._dummy(),
                                 "nearMatchingGapParam",
                                 "Levenshtein distance threshold to narrow results from prefix search (0.1 is default)",
                                 typeConverter=TypeConverters.toInt)

    predictionsLimit = Param(Params._dummy(),
                             "predictionsLimit",
                             "Limit on amount of predictions N for topN predictions",
                             typeConverter=TypeConverters.toInt)

    def setEmbeddingType(self, value):
        """Sets if we want to use 'bow' for word embeddings or 'sentence' for sentences

        Parameters
        ----------
        value : str
            Can be 'bow' for word embeddings or 'sentence' for sentences (Default: sentence)
        """
        return self._set(embeddingTypeParam=value)

    def setNumFirstChars(self, value):
        """How many characters should be considered for initial prefix search in knowledge base

        Parameters
        ----------
        value : bool
            How many characters should be considered for initial prefix search in knowledge base
        """
        return self._set(numFirstChars=value)

    def setTokenSearch(self, value):
        """Sets whether to search by token or by chunk in knowledge base (Default: true)

        Parameters
        ----------
        value : bool
            Whether to search by token or by chunk in knowledge base (Default: true)
        """
        return self._set(tokenSearch=value)

    def setNarrowWithApproximateMatching(self, value):
        """Sets whether to narrow prefix search results with levenstein distance based matching (Default: true)

        Parameters
        ----------
        value : bool
           Whether to narrow prefix search results with levenstein distance based matching (Default: true)
        """
        return self._set(narrowWithApproximateMatching=value)

    def setLevenshteinDistanceThresholdParam(self, value):
        """Sets Levenshtein distance threshold to narrow results from prefix search (0.1 is default)

        Parameters
        ----------
        value : float
            Levenshtein distance threshold to narrow results from prefix search (0.1 is default)
        """
        return self._set(levenshteinDistanceThresholdParam=value)

    def setNearMatchingGapParam(self, value):
        """Sets a limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing.

        Parameters
        ----------
        value : int
             Limit on a string length (by trimming the candidate chunks) during levenshtein-distance based narrowing
        """
        return self._set(nearMatchingGapParam=value)

    def setPredictionLimit(self, value):
        """Sets limit on amount of predictions N for topN predictions

        Parameters
        ----------
        s : bool
             Limit on amount of predictions N for topN predictions
        """
        return self._set(predictionsLimit=value)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.disambiguation.NerDisambiguatorModel",
                 java_model=None):
        super(NerDisambiguatorModel, self).__init__(
            classname=classname,
            java_model=java_model
        )

    @staticmethod
    def pretrained(name="disambiguator_per", lang="en", remote_loc=None):
        from sparknlp.pretrained import ResourceDownloader
        return ResourceDownloader.downloadModel(NerDisambiguatorModel, name, lang, "clinical/models",
                                                j_dwn='InternalsPythonResourceDownloader')

