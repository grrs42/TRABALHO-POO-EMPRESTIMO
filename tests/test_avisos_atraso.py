import os
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.entities.calculadora import Calculadora
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.usuario import Usuario
from src.models.services.notificador_simulado import NotificadorEmailSimulado


def criar_ativo(id: int, vencimento: date, grupo_codigo: str = "GEES") -> Emprestimo:
    grupo = GrupoResponsavel(grupo_codigo, "Grupo", id=1)
    tipo = TipoMaterial("CAL", "Calculadora", id=1, especializacao="CALCULADORA")
    material = Calculadora(tipo=tipo, grupo=grupo, modelo="FX-82", codigo=f"CAL-00{id}", id=id)
    confirmacao = datetime.combine(vencimento - timedelta(days=7), time(10, 0))
    return Emprestimo(
        usuario=Usuario("2026000001", "Estudante Exemplo"),
        material=material,
        id=id,
        status=StatusEmprestimo.ATIVO,
        data_solicitacao=confirmacao - timedelta(hours=1),
        data_confirmacao=confirmacao,
        data_prevista_devolucao=vencimento,
        responsavel_confirmacao=grupo_codigo,
    )


class TestNotificadorEmailSimulado(unittest.TestCase):
    def setUp(self):
        pasta = tempfile.mkdtemp()
        self.caminho = os.path.join(pasta, "avisos.log")
        self.notificador = NotificadorEmailSimulado(self.caminho)

    def test_gera_aviso_para_atrasado(self):
        emprestimo = criar_ativo(1, date(2026, 11, 27))
        mensagem = self.notificador.enviar_aviso_atraso(emprestimo, hoje=date(2026, 11, 30))
        self.assertIn("3 dia(s) de atraso", mensagem)
        self.assertIn("R$ 6.00", mensagem)
        with open(self.caminho, encoding="utf-8") as arquivo:
            self.assertEqual(arquivo.read().strip(), mensagem)

    def test_nao_avisa_no_dia_do_vencimento(self):
        emprestimo = criar_ativo(1, date(2026, 11, 27))
        with self.assertRaises(ValueError):
            self.notificador.enviar_aviso_atraso(emprestimo, hoje=date(2026, 11, 27))
        self.assertFalse(os.path.exists(self.caminho))


class TestAvisosNoController(unittest.TestCase):
    def setUp(self):
        hoje = date.today()
        self.atrasado = criar_ativo(1, date(hoje.year - 1, 1, 1))
        self.no_prazo = criar_ativo(2, date(hoje.year + 1, 1, 1))
        self.repo = Mock()
        self.repo.list_emprestimos_ativos.return_value = [self.atrasado, self.no_prazo]
        self.notificador = Mock()
        self.controller = SistemaEmprestimosController(
            Mock(), Mock(), self.repo, self.notificador
        )

    def test_lista_ativos_do_grupo(self):
        resposta = self.controller.listar_emprestimos_ativos("gees")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 2)
        self.repo.list_emprestimos_ativos.assert_called_once_with("GEES")

    def test_avisa_somente_atrasados(self):
        resposta = self.controller.gerar_avisos_atraso("GEES")
        self.assertTrue(resposta["success"])
        self.assertEqual(resposta["message"]["count"], 1)
        self.notificador.enviar_aviso_atraso.assert_called_once_with(self.atrasado)

    def test_nao_expoe_ativos_de_outro_grupo(self):
        self.repo.list_emprestimos_ativos.return_value = [criar_ativo(3, date.today(), "LABFIS")]
        resposta = self.controller.listar_emprestimos_ativos("GEES")
        self.assertFalse(resposta["success"])

    def test_rejeita_grupo_nao_autenticado(self):
        self.assertFalse(self.controller.gerar_avisos_atraso(None)["success"])
        self.repo.list_emprestimos_ativos.assert_not_called()
        self.notificador.enviar_aviso_atraso.assert_not_called()

    def test_sem_notificador_configurado(self):
        controller = SistemaEmprestimosController(Mock(), Mock(), self.repo)
        self.assertFalse(controller.gerar_avisos_atraso("GEES")["success"])


if __name__ == "__main__":
    unittest.main()
