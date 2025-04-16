
import os, glob, psycopg2, csv, sys, re
from pathlib import Path

DATAFILES_DIR = "/exercises/subject/customer"

def get_db_config() -> dict :
    return {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }

def create_and_join_tables(tables):
    DB_CONFIG = get_db_config()

    def get_tables():
        instruction = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"""
        try:
            cur.execute(instruction)
            tables = cur.fetchall()
            table_names = []
            for table in tables:
                table_names.append(table[0])
            return table_names
        except psycopg2.Error as error:
            conn.rollback()
            print(f"Error executing instruction: {error}")

    def exec_instruction(instruction) -> bool:
        print (f"Executing instuction: {instruction}")
        try:
            cur.execute(instruction)
            conn.commit()
        except psycopg2.Error as error:
            conn.rollback()
            print(f"Error executing instruction: {error}")
            return False
        return True
    
    def fill_table_from_csv(table_name, path_csv) -> bool:
        print(f"Filling table: [{table_name}] with data from file: [{path_csv}]")
        try:
            with open(path_csv, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                cur.copy_from(file, table_name, sep=',', null='')
            conn.commit()
        except FileNotFoundError:
            print(f"Error: CSV file not found at {path_csv}")
            return False
        except psycopg2.Error as error:
            conn.rollback()
            print(f"Error executing instruction: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error: {error}")
            return False
        return True


    def check_valid_table(table_name):
        pattern = r'^data_202\d_(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$'
        return bool(re.fullmatch(pattern, table_name, flags=re.IGNORECASE))

    create_table_instruction = f"""CREATE TABLE customer AS"""

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                tables = get_tables()
                for i, table in enumerate(tables):
                    if check_valid_table(table) == True:
                        print(table)
                        create_table_instruction += f"\nSELECT * FROM {table}\n"
                        if i < (len(tables) - 1):
                            create_table_instruction += "UNION ALL"
                print (create_table_instruction)
                if exec_instruction(create_table_instruction) == False:
                    return
                # if fill_table_from_csv(table_name, path_csv) == False:
                #     return

    except Exception as error:
        print(f"Exception: {error}")
        sys.exit(1)

if __name__ == "__main__":

    create_and_join_tables("table_name")
    
    
# -- Create a new table with distinct rows
# CREATE TABLE customer_distinct AS
# SELECT DISTINCT ON (event_time, event_type, product_id, price, user_id, user_session) *
# FROM customer;

# -- Drop the original and rename the new one
# DROP TABLE customer;
# ALTER TABLE customer_distinct RENAME TO customer;