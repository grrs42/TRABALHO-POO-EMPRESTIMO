import unittest
from unittest.mock import Mock

from src.controllers.usuario_register_controller import UsuarioRegisterController
from src.controllers.usuario_finder_controller import UsuarioFinderController
from src.models.entities.usuario import Usuario


class TestUsuarioRegisterController(unittest.TestCase):
    def setUp(self):
        self.repo = Mock()
        self.repo.select_usuario.return_value = None
        self.controller = UsuarioRegisterController(self.repo)
        self.dados = {
            "nome": "Estudante Exemplo",
            "matricula": "2026000001",
            "senha": "segredo123",
        }

    def test_cadastro_valido_grava_usuario_e_conta(self):
        resposta = self.controller.register(self.dados)
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["attributes"]["matricula"], "2026000001")
        usuario, conta = self.repo.insert_usuario.call_args.args
        self.assertEqual(usuario.matricula, "2026000001")
        self.assertEqual(conta.login, "2026000001")
        self.assertTrue(conta.verificar_senha("segredo123"))

    def test_rejeita_matricula_com_9_digitos(self):
        self.dados["matricula"] = "202600000"
        self.assertFalse(self.controller.register(self.dados)["success"])
        self.repo.insert_usuario.assert_not_called()

    def test_rejeita_matricula_com_letras(self):
        self.dados["matricula"] = "20260000AB"
        self.assertFalse(self.controller.register(self.dados)["success"])
        self.repo.insert_usuario.assert_not_called()

    def test_rejeita_matricula_duplicada(self):
        self.repo.select_usuario.return_value = Usuario("2026000001", "Outra")
        resposta = self.controller.register(self.dados)
        self.assertFalse(resposta["success"])
        self.assertIn("já cadastrada", resposta["error"])
        self.repo.insert_usuario.assert_not_called()

    def test_rejeita_senha_curta(self):
        self.dados["senha"] = "123"
        self.assertFalse(self.controller.register(self.dados)["success"])
        self.repo.insert_usuario.assert_not_called()


class TestUsuarioFinderController(unittest.TestCase):
    def test_busca_exige_10_digitos(self):
        repo = Mock()
        controller = UsuarioFinderController(repo)
        self.assertFalse(controller.finder({"matricula": "123"})["success"])
        repo.select_usuario.assert_not_called()


if __name__ == "__main__":
    unittest.main()
