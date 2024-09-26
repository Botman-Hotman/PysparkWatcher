import logging
from .ingestion_layer import ingest_csv_files
from .transactions_pipeline import transform_transaction_data
from .users_pipeline import transform_user_data


def select_pipeline_csv(src_path: str):

    data = ingest_csv_files(src_path)

    if data is not None:
        if data['table_name'] == 'users':
            transform_user_data(data['table'])

        elif data['table_name'] == 'transactions':
            transform_transaction_data(data['table'])

        else:
            logging.error(f"No pipeline available for {data['table_name']}")
            # option to load into automatic staging table for review
