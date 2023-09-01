# db_connector.py

import mysql.connector

def connect_to_db():
    # Replace the placeholders with your actual database credentials
    conn = mysql.connector.connect(
        host="your_db_host",
        user="your_db_username",
        password="your_db_password",
        database="your_db_name"
    )
    return conn

def execute_query(conn, query, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result
