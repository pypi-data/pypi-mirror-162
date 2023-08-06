"""
Helper class that allow us to update pretrained models located in the cache folder
"""

import sparknlp_jsl.internal as _interanl


class UpdateModels(object):

    @staticmethod
    def updateCacheModels(cache_folder=""):
        """ This method refreshes all pretrained models located in the cache pretrained folder.
            This method check what are the existing models in the cache pretrained folder and check if there is a new
            version for that model.If there are a new model then this model will be downloaded

        Parameters
        ----------
        cache_folder : str
            Path where the models will be refreshed. i.e ("hdfs:..","file:...")
        """
        _interanl._UpdateCacheModels(cache_folder).apply()

    @staticmethod
    def updateModels(date_cutoff, cache_folder=""):
        """ This method download all new pretrained models since the date_cutoff.

        Parameters
        ----------
        date_cutoff:str
            Date since
                It is the date from which the new models will be downloaded.
        cache_folder : str
            Path where the models will be downloaded. i.e ("hdfs:..","file:...")
        """
        _interanl._UpdateModels(date_cutoff, cache_folder).apply()
