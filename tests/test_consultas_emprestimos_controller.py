import unittest
from datetime import date, datetime
from unittest.mock import Mock

from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.entities.calculadora import Calculadora
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.usuario import Usuario


class TestConsultasEmprestimosController(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("2026000001", "Estudante Exemplo")
        self.outro_usuario = Usuario("2026000002", "Outra Pessoa")
        self.grupo = GrupoResponsavel("GEES", "Grêmio de Engenharia", id=1)
        self.outro_grupo = GrupoResponsavel("LABFIS", "Laboratório de Física", id=2)
        tipo = TipoMaterial("CAL", "Calculadora", id=1, especializacao="CALCULADORA")
        self.material = Calculadora(
            tipo=tipo, grupo=self.grupo, modelo="FX-82", codigo="CAL-001", id=7
        )
        self.material_outro_grupo = Calculadora(
            tipo=tipo, grupo=self.outro_grupo, modelo="C-100", codigo="CAL-002", id=8
        )

        def emprestimo(usuario, material, id, status=StatusEmprestimo.PENDENTE):
            comum = {
                "usuario": usuario,
                "material": material,
                "id": id,
                "data_solicitacao": datetime(2026, 11, 20, 9, 0),
            }
            if status == StatusEmprestimo.PENDENTE:
                return Emprestimo(**comum)
            comum.update({
                "status": status,
                "data_confirmacao": datetime(2026, 11, 20, 10, 0),
                "data_prevista_devolucao": date(2026, 11, 27),
                "responsavel_confirmacao": material.grupo.codigo,
            })
            if status == StatusEmprestimo.DEVOLVIDO:
                comum["data_devolucao"] = datetime(2026, 11, 30, 8, 0)
            return Emprestimo(**comum)

        self.pendente = emprestimo(self.usuario, self.material, 15)
        self.ativo = emprestimo(self.usuario, self.material, 16, StatusEmprestimo.ATIVO)
        self.devolvido_com_multa = emprestimo(
            self.usuario, self.material, 17, StatusEmprestimo.DEVOLVIDO
        )
        self.outra_pessoa = emprestimo(self.outro_usuario, self.material, 18)
        self.outro_material = emprestimo(
            self.usuario, self.material_outro_grupo, 19
        )

        self.repo = Mock()
        self.repo.select_emprestimo.return_value = self.pendente
        self.repo.list_emprestimos_usuario.return_value = [
            self.pendente, self.ativo, self.devolvido_com_multa
        ]
        self.repo.list_emprestimos_pendentes.return_value = [self.pendente]
        self.controller = SistemaEmprestimosController(Mock(), Mock(), self.repo)

    def assert_sem_escrita(self):
        """Consultas nunca devem realizar transações de alteração."""
        for metodo in (
            "registrar_solicitacao", "aprovar_solicitacao",
            "recusar_solicitacao", "registrar_devolucao"
        ):
            getattr(self.repo, metodo).assert_not_called()

    def test_consultar_proprio_emprestimo_como_estudante(self):
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": 15}, matricula_autenticada="2026000001"
        )
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"]["status"], "PENDENTE")
        self.repo.select_emprestimo.assert_called_once_with(15)
        self.assert_sem_escrita()

    def test_consultar_emprestimo_do_grupo(self):
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": " 15 "}, codigo_grupo_autenticado=" gees "
        )
        self.assertTrue(resposta["success"])
        self.repo.select_emprestimo.assert_called_once_with(15)
        self.assert_sem_escrita()

    def test_estudante_nao_ve_emprestimo_de_outra_pessoa(self):
        self.repo.select_emprestimo.return_value = self.outra_pessoa
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": 18}, matricula_autenticada="2026000001"
        )
        self.assertFalse(resposta["success"])
        self.assertNotIn("attributes", resposta)
        self.assertIn("acesso não autorizado", resposta["error"])
        self.assert_sem_escrita()

    def test_grupo_nao_ve_emprestimo_de_outro_grupo(self):
        self.repo.select_emprestimo.return_value = self.outro_material
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": 19}, codigo_grupo_autenticado="GEES"
        )
        self.assertFalse(resposta["success"])
        self.assertNotIn("attributes", resposta)
        self.assert_sem_escrita()

    def test_consultar_exige_exatamente_um_contexto_de_conta(self):
        for kwargs in (
            {},
            {"matricula_autenticada": "2026000001", "codigo_grupo_autenticado": "GEES"},
        ):
            with self.subTest(kwargs=kwargs):
                resposta = self.controller.consultar_emprestimo(
                    {"id_emprestimo": 15}, **kwargs
                )
                self.assertFalse(resposta["success"])
        self.repo.select_emprestimo.assert_not_called()
        self.assert_sem_escrita()

    def test_consultar_rejeita_identidades_invalidas(self):
        for kwargs in (
            {"matricula_autenticada": "20260001"},
            {"codigo_grupo_autenticado": "GEES!"},
            {"matricula_autenticada": None, "codigo_grupo_autenticado": ""},
        ):
            with self.subTest(kwargs=kwargs):
                resposta = self.controller.consultar_emprestimo(
                    {"id_emprestimo": 15}, **kwargs
                )
                self.assertFalse(resposta["success"])
        self.repo.select_emprestimo.assert_not_called()

    def test_consultar_rejeita_dados_e_id_invalidos(self):
        for dados in (None, {}, {"id_emprestimo": 0}, {"id_emprestimo": "abc"}, {"id_emprestimo": True}):
            with self.subTest(dados=dados):
                resposta = self.controller.consultar_emprestimo(
                    dados, matricula_autenticada="2026000001"
                )
                self.assertFalse(resposta["success"])
        self.repo.select_emprestimo.assert_not_called()

    def test_consultar_nao_encontrado(self):
        self.repo.select_emprestimo.return_value = None
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": 999}, matricula_autenticada="2026000001"
        )
        self.assertFalse(resposta["success"])
        self.assertIn("não encontrado", resposta["error"])

    def test_consultar_erro_no_repositorio(self):
        self.repo.select_emprestimo.side_effect = RuntimeError("Falha do banco")
        resposta = self.controller.consultar_emprestimo(
            {"id_emprestimo": 15}, codigo_grupo_autenticado="GEES"
        )
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível consultar o empréstimo.")

    def test_listar_historico_do_estudante(self):
        resposta = self.controller.listar_emprestimos_usuario("2026000001")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 3)
        self.assertEqual(
            [item["status"] for item in resposta["message"]["attributes"]],
            ["PENDENTE", "ATIVO", "DEVOLVIDO"],
        )
        self.repo.list_emprestimos_usuario.assert_called_once_with("2026000001")
        self.assert_sem_escrita()

    def test_listar_historico_vazio_e_resposta_valida(self):
        self.repo.list_emprestimos_usuario.return_value = []
        resposta = self.controller.listar_emprestimos_usuario("2026000001")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 0)
        self.assertEqual(resposta["message"]["attributes"], [])

    def test_listar_historico_rejeita_matricula_nao_autenticada(self):
        for matricula in (None, "123", "", 2026000001):
            with self.subTest(matricula=matricula):
                resposta = self.controller.listar_emprestimos_usuario(matricula)
                self.assertFalse(resposta["success"])
        self.repo.list_emprestimos_usuario.assert_not_called()

    def test_listar_historico_nao_vaza_registro_de_outro_estudante(self):
        self.repo.list_emprestimos_usuario.return_value = [self.pendente, self.outra_pessoa]
        resposta = self.controller.listar_emprestimos_usuario("2026000001")
        self.assertFalse(resposta["success"])
        self.assertNotIn("message", resposta)

    def test_listar_historico_rejeita_retorno_invalido(self):
        self.repo.list_emprestimos_usuario.return_value = None
        resposta = self.controller.listar_emprestimos_usuario("2026000001")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível listar os empréstimos.")

    def test_listar_pendentes_do_grupo(self):
        resposta = self.controller.listar_solicitacoes_pendentes(" gees ")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 1)
        self.assertEqual(resposta["message"]["attributes"][0]["id"], 15)
        self.repo.list_emprestimos_pendentes.assert_called_once_with("GEES")
        self.assert_sem_escrita()

    def test_listar_pendentes_vazio_e_resposta_valida(self):
        self.repo.list_emprestimos_pendentes.return_value = []
        resposta = self.controller.listar_solicitacoes_pendentes("GEES")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"], [])

    def test_listar_pendentes_rejeita_grupo_sem_autenticacao(self):
        resposta = self.controller.listar_solicitacoes_pendentes(None)
        self.assertFalse(resposta["success"])
        self.repo.list_emprestimos_pendentes.assert_not_called()

    def test_listar_pendentes_nao_expoe_outro_grupo(self):
        self.repo.list_emprestimos_pendentes.return_value = [self.outro_material]
        resposta = self.controller.listar_solicitacoes_pendentes("GEES")
        self.assertFalse(resposta["success"])
        self.assertNotIn("message", resposta)

    def test_listar_pendentes_nao_expoe_emprestimos_ativos(self):
        self.repo.list_emprestimos_pendentes.return_value = [self.ativo]
        resposta = self.controller.listar_solicitacoes_pendentes("GEES")
        self.assertFalse(resposta["success"])
        self.assertNotIn("message", resposta)

    def test_listar_pendentes_erro_no_repositorio(self):
        self.repo.list_emprestimos_pendentes.side_effect = RuntimeError("Falha")
        resposta = self.controller.listar_solicitacoes_pendentes("GEES")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível listar as solicitações.")

    def test_listar_pendencias_retorna_multa_apos_devolucao(self):
        # Empréstimo devolvido em 30/11, vencimento 27/11: três dias.
        resposta = self.controller.listar_pendencias_usuario("2026000001")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 1)
        self.assertEqual(resposta["message"]["attributes"][0]["id"], 17)
        self.assertEqual(resposta["message"]["attributes"][0]["multa_calculada"], "6.00")
        self.assertEqual(resposta["message"]["total_multa_calculada"], "6.00")
        self.assert_sem_escrita()

    def test_listar_pendencias_vazio(self):
        self.repo.list_emprestimos_usuario.return_value = [self.pendente]
        resposta = self.controller.listar_pendencias_usuario("2026000001")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"], [])
        self.assertEqual(resposta["message"]["total_multa_calculada"], "0.00")

    def test_listar_pendencias_inclui_ativo_atrasado(self):
        # Empréstimo vencido há muitos anos: permanece uma multa provisória.
        self.repo.list_emprestimos_usuario.return_value = [self.ativo]
        self.ativo = Emprestimo(
            usuario=self.usuario, material=self.material, id=16,
            status=StatusEmprestimo.ATIVO,
            data_solicitacao=datetime(2020, 1, 1, 9),
            data_confirmacao=datetime(2020, 1, 1, 10),
            data_prevista_devolucao=date(2020, 1, 2),
            responsavel_confirmacao="GEES",
        )
        self.repo.list_emprestimos_usuario.return_value = [self.ativo]
        resposta = self.controller.listar_pendencias_usuario("2026000001")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 1)
        self.assertGreater(float(resposta["message"]["total_multa_calculada"]), 0)

    def test_listar_pendencias_rejeita_dados_de_outra_pessoa(self):
        self.repo.list_emprestimos_usuario.return_value = [self.outra_pessoa]
        resposta = self.controller.listar_pendencias_usuario("2026000001")
        self.assertFalse(resposta["success"])
        self.assertNotIn("message", resposta)

    def test_listar_pendencias_rejeita_usuario_nao_autenticado(self):
        resposta = self.controller.listar_pendencias_usuario("000")
        self.assertFalse(resposta["success"])
        self.repo.list_emprestimos_usuario.assert_not_called()

    def test_listar_pendencias_erro_no_repositorio(self):
        self.repo.list_emprestimos_usuario.side_effect = RuntimeError("Falha")
        resposta = self.controller.listar_pendencias_usuario("2026000001")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível consultar as pendências.")


if __name__ == "__main__":
    unittest.main()