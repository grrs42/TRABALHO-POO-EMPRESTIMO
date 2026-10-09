from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.usuario import Usuario

class UsuariosRepository:
    def insert_usuario(self, usuario: Usuario) -> None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "INSERT INTO usuarios (matricula, nome) VALUES (%s, %s)",
                (usuario.matricula, usuario.nome),
            )

    def select_usuario(self, matricula: str) -> Usuario | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT matricula, nome FROM usuarios WHERE matricula = %s", (matricula,)
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        return Usuario(row[0], row[1])

    def delete_usuario(self, matricula: str) -> bool:
        with DBConnectionHandler() as db:
            db.cursor.execute("DELETE FROM usuarios WHERE matricula = %s", (matricula,))
            return db.cursor.rowcount > 0
