import os
import psycopg2


def get_db_config() -> dict :
    return {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }

def create_tables():
    DB_CONFIG = get_db_config()

    commands = (
        """
        CREATE TABLE IF NOT EXISTS data_2022_nov (
            event_time      timestamptz,
            event_type      text,
            product_id      int4,
            price           money,
            user_id         int8,
            user_session    uuid
        )
        """,
        """
        COPY data_2022_nov(event_time,event_type,product_id,price,user_id,user_session)
        FROM '/exercises/subject/customer/data_2022_nov.csv'
        DELIMITER ','
        CSV HEADER;
        """,
        )
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    try:
                        print (f"execcuting {command}")
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
    create_tables()