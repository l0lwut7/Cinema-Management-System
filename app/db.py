import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="vps56VPS",
            database="cinema_db"
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("MySQL connection error:", e)
        return None