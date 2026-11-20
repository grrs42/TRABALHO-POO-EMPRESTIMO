import unittest
from datetime import date, datetime

from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.usuario import Usuario
from src.models.entities.calculadora import Calculadora
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class TestEmprestimo(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("20260001", "Lucas")
        self.material = Calculadora(
            tipo=TipoMaterial("CAL", "Calculadora", id=1, especializacao="CALCULADORA"),
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia", id=1),
            modelo="C-100", codigo="CAL-001", id=1
        )
        self.solicitado_em = datetime(2026, 11, 20, 9, 0)
        self.confirmado_em = datetime(2026, 11, 20, 10, 0)
        self.devolvido_em = datetime(2026, 11, 22, 10, 0)
        self.emprestimo = Emprestimo(
            usuario=self.usuario,
            material=self.material,
            data_solicitacao=self.solicitado_em,
        )

    def test_criacao_pendente(self):
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)
        self.assertIsNone(self.emprestimo.data_confirmacao)
        self.assertEqual(self.emprestimo.material.codigo, "CAL-001")

    def test_aprovacao_registra_datas(self):
        self.emprestimo.aprovar(7, "Responsável GEES", self.confirmado_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)
        self.assertEqual(self.emprestimo.data_prevista_devolucao, date(2026, 11, 27))
        self.assertEqual(self.emprestimo.responsavel_confirmacao, "Responsável GEES")

    def test_recusa(self):
        self.emprestimo.recusar()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.RECUSADO)
        self.assertIsNone(self.emprestimo.data_confirmacao)

    def test_devolucao(self):
        self.emprestimo.aprovar(7, "Responsável GEES", self.confirmado_em)
        self.emprestimo.registrar_devolucao(self.devolvido_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.DEVOLVIDO)
        self.assertEqual(self.emprestimo.data_devolucao, self.devolvido_em)

    def test_prazo_invalido_preserva_estado(self):
        with self.assertRaises(ValueError):
            self.emprestimo.aprovar(0, "Responsável GEES", self.confirmado_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)
        self.assertIsNone(self.emprestimo.data_confirmacao)

    def test_responsavel_vazio_preserva_estado(self):
        with self.assertRaises(ValueError):
            self.emprestimo.aprovar(7, "  ", self.confirmado_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_aprovar_recusado_rejeitado(self):
        self.emprestimo.recusar()
        with self.assertRaises(ValueError):
            self.emprestimo.aprovar(7, "Responsável GEES", self.confirmado_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.RECUSADO)

    def test_devolver_antes_de_aprovar_rejeitado(self):
        with self.assertRaises(ValueError):
            self.emprestimo.registrar_devolucao(self.devolvido_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_devolucao_repetida_rejeitada(self):
        self.emprestimo.aprovar(7, "Responsável GEES", self.confirmado_em)
        self.emprestimo.registrar_devolucao(self.devolvido_em)
        with self.assertRaises(ValueError):
            self.emprestimo.registrar_devolucao(self.devolvido_em)
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.DEVOLVIDO)
        self.assertEqual(self.emprestimo.data_devolucao, self.devolvido_em)

    def test_atraso(self):
        self.emprestimo.aprovar(7, "Responsável GEES", self.confirmado_em)
        self.assertFalse(self.emprestimo.esta_atrasado(date(2026, 11, 27)))
        self.assertTrue(self.emprestimo.esta_atrasado(date(2026, 11, 28)))
        self.emprestimo.registrar_devolucao(self.devolvido_em)
        self.assertFalse(self.emprestimo.esta_atrasado(date(2026, 11, 28)))

    def test_reconstrucao_estado_ativo(self):
        ativo = Emprestimo(
            usuario=self.usuario,
            material=self.material,
            id=1,
            status=StatusEmprestimo.ATIVO,
            data_solicitacao=self.solicitado_em,
            data_confirmacao=self.confirmado_em,
            data_prevista_devolucao=date(2026, 11, 27),
            responsavel_confirmacao="Responsável GEES",
        )
        self.assertEqual(ativo.id, 1)
        self.assertEqual(ativo.status, StatusEmprestimo.ATIVO)

    def test_reconstrucao_inconsistente_rejeitada(self):
        with self.assertRaises(ValueError):
            Emprestimo(
                usuario=self.usuario,
                material=self.material,
                status=StatusEmprestimo.ATIVO,
                data_solicitacao=self.solicitado_em,
            )


if __name__ == "__main__":
    unittest.main()
