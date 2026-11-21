import unittest
from unittest.mock import Mock

from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.entities.calculadora import Calculadora
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.usuario import Usuario


class TestSistemaEmprestimosController(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("2026000001", "Estudante Exemplo")
        self.material = Calculadora(
            tipo=TipoMaterial(
                "CAL", "Calculadora", id=1, especializacao="CALCULADORA"
            ),
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia", id=1),
            modelo="FX-82",
            codigo="CAL-001",
            id=7,
        )
        self.usuarios_repository = Mock()
        self.materiais_repository = Mock()
        self.emprestimos_repository = Mock()
        self.usuarios_repository.select_usuario.return_value = self.usuario
        self.materiais_repository.select_material.return_value = self.material

        def simular_persistencia(emprestimo):
            # Simula a reconstrução do objeto após o INSERT no banco.
            return Emprestimo(
                usuario=emprestimo.usuario,
                material=emprestimo.material,
                id=15,
                data_solicitacao=emprestimo.data_solicitacao,
            )

        self.emprestimos_repository.registrar_solicitacao.side_effect = (
            simular_persistencia
        )
        self.controller = SistemaEmprestimosController(
            self.usuarios_repository,
            self.materiais_repository,
            self.emprestimos_repository,
        )
        self.dados = {"matricula": "2026000001", "codigo_material": "CAL-001"}

    def assert_nao_registrou(self):
        self.emprestimos_repository.registrar_solicitacao.assert_not_called()
        self.assertTrue(self.material.verificar_disponibilidade())

    def test_solicitacao_valida(self):
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 1)
        atributos = resposta["message"]["attributes"]
        self.assertEqual(atributos["id"], 15)
        self.assertEqual(atributos["status"], StatusEmprestimo.PENDENTE.value)
        self.assertEqual(atributos["matricula_usuario"], "2026000001")
        self.assertEqual(atributos["codigo_material"], "CAL-001")
        self.usuarios_repository.select_usuario.assert_called_once_with("2026000001")
        self.materiais_repository.select_material.assert_called_once_with("CAL-001")
        self.emprestimos_repository.registrar_solicitacao.assert_called_once()
        enviado = self.emprestimos_repository.registrar_solicitacao.call_args.args[0]
        self.assertIsInstance(enviado, Emprestimo)
        self.assertEqual(enviado.status, StatusEmprestimo.PENDENTE)

    def test_normaliza_espacos_e_codigo_minusculo(self):
        dados = {"matricula": " 2026000001 ", "codigo_material": " cal-001 "}
        resposta = self.controller.solicitar_emprestimo(dados)
        self.assertTrue(resposta["success"])
        self.materiais_repository.select_material.assert_called_once_with("CAL-001")

    def test_dados_nao_sao_dicionario(self):
        resposta = self.controller.solicitar_emprestimo(None)
        self.assertFalse(resposta["success"])
        self.assert_nao_registrou()

    def test_matricula_ausente(self):
        resposta = self.controller.solicitar_emprestimo({"codigo_material": "CAL-001"})
        self.assertFalse(resposta["success"])
        self.assert_nao_registrou()

    def test_matricula_curta(self):
        resposta = self.controller.solicitar_emprestimo(
            {"matricula": "20260001", "codigo_material": "CAL-001"}
        )
        self.assertFalse(resposta["success"])
        self.assert_nao_registrou()

    def test_codigo_ausente(self):
        resposta = self.controller.solicitar_emprestimo({"matricula": "2026000001"})
        self.assertFalse(resposta["success"])
        self.assert_nao_registrou()

    def test_codigo_invalido(self):
        resposta = self.controller.solicitar_emprestimo(
            {"matricula": "2026000001", "codigo_material": "CAL001"}
        )
        self.assertFalse(resposta["success"])
        self.assert_nao_registrou()

    def test_estudante_nao_encontrado(self):
        self.usuarios_repository.select_usuario.return_value = None
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertFalse(resposta["success"])
        self.assertIn("Estudante não encontrado", resposta["error"])
        self.materiais_repository.select_material.assert_not_called()
        self.assert_nao_registrou()

    def test_material_nao_encontrado(self):
        self.materiais_repository.select_material.return_value = None
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertFalse(resposta["success"])
        self.assertIn("Material não encontrado", resposta["error"])
        self.assert_nao_registrou()

    def test_material_indisponivel(self):
        self.material.marcar_indisponivel()
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertFalse(resposta["success"])
        self.assertIn("indisponível", resposta["error"])
        self.emprestimos_repository.registrar_solicitacao.assert_not_called()
        self.assertFalse(self.material.verificar_disponibilidade())

    def test_rejeicao_por_concorrencia_no_repositorio(self):
        self.emprestimos_repository.registrar_solicitacao.side_effect = ValueError(
            "Exemplar já reservado por outra solicitação."
        )
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertFalse(resposta["success"])
        self.assertIn("reservado", resposta["error"])
        self.assertTrue(self.material.verificar_disponibilidade())

    def test_erro_do_banco_retorna_falha(self):
        self.emprestimos_repository.registrar_solicitacao.side_effect = RuntimeError(
            "Falha na transação."
        )
        resposta = self.controller.solicitar_emprestimo(self.dados)
        self.assertFalse(resposta["success"])
        self.assertEqual("Não foi possível registrar a solicitação.", resposta["error"])
        self.assertTrue(self.material.verificar_disponibilidade())



class TestAprovacaoRecusaController(unittest.TestCase):
    """Testa as operações com repositórios simulados, sem Postgree"""

    def setUp(self):
        from datetime import datetime

        usuario = Usuario("2026000001", "Estudante Exemplo")
        material = Calculadora(
            tipo=TipoMaterial("CAL", "Calculadora", id=1, especializacao="CALCULADORA"),
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia de Sistemas", id=1),
            modelo="FX-82", codigo="CAL-001", id=7,
        )
        self.emprestimo = Emprestimo(
            usuario=usuario, material=material, id=15,
            data_solicitacao=datetime(2026, 11, 20, 9, 0),
        )
        self.data_confirmacao = datetime(2026, 11, 20, 10, 0)
        self.repositorio = Mock()
        self.repositorio.select_emprestimo.return_value = self.emprestimo

        def simular_aprovacao(emprestimo_id, grupo, prazo):
            self.emprestimo.aprovar(prazo, grupo, self.data_confirmacao)
            return self.emprestimo

        def simular_recusa(emprestimo_id, grupo):
            self.emprestimo.recusar()
            return self.emprestimo

        self.repositorio.aprovar_solicitacao.side_effect = simular_aprovacao
        self.repositorio.recusar_solicitacao.side_effect = simular_recusa
        self.controller = SistemaEmprestimosController(Mock(), Mock(), self.repositorio)
        self.dados_aprovacao = {"id_emprestimo": 15, "prazo_dias": 7}
        self.dados_recusa = {"id_emprestimo": 15}

    def test_aprovar_solicitacao_valida(self):
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "GEES")
        self.assertTrue(resposta["success"])
        atributos = resposta["message"]["attributes"]
        self.assertEqual(atributos["status"], "ATIVO")
        self.assertEqual(atributos["data_prevista_devolucao"], "2026-11-27")
        self.assertEqual(atributos["responsavel_confirmacao"], "GEES")
        self.repositorio.aprovar_solicitacao.assert_called_once_with(15, "GEES", 7)

    def test_recusar_solicitacao_valida(self):
        resposta = self.controller.recusar_emprestimo(self.dados_recusa, "GEES")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"]["status"], "RECUSADO")
        self.assertIsNone(self.emprestimo.data_confirmacao)
        self.repositorio.recusar_solicitacao.assert_called_once_with(15, "GEES")

    def test_aceita_id_textual_do_terminal(self):
        resposta = self.controller.aprovar_emprestimo(
            {"id_emprestimo": "15", "prazo_dias": "7"}, "gees"
        )
        self.assertTrue(resposta["success"])
        self.repositorio.aprovar_solicitacao.assert_called_once_with(15, "GEES", 7)

    def test_aprovar_rejeita_id_invalido_sem_alterar_estado(self):
        resposta = self.controller.aprovar_emprestimo(
            {"id_emprestimo": 0, "prazo_dias": 7}, "GEES"
        )
        self.assertFalse(resposta["success"])
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)
        self.repositorio.aprovar_solicitacao.assert_not_called()

    def test_aprovar_rejeita_prazo_zero(self):
        resposta = self.controller.aprovar_emprestimo(
            {"id_emprestimo": 15, "prazo_dias": 0}, "GEES"
        )
        self.assertFalse(resposta["success"])
        self.repositorio.select_emprestimo.assert_not_called()
        self.repositorio.aprovar_solicitacao.assert_not_called()

    def test_aprovar_rejeita_grupo_sem_autenticacao(self):
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, None)
        self.assertFalse(resposta["success"])
        self.repositorio.aprovar_solicitacao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_aprovar_rejeita_grupo_de_outro_material(self):
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "LABFIS")
        self.assertFalse(resposta["success"])
        self.assertIn("não pode operar", resposta["error"])
        self.repositorio.aprovar_solicitacao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_aprovar_rejeita_emprestimo_inexistente(self):
        self.repositorio.select_emprestimo.return_value = None
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("não encontrado", resposta["error"])
        self.repositorio.aprovar_solicitacao.assert_not_called()

    def test_aprovar_rejeita_solicitacao_ja_aprovada(self):
        self.emprestimo.aprovar(7, "GEES", self.data_confirmacao)
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "GEES")
        self.assertFalse(resposta["success"])
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)
        self.repositorio.aprovar_solicitacao.assert_not_called()

    def test_recusar_rejeita_grupo_de_outro_material(self):
        resposta = self.controller.recusar_emprestimo(self.dados_recusa, "LABFIS")
        self.assertFalse(resposta["success"])
        self.repositorio.recusar_solicitacao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_recusar_rejeita_solicitacao_ja_recusada(self):
        self.emprestimo.recusar()
        resposta = self.controller.recusar_emprestimo(self.dados_recusa, "GEES")
        self.assertFalse(resposta["success"])
        self.repositorio.recusar_solicitacao.assert_not_called()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.RECUSADO)

    def test_aprovar_rejeita_concorrencia_do_repositorio(self):
        self.repositorio.aprovar_solicitacao.side_effect = ValueError(
            "Solicitação processada por outra operação."
        )
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("outra operação", resposta["error"])
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_recusar_rejeita_concorrencia_do_repositorio(self):
        self.repositorio.recusar_solicitacao.side_effect = ValueError(
            "Solicitação já processada."
        )
        resposta = self.controller.recusar_emprestimo(self.dados_recusa, "GEES")
        self.assertFalse(resposta["success"])
        self.assertIn("processada", resposta["error"])
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_aprovar_erro_banco_nao_muda_estado(self):
        self.repositorio.aprovar_solicitacao.side_effect = RuntimeError(
            "Erro no banco."
        )
        resposta = self.controller.aprovar_emprestimo(self.dados_aprovacao, "GEES")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível aprovar a solicitação.")
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)

    def test_recusar_erro_banco_nao_muda_estado(self):
        self.repositorio.recusar_solicitacao.side_effect = RuntimeError(
            "Erro no banco."
        )
        resposta = self.controller.recusar_emprestimo(self.dados_recusa, "GEES")
        self.assertFalse(resposta["success"])
        self.assertEqual(resposta["error"], "Não foi possível recusar a solicitação.")
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.PENDENTE)


if __name__ == "__main__":
    unittest.main()