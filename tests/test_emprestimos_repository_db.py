import os
import unittest
from datetime import date, timedelta

import psycopg2.errors

from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.repositories.emprestimos_repository import EmprestimosRepository
from src.models.repositories.materiais_repository import MateriaisRepository
from src.models.repositories.usuarios_repository import UsuariosRepository
from src.models.settings.db_connection_handler import DBConnectionHandler

DB_TEST_NAME = os.getenv("DB_TEST_NAME")
MATRICULA = "2026000001"
CODIGO = "CAL-001"


@unittest.skipUnless(DB_TEST_NAME, "Defina DB_TEST_NAME no .env para rodar os testes de banco.")
class TestEmprestimosRepositoryDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DB_TEST_NAME == os.getenv("DB_NAME"):
            raise unittest.SkipTest("DB_TEST_NAME deve ser diferente do banco de demonstração.")
        cls._db_name_original = os.getenv("DB_NAME")
        os.environ["DB_NAME"] = DB_TEST_NAME

    @classmethod
    def tearDownClass(cls):
        if cls._db_name_original is None:
            os.environ.pop("DB_NAME", None)
        else:
            os.environ["DB_NAME"] = cls._db_name_original

    def setUp(self):
        with DBConnectionHandler() as db:
            db.cursor.execute("DELETE FROM emprestimos")
            db.cursor.execute("UPDATE materiais SET disponivel = TRUE WHERE codigo = %s", (CODIGO,))
        self.usuarios = UsuariosRepository()
        self.materiais = MateriaisRepository()
        self.repo = EmprestimosRepository(self.usuarios, self.materiais)

    def _solicitar(self) -> Emprestimo:
        usuario = self.usuarios.select_usuario(MATRICULA)
        material = self.materiais.select_material(CODIGO)
        return self.repo.registrar_solicitacao(Emprestimo(usuario=usuario, material=material))

    def _contar_emprestimos(self) -> int:
        with DBConnectionHandler() as db:
            db.cursor.execute("SELECT COUNT(*) FROM emprestimos")
            return db.cursor.fetchone()[0]

    def _disponivel(self) -> bool:
        return self.materiais.select_material(CODIGO).verificar_disponibilidade()

    def test_solicitacao_reserva_material_e_persiste(self):
        salvo = self._solicitar()
        self.assertIsNotNone(salvo.id)
        self.assertEqual(salvo.status, StatusEmprestimo.PENDENTE)
        self.assertFalse(salvo.material.verificar_disponibilidade())
        relido = EmprestimosRepository().select_emprestimo(salvo.id)
        self.assertEqual(relido.status, StatusEmprestimo.PENDENTE)
        self.assertEqual(relido.usuario.matricula, MATRICULA)
        self.assertFalse(self._disponivel())

    def test_fluxo_pelo_controller(self):
        controller = SistemaEmprestimosController(self.usuarios, self.materiais, self.repo)
        resposta = controller.solicitar_emprestimo({"matricula": MATRICULA, "codigo_material": "cal-001"})
        self.assertTrue(resposta["success"], resposta.get("error"))
        self.assertEqual(resposta["message"]["attributes"]["status"], "PENDENTE")

    def test_segunda_solicitacao_rejeitada_sem_reserva_parcial(self):
        usuario = self.usuarios.select_usuario(MATRICULA)
        material_desatualizado = self.materiais.select_material(CODIGO)
        self._solicitar()
        with self.assertRaises(ValueError):
            self.repo.registrar_solicitacao(
                Emprestimo(usuario=usuario, material=material_desatualizado)
            )
        self.assertEqual(self._contar_emprestimos(), 1)

    def test_indice_impede_dois_emprestimos_abertos(self):
        salvo = self._solicitar()
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            with DBConnectionHandler() as db:
                db.cursor.execute(
                    """
                    INSERT INTO emprestimos (usuario_matricula, material_id, status, data_solicitacao)
                    VALUES (%s, %s, 'PENDENTE', NOW())
                    """,
                    (MATRICULA, salvo.material.id),
                )
        self.assertEqual(self._contar_emprestimos(), 1)

    def test_aprovar_mantem_material_reservado(self):
        salvo = self._solicitar()
        aprovado = self.repo.aprovar_solicitacao(salvo.id, "GEES", 7)
        self.assertEqual(aprovado.status, StatusEmprestimo.ATIVO)
        self.assertEqual(aprovado.responsavel_confirmacao, "GEES")
        self.assertEqual(aprovado.data_prevista_devolucao, date.today() + timedelta(days=7))
        self.assertFalse(self._disponivel())

    def test_grupo_errado_nao_altera_dados(self):
        salvo = self._solicitar()
        with self.assertRaises(PermissionError):
            self.repo.aprovar_solicitacao(salvo.id, "LABFIS", 7)
        self.assertEqual(self.repo.select_emprestimo(salvo.id).status, StatusEmprestimo.PENDENTE)
        self.assertFalse(self._disponivel())

    def test_reaprovar_rejeitado_preserva_ativo(self):
        salvo = self._solicitar()
        self.repo.aprovar_solicitacao(salvo.id, "GEES", 7)
        with self.assertRaises(ValueError):
            self.repo.aprovar_solicitacao(salvo.id, "GEES", 3)
        relido = self.repo.select_emprestimo(salvo.id)
        self.assertEqual(relido.status, StatusEmprestimo.ATIVO)
        self.assertEqual(relido.data_prevista_devolucao, date.today() + timedelta(days=7))

    def test_recusar_libera_material_e_nao_repete(self):
        salvo = self._solicitar()
        recusado = self.repo.recusar_solicitacao(salvo.id, "GEES")
        self.assertEqual(recusado.status, StatusEmprestimo.RECUSADO)
        self.assertTrue(self._disponivel())
        with self.assertRaises(ValueError):
            self.repo.recusar_solicitacao(salvo.id, "GEES")
        self.assertTrue(self._disponivel())

    def test_devolucao_libera_material_e_nao_repete(self):
        salvo = self._solicitar()
        self.repo.aprovar_solicitacao(salvo.id, "GEES", 7)
        devolvido = self.repo.registrar_devolucao(salvo.id, "GEES")
        self.assertEqual(devolvido.status, StatusEmprestimo.DEVOLVIDO)
        self.assertIsNotNone(devolvido.data_devolucao)
        self.assertTrue(self._disponivel())
        with self.assertRaises(ValueError):
            self.repo.registrar_devolucao(salvo.id, "GEES")
        self.assertEqual(self._solicitar().status, StatusEmprestimo.PENDENTE)

    def test_devolver_pendente_rejeitado(self):
        salvo = self._solicitar()
        with self.assertRaises(ValueError):
            self.repo.registrar_devolucao(salvo.id, "GEES")
        self.assertEqual(self.repo.select_emprestimo(salvo.id).status, StatusEmprestimo.PENDENTE)
        self.assertFalse(self._disponivel())

    def test_id_inexistente(self):
        self.assertIsNone(self.repo.select_emprestimo(999999))
        with self.assertRaises(ValueError):
            self.repo.aprovar_solicitacao(999999, "GEES", 7)

    def test_consultas_por_usuario_e_grupo(self):
        salvo = self._solicitar()
        self.assertEqual([e.id for e in self.repo.list_emprestimos_usuario(MATRICULA)], [salvo.id])
        self.assertEqual([e.id for e in self.repo.list_emprestimos_pendentes("GEES")], [salvo.id])
        self.assertEqual(self.repo.list_emprestimos_pendentes("LABFIS"), [])
        self.assertEqual(self.repo.list_emprestimos_ativos("GEES"), [])
        self.repo.aprovar_solicitacao(salvo.id, "GEES", 7)
        self.assertEqual([e.id for e in self.repo.list_emprestimos_ativos("GEES")], [salvo.id])


if __name__ == "__main__":
    unittest.main()
