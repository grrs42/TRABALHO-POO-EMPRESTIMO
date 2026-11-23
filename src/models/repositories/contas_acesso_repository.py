
from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.conta_acesso import ContaAcesso


class ContasAcessoRepository:
    """
    Gerencia a consulta das contas de acesso ao sistema.

    A classe consulta a tabela contas_acesso do PostgreSQL
    e reconstrói os registros como objetos ContaAcesso.

    Cada conta possui um login, um perfil de acesso,
    informações de autenticação e uma referência à
    identidade associada, que pode representar um
    estudante ou um grupo responsável.
    """

    def select_conta(self, login: str) -> ContaAcesso | None:
        """
        Consulta uma conta de acesso pelo login.

        A consulta recupera o perfil da conta, o hash
        da senha, o salt e os identificadores associados
        ao estudante ou grupo responsável.

        O hash e o salt são utilizados posteriormente
        pelo método verificar_senha() de ContaAcesso.

        A consulta não realiza autenticação por si só
        e não modifica os registros do PostgreSQL.
        """
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