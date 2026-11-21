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
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia de Sistemas", id=1),
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


if __name__ == "__main__":
    unittest.main()
