import mysql.connector
from mysql.connector import Error
from app.config import DB_CONFIG


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    connection = get_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if fetch:
                return cursor.fetchall()

            connection.commit()
            return True

        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            connection.rollback()

        finally:
            cursor.close()
            connection.close()

    return None
