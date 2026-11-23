
from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.grupo_responsavel import GrupoResponsavel


class GruposResponsaveisRepository:
    """
    Realiza consultas aos grupos responsáveis cadastrados.

    A classe acessa a tabela grupos_responsaveis do
    PostgreSQL e reconstrói os registros encontrados
    como objetos da entidade GrupoResponsavel.

    As operações implementadas são apenas de leitura.
    A abertura e o encerramento das conexões são
    gerenciados pelo DBConnectionHandler.
    """

    def select_grupo(self, codigo: str) -> GrupoResponsavel | None:
        """
        Consulta um grupo responsável pelo código.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT id, codigo, nome FROM grupos_responsaveis WHERE codigo = %s", (codigo,)
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return GrupoResponsavel(codigo=row[1], nome=row[2], id=row[0])

    def list_grupos(self) -> list[GrupoResponsavel]:
        """
        Recupera todos os grupos responsáveis cadastrados.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute("SELECT id, codigo, nome FROM grupos_responsaveis ORDER BY id")
            rows = db.cursor.fetchall()
        return [GrupoResponsavel(codigo=row[1], nome=row[2], id=row[0]) for row in rows]