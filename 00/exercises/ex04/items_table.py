import os
import psycopg2
from pathlib import Path

DATAFILES_DIR = "/exercises/subject/item"

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
            product_id      int4,
            category_id     numeric(50,0),
            category_code   text,
            brand           text
        )
        """,
        f"""
        COPY {table_name}(product_id,category_id,category_code,brand)
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
    path_file = DATAFILES_DIR + "/item.csv"
    table_name = table_name = Path(path_file).stem
    create_and_fill_table(table_name, path_file)