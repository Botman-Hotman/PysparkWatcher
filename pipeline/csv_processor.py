import logging
import os

from core.spark import spark


def csv_processor(directory: str):
    file_name = os.path.basename(directory)
    df_new = spark.read.csv(
        directory,
        header=True,
        inferSchema=True
    )

    if df_new.count() > 0:
        logging.debug(f"{df_new.count()} rows found for {file_name}")
        # jdbc_url = "jdbc:postgresql://your_postgres_host:your_postgres_port/your_database"
        # db_properties = {
        #     "user": "your_username",
        #     "password": "your_password",
        #     "driver": "org.postgresql.Driver"
        # }
        #
        # # Read existing data from PostgreSQL
        # df_existing = spark.read.jdbc(
        #     url=jdbc_url,
        #     table=file_name.split('.')[0],
        #     properties=db_properties
        # )
        #
        # # Ensure primary keys are not null
        # df_new = df_new.dropna(subset=primary_key)
        # df_existing = df_existing.dropna(subset=primary_key)
        #
        # # Identify inserts (new records not in existing data)
        # inserts_df = df_new.alias("new").join(
        #     df_existing.alias("existing"),
        #     on=primary_key,
        #     how="left_anti"
        # )
        #
        # # Identify updates (records where non-key columns have changed)
        # updates_df = df_new.alias("new").join(
        #     df_existing.alias("existing"),
        #     on=primary_key,
        #     how="inner"
        # ).filter(
        #     # Replace 'attribute_columns' with the actual columns to compare
        #     col("new.attribute") != col("existing.attribute")
        # )
        #
        # # Identify deletes (records in existing data not in new data)
        # deletes_df = df_existing.alias("existing").join(
        #     df_new.alias("new"),
        #     on=primary_key,
        #     how="left_anti"
        # )


    else:
        logging.warning(f"{file_name} has no rows to process, skipping.")

