from sparknlp.common import *

class ChunkMapperFilterer(AnnotatorModel):
    """
        Filter what kind of chunks must be returned, whether the chunks that are in the label dependencies or not.

        ==============================   =======================
            Input Annotation types        Output Annotation type
        ==============================   =======================
        ``CHUNK``,``LABEL_DEPENDENCY``          ``CHUNK``
        ==============================   =======================

        Parameters
        ----------
        setReturnCriteria
            Select what kind o chunk we will return. If is fail will return the chunk that are no in the label dependencies if is success return the labels that are label dependencies
    """

    name = "ChunkMapperFiltererModel"

    returnCriteria = Param(Params._dummy(),
                           "returnCriteria",
                           "Select what kind o chunk we will return. If is fail will return the chunk that are no in the label depencies if is success return the labels that are label dependencies",
                           typeConverter=TypeConverters.toString)

    def setReturnCriteria(self, rc):
        return self._set(returnCriteria=rc)

    def __init__(self, classname="com.johnsnowlabs.nlp.annotators.chunker.ChunkMapperFilterer", java_model=None):
        super(ChunkMapperFilterer, self).__init__(
            classname=classname,
            java_model=java_model
        )