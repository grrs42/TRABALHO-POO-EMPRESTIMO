from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.conta_acesso import ContaAcesso


class ContasAcessoRepository:
    def select_conta(self, login: str) -> ContaAcesso | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """
                SELECT login, tipo, senha_hash, salt, usuario_matricula, grupo_codigo
                FROM contas_acesso
                WHERE login = %s
                """,
                (login,),
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return ContaAcesso(
            login=row[0],
            tipo=row[1],
            senha_hash=row[2],
            salt=row[3],
            usuario_matricula=row[4],
            grupo_codigo=row[5],
        )
