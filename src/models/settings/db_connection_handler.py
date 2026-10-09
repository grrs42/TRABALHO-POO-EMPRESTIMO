import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DBConnectionHandler:
    def __init__(self) -> None:
        self.__connection_params = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = psycopg2.connect(**self.__connection_params)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()
