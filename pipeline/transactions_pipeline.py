import logging

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_date, current_timestamp

from core.config import settings
from core.spark import spark, spark_settings


def transform_transaction_data(target_data: dict):
    new_df: DataFrame = target_data['dataframe']

    # clean the target data
    new_df = new_df.withColumn("transaction_date", to_date(col("transaction_date"), "dd/MM/yyyy"))
    new_df = new_df.dropna(subset=["user_id", "amount", "transaction_date"])
    new_df = new_df.dropDuplicates()

    # Check for existing data
    existing_df = spark.read.jdbc(
        url=spark_settings.jdbc_url,
        table=f"{settings.dw_schema}.{target_data['table_name']}",
        properties=spark_settings.connection_properties
    )

    if existing_df.count() > 0:
        logging.debug(f"{existing_df.count()} existing row's, updating {target_data['table_name']}")

    else:
        logging.debug(f"No existing data found for {target_data['table_name']} table, inserting data")

        new_df = new_df.withColumn("created_at", current_timestamp())
        new_df = new_df.withColumn("updated_at", current_timestamp())

        new_df.write.jdbc(
            url=spark_settings.jdbc_url,
            table=f"{settings.dw_schema}.{target_data['table_name']}",
            mode="append",
            properties=spark_settings.connection_properties
        )