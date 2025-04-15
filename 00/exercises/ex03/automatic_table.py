import os
import glob
from pathlib import Path
import psycopg2

DATAFILES_DIR = "/exercises/subject/customer"

def get_db_config() -> dict :
    return {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }

def create_and_fill_table(table_name, path_csv):
    DB_CONFIG = get_db_config()

    commands = (
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            event_time      timestamptz,
            event_type      text,
            product_id      int4,
            price           money,
            user_id         int8,
            user_session    uuid
        )
        """,
        f"""
        COPY {table_name}(event_time,event_type,product_id,price,user_id,user_session)
        FROM '{path_csv}'
        DELIMITER ','
        CSV HEADER;
        """,
        )
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    try:
                        print (f"executing: {command}")
                        cur.execute(command)
                        conn.commit()
                    except psycopg2.Error as error:
                        conn.rollback()
                        print(f"Error executing command: {error}")
                        raise
    except Exception as error:
        print(f"Exception: {error}")
        raise
    finally:
        print("All commands executed")

if __name__ == "__main__":
    files = glob.glob(DATAFILES_DIR + "/data_*.csv")
    for file in files:
        table_name = Path(file).stem
        print (f"\nCreating table: {table_name}")
        print ("-----------------------------")
        create_and_fill_table(table_name, file)
