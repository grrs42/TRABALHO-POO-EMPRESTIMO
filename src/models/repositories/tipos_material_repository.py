
from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.tipo_material import TipoMaterial


class TiposMaterialRepository:
    """
    Gerencia a persistência das categorias de materiais.

    Realiza inserções e consultas na tabela tipos_material
    do PostgreSQL.

    Cada categoria possui uma sigla, um nome e uma
    especialização que determina a classe concreta
    utilizada pela MaterialFactory.

    Os registros recuperados são reconstruídos como
    objetos da entidade TipoMaterial.
    """

    def insert_tipo(self, tipo: TipoMaterial) -> TipoMaterial:
        """
        Insere uma nova categoria de material no banco.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """
                INSERT INTO tipos_material
                    (sigla, nome, especializacao)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    tipo.sigla,
                    tipo.nome,
                    tipo.especializacao
                )
            )

            new_id = db.cursor.fetchone()[0]

        return TipoMaterial(
            sigla=tipo.sigla,
            nome=tipo.nome,
            id=new_id,
            especializacao=tipo.especializacao
        )

    def select_tipo(self, sigla: str) -> TipoMaterial | None:
        """
        Consulta uma categoria pela sua sigla.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """
                SELECT id, sigla, nome, especializacao
                FROM tipos_material
                WHERE sigla = %s
                """,
                (sigla,)
            )

            row = db.cursor.fetchone()

        if row is None:
            return None

        return TipoMaterial(
            id=row[0],
            sigla=row[1],
            nome=row[2],
            especializacao=row[3]
        )

    def list_tipos(self) -> list[TipoMaterial]:
        """
        Recupera todas as categorias cadastradas.
        """
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """
                SELECT id, sigla, nome, especializacao
                FROM tipos_material
                ORDER BY sigla
                """
            )

            rows = db.cursor.fetchall()

        return [
            TipoMaterial(
                id=row[0],
                sigla=row[1],
                nome=row[2],
                especializacao=row[3]
            )
            for row in rows
        ]