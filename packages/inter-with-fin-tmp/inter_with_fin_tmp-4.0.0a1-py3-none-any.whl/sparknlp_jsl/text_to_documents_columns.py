from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession


class TextToDocumentsColumns:

    def __init__(self, spark: SparkSession, columns: List[str]):
        self.columns = columns
        self.spark = spark

        self.instance = self.spark._jvm.com.johnsnowlabs.nlp.annotators.deid.TextToDocumentColumns(
            columns
        )

    def toDocumentsColumns(self, df: DataFrame):
        result = DataFrame(self.instance.toDocumentsColumns(df._jdf), self.spark._wrapped)
        return result
