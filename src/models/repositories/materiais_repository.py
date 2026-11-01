from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.factories.material_factory import MaterialFactory

class MateriaisRepository:
    def insert_material(self, material: Material) -> Material:
        material.validar_dados_especificos()
        detalhes = material.detalhes_especificos()

        with DBConnectionHandler() as db:
            # Gera o próximo número para este tipo de material.
            db.cursor.execute(
                """
                SELECT COALESCE(MAX(numero), 0) + 1
                FROM materiais
                WHERE tipo_id = %s
                """,
                (material.tipo.id,)
            )

            numero = db.cursor.fetchone()[0]

            codigo = Material.gerar_codigo(
                material.tipo.sigla,
                numero
            )

            # Salva atributos comuns e específicos.
            db.cursor.execute(
                """
                INSERT INTO materiais (
                    codigo,
                    numero,
                    tipo_id,
                    grupo_id,
                    disponivel,
                    marca,
                    modelo,
                    tamanho,
                    titulo,
                    editora,
                    descricao
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    codigo,
                    numero,
                    material.tipo.id,
                    material.grupo.id,
                    material.verificar_disponibilidade(),
                    material.marca,
                    detalhes.get("modelo"),
                    detalhes.get("tamanho"),
                    detalhes.get("titulo"),
                    detalhes.get("editora"),
                    detalhes.get("descricao")
                )
            )

            novo_id = db.cursor.fetchone()[0]

            # Reconstrói o objeto com o ID e código gerados.
            material_salvo = MaterialFactory.criar(
                tipo=material.tipo,
                grupo=material.grupo,
                dados_especificos=detalhes,
                marca=material.marca,
                codigo=codigo,
                disponivel=material.verificar_disponibilidade(),
                id=novo_id
            )

        return material_salvo


    def select_material(self, codigo: str) -> Material | None:
        """Consulta um exemplar e reconstrói sua subclasse."""
        with DBConnectionHandler() as db:
            db.cursor.execute(
                """
                SELECT
                    m.id,
                    m.codigo,
                    m.disponivel,
                    m.marca,
                    m.modelo,
                    m.tamanho,
                    m.titulo,
                    m.editora,
                    m.descricao,
                    t.id,
                    t.sigla,
                    t.nome,
                    t.especializacao,
                    g.id,
                    g.codigo,
                    g.nome
                FROM materiais m
                JOIN tipos_material t ON t.id = m.tipo_id
                JOIN grupos_responsaveis g ON g.id = m.grupo_id
                WHERE m.codigo = %s
                """,
                (codigo,)
            )    
            row = db.cursor.fetchone()

        if row is None:
            return None

        # Reconstrói o tipo e o grupo associados ao material.
        tipo = TipoMaterial(
            id=row[9],
            sigla=row[10],
            nome=row[11],
            especializacao=row[12]
        )

        grupo = GrupoResponsavel(
            id=row[13],
            codigo=row[14],
            nome=row[15]
        )

        # Recupera somente os atributos da especialização.
        detalhes_por_especializacao = {
            "CALCULADORA": {"modelo": row[4]},
            "JALECO": {"tamanho": row[5]},
            "LIVRO": {
                "titulo": row[6],
                "editora": row[7]
            },
            "OUTRO": {"descricao": row[8]}
        }

        dados_especificos = detalhes_por_especializacao[
            tipo.especializacao
        ]

        # Retorna a subclasse correspondente ao tipo cadastrado.
        return MaterialFactory.criar(
            tipo=tipo,
            grupo=grupo,
            dados_especificos=dados_especificos,
            marca=row[3],
            codigo=row[1],
            disponivel=row[2],
            id=row[0]
        )

    def delete_material(self, codigo: str) -> bool:
        with DBConnectionHandler() as db:
            db.cursor.execute("DELETE FROM materiais WHERE codigo = %s", (codigo,))
            return db.cursor.rowcount > 0
