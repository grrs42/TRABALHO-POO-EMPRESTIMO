from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel

class MateriaisRepository:
    def insert_material(self, material: Material) -> Material:
        # O número sequencial do tipo e o INSERT ficam na mesma transação
        with DBConnectionHandler() as db:
            db.cursor.execute(
                "SELECT COALESCE(MAX(numero), 0) + 1 FROM materiais WHERE tipo_id = %s",
                (material.tipo.id,),
            )
            numero = db.cursor.fetchone()[0]
            codigo = Material.gerar_codigo(material.tipo.sigla, numero)
            db.cursor.execute(
                """INSERT INTO materiais (codigo, numero, tipo_id, grupo_id, disponivel)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (codigo, numero, material.tipo.id, material.grupo.id,
                 material.verificar_disponibilidade()),
            )
            new_id = db.cursor.fetchone()[0]
        return Material(material.tipo, material.grupo, codigo,
                        material.verificar_disponibilidade(), new_id)

    def select_material(self, codigo: str) -> Material | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """SELECT m.id, m.codigo, m.disponivel,
                          t.id, t.sigla, t.nome,
                          g.id, g.codigo, g.nome
                   FROM materiais m
                   JOIN tipos_material t ON t.id = m.tipo_id
                   JOIN grupos_responsaveis g ON g.id = m.grupo_id
                   WHERE m.codigo = %s""",
                (codigo,),
            )
            row = db.cursor.fetchone()
        if row is None:
            return None
        tipo = TipoMaterial(sigla=row[4], nome=row[5], id=row[3])
        grupo = GrupoResponsavel(codigo=row[7], nome=row[8], id=row[6])
        return Material(tipo, grupo, codigo=row[1], disponivel=row[2], id=row[0])

    def delete_material(self, codigo: str) -> bool:
        with DBConnectionHandler() as db:
            db.cursor.execute("DELETE FROM materiais WHERE codigo = %s", (codigo,))
            return db.cursor.rowcount > 0
