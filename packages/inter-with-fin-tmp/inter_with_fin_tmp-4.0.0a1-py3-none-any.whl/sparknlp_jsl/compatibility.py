"""Class to check what are the models compatibles with our distribution.
"""
from pyspark.sql import SparkSession



class Compatibility:

    def __init__(self, spark: SparkSession):
        self.spark = spark

        self.instance = self.spark._jvm.com.johnsnowlabs.util.Compatibility()

    def findVersion(self, model: str = "all"):
        """ It returns the private models that are compatible with the current library version.

        Parameters
        ----------
        model : str
            Name of the model that you try to find.If the model name is 'all' that method will return all private models.
        """
        result = self.instance.findVersion(model)
        return result

    def showVersion(self, model: str = "all"):
        """It prints the private models that are compatibles with the current library version.

        Parameters
        ----------
        model : str
            Name of the model that you try to find.If the model name is 'all' that method will print all private models.
        """
        print(self.instance.showStringVersion(model))
