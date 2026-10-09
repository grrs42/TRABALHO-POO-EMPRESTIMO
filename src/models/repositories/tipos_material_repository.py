from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.tipo_material import TipoMaterial

class TiposMaterialRepository:
    def insert_tipo(self, tipo: TipoMaterial) -> TipoMaterial:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "INSERT INTO tipos_material (sigla, nome) VALUES (%s, %s) RETURNING id",
                (tipo.sigla, tipo.nome),
            )
            new_id = db.cursor.fetchone()[0]
        return TipoMaterial(tipo.sigla, tipo.nome, new_id)

    def select_tipo(self, sigla: str) -> TipoMaterial | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT id, sigla, nome FROM tipos_material WHERE sigla = %s", (sigla,)
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return TipoMaterial(sigla=row[1], nome=row[2], id=row[0])

    def list_tipos(self) -> list[TipoMaterial]:
        with DBConnectionHandler() as db:
            db.cursor.execute("SELECT id, sigla, nome FROM tipos_material ORDER BY sigla")
            rows = db.cursor.fetchall()
        return [TipoMaterial(sigla=row[1], nome=row[2], id=row[0]) for row in rows]
