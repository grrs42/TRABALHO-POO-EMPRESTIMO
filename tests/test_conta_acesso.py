import unittest
from unittest.mock import Mock

from src.controllers.login_controller import LoginController
from src.models.entities.conta_acesso import ContaAcesso


class TestContaAcesso(unittest.TestCase):
    def test_senha_correta_e_incorreta(self):
        conta = ContaAcesso.criar_para_estudante("2026000001", "segredo123")
        self.assertTrue(conta.verificar_senha("segredo123"))
        self.assertFalse(conta.verificar_senha("segredo124"))
        self.assertFalse(conta.verificar_senha(""))

    def test_senha_nao_e_guardada_em_texto(self):
        conta = ContaAcesso.criar_para_estudante("2026000001", "segredo123")
        self.assertNotIn("segredo123", conta.senha_hash)
        self.assertEqual(len(conta.senha_hash), 64)

    def test_salt_diferente_gera_hash_diferente(self):
        a = ContaAcesso.criar_para_estudante("2026000001", "segredo123")
        b = ContaAcesso.criar_para_estudante("2026000002", "segredo123")
        self.assertNotEqual(a.salt, b.salt)
        self.assertNotEqual(a.senha_hash, b.senha_hash)

    def test_rejeita_senha_curta(self):
        with self.assertRaises(ValueError):
            ContaAcesso.criar_para_estudante("2026000001", "12345")

    def test_identidade_por_tipo(self):
        estudante = ContaAcesso.criar_para_estudante("2026000001", "segredo123")
        senha_hash, salt = ContaAcesso.gerar_hash("segredo123")
        grupo = ContaAcesso("GEES", ContaAcesso.GRUPO, senha_hash, salt, grupo_codigo="GEES")
        self.assertEqual(estudante.identidade, "2026000001")
        self.assertEqual(grupo.identidade, "GEES")

    def test_rejeita_conta_com_dois_vinculos(self):
        senha_hash, salt = ContaAcesso.gerar_hash("segredo123")
        with self.assertRaises(ValueError):
            ContaAcesso(
                "GEES", ContaAcesso.GRUPO, senha_hash, salt,
                usuario_matricula="2026000001", grupo_codigo="GEES",
            )


class TestLoginController(unittest.TestCase):
    def setUp(self):
        senha_hash, salt = ContaAcesso.gerar_hash("gees1234")
        self.conta_grupo = ContaAcesso(
            "GEES", ContaAcesso.GRUPO, senha_hash, salt, grupo_codigo="GEES"
        )
        self.repo = Mock()
        self.repo.select_conta.return_value = self.conta_grupo
        self.controller = LoginController(self.repo)

    def test_login_valido_retorna_identidade(self):
        resposta = self.controller.autenticar({"login": " gees ", "senha": "gees1234"})
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"], {"tipo": "GRUPO", "identidade": "GEES"})
        self.repo.select_conta.assert_called_once_with("GEES")

    def test_senha_errada_e_login_inexistente_tem_mesma_mensagem(self):
        errada = self.controller.autenticar({"login": "GEES", "senha": "outra123"})
        self.repo.select_conta.return_value = None
        inexistente = self.controller.autenticar({"login": "XPTO", "senha": "gees1234"})
        self.assertFalse(errada["success"])
        self.assertFalse(inexistente["success"])
        self.assertEqual(errada["error"], inexistente["error"])

    def test_dados_invalidos(self):
        self.assertFalse(self.controller.autenticar(None)["success"])
        self.assertFalse(self.controller.autenticar({"login": "GEES"})["success"])

    def test_erro_do_banco(self):
        self.repo.select_conta.side_effect = RuntimeError("Falha")
        resposta = self.controller.autenticar({"login": "GEES", "senha": "gees1234"})
        self.assertEqual(resposta["error"], "Não foi possível realizar o login.")


if __name__ == "__main__":
    unittest.main()
