import psycopg2.errors

from src.models.settings.db_connection_handler import DBConnectionHandler
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.repositories.usuarios_repository import UsuariosRepository
from src.models.repositories.materiais_repository import MateriaisRepository


class EmprestimosRepository:
    _SELECT = """
        SELECT
            e.id,
            e.usuario_matricula,
            m.codigo,
            e.status,
            e.data_solicitacao,
            e.data_confirmacao,
            e.data_prevista_devolucao,
            e.data_devolucao,
            e.responsavel_confirmacao
        FROM emprestimos e
        JOIN materiais m ON m.id = e.material_id
        JOIN grupos_responsaveis g ON g.id = m.grupo_id
    """

    def __init__(
        self,
        usuarios_repository: UsuariosRepository | None = None,
        materiais_repository: MateriaisRepository | None = None,
    ) -> None:
        self.__usuarios_repository = usuarios_repository or UsuariosRepository()
        self.__materiais_repository = materiais_repository or MateriaisRepository()

    def registrar_solicitacao(self, emprestimo: Emprestimo) -> Emprestimo:
        if (
            not isinstance(emprestimo, Emprestimo)
            or emprestimo.id is not None
            or emprestimo.status != StatusEmprestimo.PENDENTE
        ):
            raise ValueError("Somente uma nova solicitação pendente pode ser registrada.")
        material_id = emprestimo.material.id
        if material_id is None:
            raise ValueError("Material sem identificador no banco.")

        try:
            with DBConnectionHandler() as db:
                db.cursor.execute(
                    "SELECT disponivel FROM materiais WHERE id = %s FOR UPDATE",
                    (material_id,),
                )
                row = db.cursor.fetchone()
                if row is None:
                    raise ValueError("Material não encontrado.")
                if not row[0]:
                    raise ValueError("Material indisponível para empréstimo.")

                db.cursor.execute(
                    """
                    INSERT INTO emprestimos
                        (usuario_matricula, material_id, status, data_solicitacao)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        emprestimo.usuario.matricula,
                        material_id,
                        StatusEmprestimo.PENDENTE.value,
                        emprestimo.data_solicitacao,
                    ),
                )
                novo_id = db.cursor.fetchone()[0]
                db.cursor.execute(
                    "UPDATE materiais SET disponivel = FALSE WHERE id = %s",
                    (material_id,),
                )
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Material indisponível para empréstimo.")
        except psycopg2.errors.ForeignKeyViolation:
            raise ValueError("Estudante ou material não cadastrado.")

        return self.select_emprestimo(novo_id)

    def select_emprestimo(self, emprestimo_id: int) -> Emprestimo | None:
        with DBConnectionHandler() as db:
            db.cursor.execute(self._SELECT + " WHERE e.id = %s", (emprestimo_id,))
            row = db.cursor.fetchone()
        if row is None:
            return None
        return self.__montar(row)

    def aprovar_solicitacao(
        self, emprestimo_id: int, codigo_grupo: str, prazo_dias: int
    ) -> Emprestimo:
        with DBConnectionHandler() as db:
            emprestimo, codigo_real = self.__carregar_para_alteracao(
                db, emprestimo_id, codigo_grupo
            )
            emprestimo.aprovar(prazo_dias, codigo_real)
            db.cursor.execute(
                """
                UPDATE emprestimos
                SET status = %s,
                    data_confirmacao = %s,
                    data_prevista_devolucao = %s,
                    responsavel_confirmacao = %s
                WHERE id = %s
                """,
                (
                    emprestimo.status.value,
                    emprestimo.data_confirmacao,
                    emprestimo.data_prevista_devolucao,
                    emprestimo.responsavel_confirmacao,
                    emprestimo_id,
                ),
            )
        return self.select_emprestimo(emprestimo_id)

    def recusar_solicitacao(self, emprestimo_id: int, codigo_grupo: str) -> Emprestimo:
        with DBConnectionHandler() as db:
            emprestimo, _ = self.__carregar_para_alteracao(
                db, emprestimo_id, codigo_grupo
            )
            emprestimo.recusar()
            db.cursor.execute(
                "UPDATE emprestimos SET status = %s WHERE id = %s",
                (emprestimo.status.value, emprestimo_id),
            )
            db.cursor.execute(
                "UPDATE materiais SET disponivel = TRUE WHERE id = %s",
                (emprestimo.material.id,),
            )
        return self.select_emprestimo(emprestimo_id)

    def registrar_devolucao(self, emprestimo_id: int, codigo_grupo: str) -> Emprestimo:
        with DBConnectionHandler() as db:
            emprestimo, _ = self.__carregar_para_alteracao(
                db, emprestimo_id, codigo_grupo
            )
            emprestimo.registrar_devolucao()
            db.cursor.execute(
                "UPDATE emprestimos SET status = %s, data_devolucao = %s WHERE id = %s",
                (emprestimo.status.value, emprestimo.data_devolucao, emprestimo_id),
            )
            db.cursor.execute(
                "UPDATE materiais SET disponivel = TRUE WHERE id = %s",
                (emprestimo.material.id,),
            )
        return self.select_emprestimo(emprestimo_id)

    def list_emprestimos_usuario(self, matricula: str) -> list[Emprestimo]:
        return self.__listar(" WHERE e.usuario_matricula = %s ORDER BY e.id", (matricula,))

    def list_emprestimos_pendentes(self, codigo_grupo: str) -> list[Emprestimo]:
        return self.__listar(
            " WHERE UPPER(g.codigo) = UPPER(%s) AND e.status = %s ORDER BY e.id",
            (codigo_grupo, StatusEmprestimo.PENDENTE.value),
        )

    def list_emprestimos_ativos(self, codigo_grupo: str) -> list[Emprestimo]:
        return self.__listar(
            " WHERE UPPER(g.codigo) = UPPER(%s) AND e.status = %s ORDER BY e.id",
            (codigo_grupo, StatusEmprestimo.ATIVO.value),
        )

    def __listar(self, filtro: str, parametros: tuple) -> list[Emprestimo]:
        with DBConnectionHandler() as db:
            db.cursor.execute(self._SELECT + filtro, parametros)
            rows = db.cursor.fetchall()
        return [self.__montar(row) for row in rows]

    def __carregar_para_alteracao(
        self, db: DBConnectionHandler, emprestimo_id: int, codigo_grupo: str
    ) -> tuple[Emprestimo, str]:
        db.cursor.execute(
            """
            SELECT e.id, g.codigo
            FROM emprestimos e
            JOIN materiais m ON m.id = e.material_id
            JOIN grupos_responsaveis g ON g.id = m.grupo_id
            WHERE e.id = %s
            FOR UPDATE OF e, m
            """,
            (emprestimo_id,),
        )
        row = db.cursor.fetchone()
        if row is None:
            raise ValueError("Empréstimo não encontrado.")
        if row[1].upper() != str(codigo_grupo).strip().upper():
            raise PermissionError("Este grupo não pode operar o material informado.")

        db.cursor.execute(self._SELECT + " WHERE e.id = %s", (emprestimo_id,))
        return self.__montar(db.cursor.fetchone()), row[1]

    def __montar(self, row: tuple) -> Emprestimo:
        usuario = self.__usuarios_repository.select_usuario(row[1])
        material = self.__materiais_repository.select_material(row[2])
        if usuario is None or material is None:
            raise RuntimeError("Registro de empréstimo inconsistente no banco.")
        return Emprestimo(
            usuario=usuario,
            material=material,
            id=row[0],
            status=StatusEmprestimo(row[3]),
            data_solicitacao=row[4],
            data_confirmacao=row[5],
            data_prevista_devolucao=row[6],
            data_devolucao=row[7],
            responsavel_confirmacao=row[8],
        )
