from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.grupo_responsavel import GrupoResponsavel

class GruposResponsaveisRepository:
    def select_grupo(self, codigo: str) -> GrupoResponsavel | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT id, codigo, nome FROM grupos_responsaveis WHERE codigo = %s", (codigo,)
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return GrupoResponsavel(codigo=row[1], nome=row[2], id=row[0])

    def list_grupos(self) -> list[GrupoResponsavel]:
        with DBConnectionHandler() as db:
            db.cursor.execute("SELECT id, codigo, nome FROM grupos_responsaveis ORDER BY id")
            rows = db.cursor.fetchall()
        return [GrupoResponsavel(codigo=row[1], nome=row[2], id=row[0]) for row in rows]
