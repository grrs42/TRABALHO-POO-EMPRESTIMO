
import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente utilizadas na conexão.
load_dotenv()


class DBConnectionHandler:
    """
    Gerencia as conexões e transações com o PostgreSQL.

    Utiliza parâmetros definidos em variáveis de ambiente
    para evitar manter credenciais diretamente no código.

    Implementa o protocolo de gerenciador de contexto
    do Python, permitindo utilizar a instrução with.

    Quando a operação termina sem exceções, confirma
    a transação com commit(). Se ocorrer uma exceção,
    desfaz as alterações com rollback().
    """

    def __init__(self) -> None:
        """
        Inicializa os parâmetros da conexão.
        """
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
        """
        Abre a conexão com o banco e cria um cursor.
        """
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