
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
        "dbname"    : os.environ.get("POSTGRES_DB"),
        "user"      : os.environ.get("POSTGRES_USER"),
        "password"  : os.environ.get("POSTGRES_PASSWORD"),
        "host"      : os.environ.get("POSTGRES_HOST", "localhost"),
        "port"      : os.environ.get("POSTGRES_PORT", "5432"),
    }

def exec_query(query) -> dict:
    DB_CONFIG = get_db_config()

    response_data = {}
    @timer_decorator
    def exec_instruction(instruction) -> bool:
        nonlocal response_data
        try:
            cur.execute(instruction)
            response_data = cur.fetchall()
            conn.commit()
            return True
        except psycopg2.Error as error:
            conn.rollback()
            print(f"Error executing instruction: {error}")
            return False
    
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                if exec_instruction(query) == False:
                    return None
        conn.close()
        cur.close()
        return response_data
    except Exception as error:
        print(f"Exception: {error}")
        sys.exit(1)

# Import libraries
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

def building():
    customers_count = f"""
    SELECT 
        order_count, 
        COUNT(user_id) AS customer_count
    FROM (
        SELECT 
            user_id, 
            CEIL(COUNT(user_session) / 10) * 10 AS order_count
        FROM customers 
        WHERE event_type = 'purchase' 
        GROUP BY user_id
    ) AS user_orders
    GROUP BY order_count
    ORDER BY order_count;
    """
    # LIMIT 10000

    data = exec_query(customers_count)

    df = pd.DataFrame(data, columns=['order_count', 'customer_count'])
    print(df)

    plt.figure(figsize=(10, 6))
    plt.gcf().set_facecolor('lightgray')
    plt.xlabel('frequency')
    plt.ylabel('customers')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    data_zoom = df[(df['order_count'] >= 0) & (df['order_count'] < 40)]
    bars = plt.bar(data_zoom['order_count'], data_zoom['customer_count'],
                   color='#b6c5d8',
                   width=5,align='edge'
    )
    ax = plt.gca()
    ax.set_facecolor('lightblue')

    plt.savefig('./figure_1.png', dpi=300, bbox_inches='tight')
    plt.close()

def building2():
    customers_count = f"""
    SELECT
        user_id,
        COUNT(*) AS purchases,
        SUM(price) as spend
    FROM
        customers
    WHERE
        event_type = 'purchase'
    GROUP BY
        user_id
    ORDER BY
        spend
    LIMIT 50000;
    """
    # LIMIT 10000

    data = exec_query(customers_count)

    df = pd.DataFrame(data, columns=['user_id', 'purchases', 'spend'])
    print(df)

    plt.figure(figsize=(10, 6))
    plt.gcf().set_facecolor('lightgray')
    plt.xlabel('frequency')
    plt.ylabel('customers')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # data_zoom = df[(df['order_count'] >= 0) & (df['order_count'] < 40)]
    bars = plt.hist(df['purchases']
    )
    ax = plt.gca()
    ax.set_facecolor('lightblue')

    plt.savefig('./figure_1.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    building2()
   
"""
SELECT
    user_id,
    COUNT(*) AS purchases,
	SUM(price) as spend
FROM
    customers
WHERE
    event_type = 'purchase'
GROUP BY
    user_id
ORDER BY
    spend ;
"""
"""
SELECT 
    order_count, 
    COUNT(user_id) AS customer_count
FROM (
    SELECT 
        user_id, 
        COUNT(DISTINCT user_session) AS order_count
    FROM customers 
    WHERE event_type = 'purchase' 
    GROUP BY user_id
) AS user_orders
GROUP BY order_count
ORDER BY order_count;
"""

"""
SELECT 
    spending_range, 
    SUM(number_clients) AS group_total
FROM (
    SELECT 
        user_id,
        CASE
            WHEN SUM(price::numeric) <= 50 THEN 50
            WHEN SUM(price::numeric) > 50 AND SUM(price::numeric) <= 100 THEN 100
            WHEN SUM(price::numeric) > 100 AND SUM(price::numeric) <= 150 THEN 150
            WHEN SUM(price::numeric) > 150 AND SUM(price::numeric) <= 200 THEN 200
            WHEN SUM(price::numeric) > 200 AND SUM(price::numeric) <= 250 THEN 250
            ELSE 300
        END AS spending_range,
        COUNT(DISTINCT(user_id)) AS number_clients
    FROM customers
    WHERE event_type = 'purchase'
    GROUP BY user_id
) AS user_spending
GROUP BY spending_range
ORDER BY spending_range
"""