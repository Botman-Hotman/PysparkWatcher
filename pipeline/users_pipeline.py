import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_date, current_timestamp, coalesce
from pyspark.sql.functions import lit, when
from pyspark.sql import functions as F

from core.config import settings
from core.spark import spark, spark_settings


def transform_user_data(target_data: dict):
    new_df: DataFrame = target_data['dataframe']

    logging.info(f"{new_df.count()} row's to process for {settings.dw_schema}.{target_data['table_name']}")

    # clean the target data
    new_df = new_df.withColumn("date_of_birth", to_date(col("date_of_birth"), 'dd/MM/yyyy'))
    new_df = new_df.dropDuplicates(subset=["email"])
    new_df = new_df.withColumn(
        "user_id",
        F.concat_ws("-",
                    F.substring(F.md5(F.col("email")), 1, 8),  # 8 characters
                    F.substring(F.md5(F.col("email")), 9, 4),  # 4 characters
                    F.substring(F.md5(F.col("email")), 13, 4),  # 4 characters
                    F.substring(F.md5(F.col("email")), 17, 4),  # 4 characters
                    F.substring(F.md5(F.col("email")), 21, 12)  # 12 characters
                    )
    )

    # Check for existing data
    existing_df: DataFrame = spark.read.jdbc(
        url=spark_settings.jdbc_url,
        table=f"{settings.dw_schema}.{target_data['table_name']}",
        properties=spark_settings.connection_properties
    )

    if not existing_df.isEmpty():
        logging.info(f"{existing_df.count()} existing row's, updating {target_data['table_name']}")

        # Join CDC data with existing dimension data
        join_condition = [new_df["email"] == existing_df["email"]]
        merged_df = new_df.alias('new').join(existing_df.alias('existing'), join_condition, "left")

        # Filter new records
        new_records_df = merged_df.filter(col("existing.user_id").isNull()).select(
            col("new.email"),
            col("new.user_id"),
            col("new.name"),
            col("new.date_of_birth"),
            current_timestamp().alias("effective_start_date"),
            lit(None).cast("timestamp").alias("effective_end_date"),
            lit(True).alias("is_current"),
            lit(1).alias("version_number")
        )

        # Filter changed records
        changed_records_df = merged_df.filter(
            col("existing.email").isNotNull() &
            (
                (col("new.name") != col("existing.name")) |
                (col("new.date_of_birth") != col("existing.date_of_birth"))
            )
        )

        # Insert new rows for updated records with is_current = True and version number updated
        new_updated_rows_df = changed_records_df.select(
            col("new.email").alias("email"),
            col("new.user_id").alias("user_id"),
            col("new.name").alias("name"),
            col("new.date_of_birth").alias("date_of_birth"),
            current_timestamp().alias("effective_start_date"),
            lit(None).cast("timestamp").alias("effective_end_date"),
            lit(True).alias("is_current"),
            (col("existing.version_number") + 1).alias("version_number")
        )

        # Mark old rows as inactive
        deactivated_df = changed_records_df.select(
            col("existing.user_id").alias("user_id"),
            col("existing.email").alias("email"),
            col("existing.name").alias("name"),
            col("existing.date_of_birth").alias("date_of_birth"),
            col("existing.effective_start_date"),
            current_timestamp().alias("effective_end_date"),
            lit(False).alias("is_current"),
            col("existing.version_number")
        )

        # Combine all records
        final_df = deactivated_df.unionByName(new_records_df, allowMissingColumns=True).unionByName(new_updated_rows_df, allowMissingColumns=True)

        # Verify final DataFrame
        # final_df.groupBy('is_current').count().show()
        # final_df.groupBy('version_number').count().show()

        logging.info(f"{new_records_df.count()} new records, {deactivated_df.count()} records deactivated, {new_updated_rows_df.count()} records to update for {settings.dw_schema}.{target_data['table_name']}")

        if not final_df.isEmpty():

            logging.info(f"{final_df.count()} records inserted")

            final_df.write.jdbc(
                url=spark_settings.jdbc_url,
                table=f"{settings.dw_schema}.{target_data['table_name']}",
                mode="append",
                properties=spark_settings.connection_properties
            )

        else:
            logging.info(f"No new records to update for {settings.dw_schema}.{target_data['table_name']}")

    else:
        logging.info(f"No existing data found for {target_data['table_name']} table, inserting data")
        new_df = new_df.withColumn("effective_start_date", current_timestamp())
        new_df = new_df.withColumn("effective_end_date", lit(None).cast("timestamp"))
        new_df = new_df.withColumn("is_current", lit(True))
        new_df = new_df.withColumn("version_number", lit(1))

        new_df.write.jdbc(
            url=spark_settings.jdbc_url,
            table=f"{settings.dw_schema}.{target_data['table_name']}",
            mode="append",
            properties=spark_settings.connection_properties
        )

        logging.info(f"{new_df.count()} records inserted successfully for {settings.dw_schema}.{target_data['table_name']}")


# local test code
if __name__ == '__main__':
    from pipeline.ingestion_layer import ingest_csv_files

    logging.basicConfig(
        format='%(asctime)s : %(name)s :  %(levelname)s : %(funcName)s :  %(message)s'
        , level=logging.DEBUG if False else logging.INFO
        , handlers=[
            logging.StreamHandler()  # Continue to log to the console as well
        ]
    )
    # data = ingest_csv_files('../example_data/inserts/users.csv')
    data = ingest_csv_files('../example_data/updates/users.csv')

    if data is not None:
        if data['table_name'] == 'users':
            transform_user_data(data)