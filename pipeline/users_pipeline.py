import logging

from pyspark.sql import DataFrame
from core.spark import spark, spark_settings
from pyspark.sql.functions import col, current_date, datediff, to_date, current_timestamp
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, lit, when, coalesce, greatest
from core.config import settings


def transform_user_data(target_data: dict):

    new_df: DataFrame = target_data['dataframe']

    # clean the target data
    new_df = new_df.withColumn("date_of_birth", to_date(col("date_of_birth"), "dd/MM/yyyy"))
    new_df = new_df.dropna(subset=["name", "email", "date_of_birth"])
    new_df = new_df.dropDuplicates(subset=["email"])

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

        new_df = new_df.withColumn("effective_start_date", current_timestamp())
        new_df = new_df.withColumn("is_current", lit(True))
        new_df = new_df.withColumn("version_number", lit(1))

        new_df.write.jdbc(
            url=spark_settings.jdbc_url,
            table=f"{settings.dw_schema}.{target_data['table_name']}",
            mode="append",
            properties=spark_settings.connection_properties
        )


if __name__ == '__main__':
    from pipeline.ingestion_layer import ingest_csv_files

    logging.basicConfig(
        format='%(asctime)s : %(name)s :  %(levelname)s : %(funcName)s :  %(message)s'
        , level=logging.DEBUG if True else logging.INFO
        , handlers=[

            logging.StreamHandler()  # Continue to log to the console as well
        ]
    )

    data = ingest_csv_files('../example_data/inserts/users.csv')

    if data is not None:
        if data['table_name'] == 'users':
            transform_user_data(data)