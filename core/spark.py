from pyspark.sql import SparkSession

from core.config import spark_settings

spark: SparkSession = (SparkSession.builder
                       .appName(spark_settings.app_name)
                       .master(spark_settings.master)
                       .getOrCreate()
                       )
