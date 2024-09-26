from pyspark.sql import SparkSession

from core.config import spark_settings

spark: SparkSession = (SparkSession.builder
                       .appName(spark_settings.app_name)
                       .config("spark.jars", "core/drivers/postgresql-42.7.4.jar")
                       .master(spark_settings.master)
                       .getOrCreate()
                       )
spark.sparkContext.setLogLevel(spark_settings.spark_log_level)
