import logging
import os
from pyspark.sql import DataFrame
from core.spark import spark


def ingest_csv_files(directory: str) -> None | dict:
    """
    Ingest a target csv file and check for data. Return a dict with dataframe and metadata.
    """
    file_name: str = os.path.basename(directory)
    logging.info(f'processing {file_name}')
    table_name: str = file_name.split('.')[0]

    df_new: DataFrame = spark.read.csv(
        directory,
        header=True,
        inferSchema=True  # Automatically infer data types
    )

    if df_new.count() > 0:
        logging.debug(f"{df_new.count()} rows found for {file_name}")

        return {
            "dataframe": df_new,
            "table_name": table_name,
            "file_name": file_name,
            "source_directory": directory
        }

    else:
        logging.error(f"{file_name} has no rows to process, skipping.")
        return

