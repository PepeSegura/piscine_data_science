
import os, glob, psycopg2, csv, sys, re
from pathlib import Path

import time
from functools import wraps

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def get_db_config() -> dict :
    return {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }

def get_event_types_count() -> dict:
    DB_CONFIG = get_db_config()

    @timer_decorator
    def exec_instruction(instruction) -> bool | dict:
        print (f"Executing instuction: {instruction}")
        try:
            cur.execute(instruction)
            result = cur.fetchall()
            conn.commit()
            return result
        except psycopg2.Error as error:
            conn.rollback()
            print(f"Error executing instruction: {error}")
            return False
    
    get_event_types_count = f"""
    SELECT event_type, COUNT(*) as type_count FROM customers
    GROUP BY event_type
    ORDER BY type_count DESC;
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                return exec_instruction(get_event_types_count)

    except Exception as error:
        print(f"Exception: {error}")
        sys.exit(1)

# Import libraries
from matplotlib import pyplot as plt
import numpy as np


if __name__ == "__main__":
    result = get_event_types_count()
    total_count = sum(count for _, count in result)

    types_count = dict(result)

    types_percent = {}
    for x in types_count:
        types_percent[x] = (types_count[x] * 100) / total_count

    print(types_count)
    print(types_percent)
    print("total_count:   ", sum(types_count[x] for x in types_count))
    print("total_percent: ", sum(types_percent[x] for x in types_percent))

    # # Creating plot
    # fig = plt.figure(figsize=(10, 7))
    # plt.pie(types_percent.values(), labels=types_percent.keys())

    # # show plot
    # plt.show()
