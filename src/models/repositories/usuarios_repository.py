
from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.usuario import Usuario
from src.models.entities.conta_acesso import ContaAcesso


class UsuariosRepository:
    """
    Gerencia a persistência dos estudantes no PostgreSQL.

    Realiza operações de inserção, consulta e exclusão
    dos registros da tabela usuarios.

    Também permite cadastrar a conta de acesso vinculada
    ao estudante, utilizando uma única transação para
    inserir os dois registros.
    """

    def insert_usuario(self, usuario: Usuario, conta: ContaAcesso | None = None) -> None:
        """
        Insere um estudante e sua conta de acesso.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "INSERT INTO usuarios (matricula, nome) VALUES (%s, %s)",
                (usuario.matricula, usuario.nome),
            )
            if conta is not None:
                db.cursor.execute(
                    """
                    INSERT INTO contas_acesso
                        (login, senha_hash, salt, tipo, usuario_matricula, grupo_codigo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        conta.login,
                        conta.senha_hash,
                        conta.salt,
                        conta.tipo,
                        conta.usuario_matricula,
                        conta.grupo_codigo,
                    ),
                )

    def select_usuario(self, matricula: str) -> Usuario | None:
        """
        Consulta um estudante utilizando sua matrícula.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT matricula, nome FROM usuarios WHERE matricula = %s", (matricula,)
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return Usuario(row[0], row[1])

    def delete_usuario(self, matricula: str) -> bool:
        """
        Exclui um estudante identificado pela matrícula.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute("DELETE FROM usuarios WHERE matricula = %s", (matricula,))
            return db.cursor.rowcount > 0