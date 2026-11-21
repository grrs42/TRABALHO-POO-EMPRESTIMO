"""Testes da devolução sem PostgreSQL, usando Mock para a persistência."""

import unittest
from datetime import datetime
from unittest.mock import Mock

from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.entities.calculadora import Calculadora
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.usuario import Usuario


class TestDevolucaoController(unittest.TestCase):
    def setUp(self):
        usuario = Usuario("2026000001", "Estudante Exemplo")
        self.material = Calculadora(
            tipo=TipoMaterial(
                "CAL", "Calculadora", id=1, especializacao="CALCULADORA"
            ),
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia de Sistemas", id=1),
            modelo="FX-82", codigo="CAL-001", id=7,
        )
        self.solicitado_em = datetime(2026, 11, 20, 9, 0)
        self.confirmado_em = datetime(2026, 11, 20, 10, 0)
        self.devolvido_em = datetime(2026, 11, 22, 10, 0)
        self.emprestimo = Emprestimo(
            usuario=usuario,
            material=self.material,
            id=15,
            data_solicitacao=self.solicitado_em,
        )
        self.emprestimo.aprovar(7, "GEES", self.confirmado_em)
        self.material.marcar_indisponivel()

        self.repositorio = Mock()
        self.repositorio.select_emprestimo.return_value = self.emprestimo

        def simular_devolucao(emprestimo_id, grupo):
            self.emprestimo.registrar_devolucao(self.devolvido_em)
            return self.emprestimo

        self.repositorio.registrar_devolucao.side_effect = simular_devolucao
        self.controller = SistemaEmprestimosController(Mock(), Mock(), self.repositorio)
        self.dados = {"id_emprestimo": 15}

    def test_devolucao_valida(self):
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"]["status"], "DEVOLVIDO")
        self.assertEqual(
            resposta["message"]["attributes"]["data_devolucao"],
            "2026-11-22T10:00:00",
        )
        self.repositorio.select_emprestimo.assert_called_once_with(15)
        self.repositorio.registrar_devolucao.assert_called_once_with(15, "GEES")

    def test_aceita_id_textual_e_normaliza_grupo(self):
        resposta = self.controller.registrar_devolucao(
            {"id_emprestimo": " 15 "}, " gees "
        )
        self.assertTrue(resposta["success"])
        self.repositorio.registrar_devolucao.assert_called_once_with(15, "GEES")

    def test_rejeita_dados_nao_dicionario(self):
        resposta = self.controller.registrar_devolucao(None, "GEES")
        self.assertFalse(resposta["success"])
        self.repositorio.select_emprestimo.assert_not_called()
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)

    def test_rejeita_id_ausente(self):
        resposta = self.controller.registrar_devolucao({}, "GEES")
        self.assertFalse(resposta["success"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)

    def test_rejeita_id_invalido(self):
        for valor in (0, -1, "abc", True):
            with self.subTest(id_emprestimo=valor):
                resposta = self.controller.registrar_devolucao(
                    {"id_emprestimo": valor}, "GEES"
                )
                self.assertFalse(resposta["success"])
        self.repositorio.select_emprestimo.assert_not_called()
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)

    def test_rejeita_grupo_nao_autenticado(self):
        resposta = self.controller.registrar_devolucao(self.dados, None)
        self.assertFalse(resposta["success"])
        self.assertIn("não autenticada", resposta["error"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)

    def test_rejeita_grupo_de_outro_material(self):
        resposta = self.controller.registrar_devolucao(self.dados, "LABFIS")
        self.assertFalse(resposta["success"])
        self.assertIn("não pode operar", resposta["error"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)
        self.assertFalse(self.material.verificar_disponibilidade())

    def test_rejeita_emprestimo_inexistente(self):
        self.repositorio.select_emprestimo.return_value = None
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("não encontrado", resposta["error"])
        self.repositorio.registrar_devolucao.assert_not_called()

    def test_rejeita_solicitacao_pendente(self):
        self.emprestimo = Emprestimo(
            usuario=self.emprestimo.usuario,
            material=self.material,
            id=15,
            data_solicitacao=self.solicitado_em,
        )
        self.repositorio.select_emprestimo.return_value = self.emprestimo
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("ativos", resposta["error"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_rejeita_solicitacao_recusada(self):
        self.emprestimo = Emprestimo(
            usuario=self.emprestimo.usuario,
            material=self.material,
            id=15,
            data_solicitacao=self.solicitado_em,
        )
        self.emprestimo.recusar()
        self.repositorio.select_emprestimo.return_value = self.emprestimo
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.RECUSADO)

    def test_rejeita_devolucao_duplicada(self):
        self.emprestimo.registrar_devolucao(self.devolvido_em)
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.repositorio.registrar_devolucao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.DEVOLVIDO)
        self.assertEqual(self.emprestimo.data_devolucao, self.devolvido_em)

    def test_rejeita_concorrencia_do_repositorio(self):
        self.repositorio.registrar_devolucao.side_effect = ValueError(
            "Empréstimo já devolvido por outra operação."
        )
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("outra operação", resposta["error"])
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)
        self.assertIsNone(self.emprestimo.data_devolucao)
        self.assertFalse(self.material.verificar_disponibilidade())

    def test_erro_do_banco_preserva_estado(self):
        self.repositorio.registrar_devolucao.side_effect = RuntimeError(
            "Falha na transação."
        )
        resposta = self.controller.registrar_devolucao(self.dados, "GEES")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível registrar a devolução.")
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)
        self.assertIsNone(self.emprestimo.data_devolucao)
        self.assertFalse(self.material.verificar_disponibilidade())


if __name__ == "__main__":
    unittest.main()