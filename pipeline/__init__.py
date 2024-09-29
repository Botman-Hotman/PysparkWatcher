import logging

from .ingestion_layer import ingest_csv_files
from .transactions_pipeline import transform_transaction_data
from .users_pipeline import transform_user_data
from core.db import sync_engine
from sqlalchemy import text

def select_pipeline_csv(src_path: str):

    data = ingest_csv_files(src_path)

    if data is not None:
        if data['table_name'] == 'users':
            transform_user_data(data)

            # remove any old records from the data base that have been deactivated to new versions
            with sync_engine.begin() as conn:
                conn.execute(text("""
                                    with target_data as 
                                    (
                                        select user_id, is_current, version_number from datawarehouse.users 
                                        where version_number = 2
                                    )
                                    
                                    
                                    , filter_data as (
                                    
                                        select * from datawarehouse.users 
                                        where user_id in (select user_id from target_data)
                                        and is_current 
                                        and version_number = 1
                                    )
                                    
                                    
                                    delete from datawarehouse.users 
                                    where id in (select id from filter_data);
                                    """
                                    )
                               )
                conn.commit()
                conn.close()

        elif data['table_name'] == 'transactions':
            transform_transaction_data(data)

        else:
            logging.error(f"No pipeline available for {data['table_name']}")
            # option to load into automatic staging table for review
