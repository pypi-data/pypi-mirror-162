""" Utility class that helps to obfuscate tabular data."""
from typing import List, Dict

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession


class StructuredDeidentification:

    """ A helper class that allow to obfuscate a structured deidentification.

    Parameters
    ----------
    columns : dict
          Is a map that allows to select the name of the column with the entity.
                                   The key of the the map is the column in the dataframe and the value of the map is the entity for that column.
 
                                   The default entities are:
                                   "location" A general location."
                                   "location-other" A location that is not country, street,hospital,city or state
                                   "street" A street
                                   "hospital" The name of a hospital.
                                   "city" A city
                                   "state"A state
                                   "zip" The zip code
                                   "country" A country
                                   "contact" The contact of one person
                                   "username"A username
                                   "phone" A number phone.
                                   "fax" The number fax
                                   "url" A url for internet
                                   "email" The email of one person
                                   "profession" A profession of one person
                                   "name" The name opf one person
                                   "doctor" The name of a doctor
                                   "patient" The name of the patient
                                   "id" A general Id number
                                   "bioid" Is a system to screen for protein interactions as they occur in living cells
                                   "age" The age of something or someone
                                   "organization" Name of one organization o company
                                   "healthplan" The id that identify the healthplan
                                   "medicalrecord" The identification of a medical record
                                   "device"The id that identified a device
                                   "date" A general date"
    columnsSeed : int
       Allow to add a seed to the column that you want to obfuscate.The seed used to randomly select the entities used
       during obfuscation mode.
    obfuscateRefFile : bool
         This is an optional parameter that allows to add your own terms to be used for obfuscation.
         The file contains as a key the entity and as the value the terms that will be used in the obfuscation.
    days : int
         Number of days to obfuscate the dates by displacement. If not provided a random integer between 1 and 60 will
         be used
    useRandomDateDisplacement : bool
        Use a random displacement days in dates entities.If true use random displacement days in dates entities,if false use the days.
    dateFormats : List[str]
        List of date formats.example ["dd-MM-yyyy", "dd/MM/yyyy", "d/M/yyyy", "dd-MM-yyyy", "d-M-yyyy"]
    """

    def __init__(self, spark: SparkSession,
                 columns: Dict[str, str],
                 columnsSeed: Dict[str, int] = None,
                 obfuscateRefFile: str = "",
                 obfuscateRefSource: str = "both",
                 days: int = 0,
                 useRandomDateDisplacement: bool = False,
                 dateFormats: List[str] = None):
        if columnsSeed is None:
            columnsSeed = {}

        if dateFormats is None:
            dateFormats = ["dd-MM-yyyy", "dd/MM/yyyy", "d/M/yyyy", "dd-MM-yyyy", "d-M-yyyy",
                           "MM-dd-yyyy", "M-d-yyyy", "d/m/yyyy", "M d, yyyy", "d M yyyy", "yyyy-MM-dd",
                           "yyyy-M-d", "MM/dd/YY"]

        self.columns = columns
        self.spark = spark
        self.obfuscateRefFile = obfuscateRefFile

        self.instance = self.spark._jvm.com.johnsnowlabs.nlp.annotators.deid.StructuredDeidentification(
            columns,
            columnsSeed,
            obfuscateRefFile,
            obfuscateRefSource,
            days,
            useRandomDateDisplacement,
            dateFormats)

    def obfuscateColumns(self, df: DataFrame):
        result = DataFrame(self.instance.obfuscateColumns(df._jdf), self.spark._wrapped)
        return result
