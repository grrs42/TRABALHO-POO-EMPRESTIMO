import unittest
from datetime import date, datetime
from decimal import Decimal

from src.models.entities.calculadora import Calculadora
from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.usuario import Usuario


class TestMultaEmprestimo(unittest.TestCase):
    def setUp(self):
        usuario = Usuario("2026000001", "Estudante Exemplo")
        material = Calculadora(
            tipo=TipoMaterial("CAL", "Calculadora", id=1, especializacao="CALCULADORA"),
            grupo=GrupoResponsavel("GEES", "Grêmio de Engenharia", id=1),
            modelo="FX-82", codigo="CAL-001", id=7,
        )
        self.solicitado_em = datetime(2026, 11, 20, 9, 0)
        self.confirmado_em = datetime(2026, 11, 20, 10, 0)
        self.emprestimo = Emprestimo(
            usuario=usuario, material=material,
            data_solicitacao=self.solicitado_em,
        )

    def aprovar(self, prazo=7):
        self.emprestimo.aprovar(prazo, "GEES", self.confirmado_em)

    def test_pendente_nao_tem_multa(self):
        self.assertEqual(self.emprestimo.dias_atraso(date(2027, 1, 1)), 0)
        self.assertEqual(self.emprestimo.calcular_multa(date(2027, 1, 1)), Decimal("0.00"))

    def test_recusada_nao_tem_multa(self):
        self.emprestimo.recusar()
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.RECUSADO)
        self.assertEqual(self.emprestimo.calcular_multa(date(2027, 1, 1)), Decimal("0.00"))

    def test_ativo_antes_e_no_vencimento_sem_multa(self):
        self.aprovar()
        for data in (date(2026, 11, 26), date(2026, 11, 27)):
            with self.subTest(data=data):
                self.assertEqual(self.emprestimo.dias_atraso(data), 0)
                self.assertEqual(self.emprestimo.calcular_multa(data), Decimal("0.00"))

    def test_ativo_um_dia_de_atraso(self):
        self.aprovar()
        self.assertEqual(self.emprestimo.dias_atraso(date(2026, 11, 28)), 1)
        self.assertEqual(self.emprestimo.calcular_multa(date(2026, 11, 28)), Decimal("2.00"))

    def test_ativo_tres_dias_de_atraso(self):
        self.aprovar()
        self.assertEqual(self.emprestimo.dias_atraso(date(2026, 11, 30)), 3)
        self.assertEqual(self.emprestimo.calcular_multa(date(2026, 11, 30)), Decimal("6.00"))

    def test_devolucao_no_prazo_sem_multa(self):
        self.aprovar()
        self.emprestimo.registrar_devolucao(datetime(2026, 11, 27, 23, 59))
        self.assertEqual(self.emprestimo.dias_atraso(date(2027, 1, 1)), 0)
        self.assertEqual(self.emprestimo.calcular_multa(), Decimal("0.00"))

    def test_devolucao_atrasada_congela_valor_da_multa(self):
        self.aprovar()
        self.emprestimo.registrar_devolucao(datetime(2026, 11, 30, 9, 0))
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.DEVOLVIDO)
        self.assertEqual(self.emprestimo.dias_atraso(), 3)
        self.assertEqual(self.emprestimo.calcular_multa(), Decimal("6.00"))
        self.assertEqual(self.emprestimo.calcular_multa(date(2027, 3, 1)), Decimal("6.00"))
        self.assertFalse(self.emprestimo.esta_atrasado(date(2027, 3, 1)))

    def test_devolucao_antes_do_vencimento_nao_gera_dias_negativos(self):
        self.aprovar()
        self.emprestimo.registrar_devolucao(datetime(2026, 11, 22, 8, 0))
        self.assertEqual(self.emprestimo.dias_atraso(), 0)
        self.assertEqual(self.emprestimo.calcular_multa(), Decimal("0.00"))

    def test_data_referencia_invalida_rejeitada(self):
        self.aprovar()
        with self.assertRaises(TypeError):
            self.emprestimo.dias_atraso("2026-11-28")
        with self.assertRaises(TypeError):
            self.emprestimo.calcular_multa(datetime(2026, 11, 28, 9, 0))
        self.assertEqual(self.emprestimo.status, StatusEmprestimo.ATIVO)

    def test_to_dict_exibe_multa_apos_devolucao(self):
        self.aprovar()
        self.emprestimo.registrar_devolucao(datetime(2026, 11, 29, 12, 0))
        dados = self.emprestimo.to_dict()
        self.assertEqual(dados["dias_atraso"], 2)
        self.assertEqual(dados["multa_calculada"], "4.00")
        self.assertEqual(dados["status"], "DEVOLVIDO")

    def test_virada_de_ano_conta_dias_corridos(self):
        self.emprestimo = Emprestimo(
            usuario=self.emprestimo.usuario, material=self.emprestimo.material,
            data_solicitacao=datetime(2026, 12, 29, 8, 0),
        )
        self.emprestimo.aprovar(1, "GEES", datetime(2026, 12, 30, 8, 0))
        self.assertEqual(self.emprestimo.data_prevista_devolucao, date(2026, 12, 31))
        self.assertEqual(self.emprestimo.dias_atraso(date(2027, 1, 2)), 2)
        self.assertEqual(self.emprestimo.calcular_multa(date(2027, 1, 2)), Decimal("4.00"))

    def test_reconstrucao_devolvido_preserva_multa(self):
        self.aprovar()
        self.emprestimo.registrar_devolucao(datetime(2026, 11, 30, 12, 0))
        reconstruido = Emprestimo(
            usuario=self.emprestimo.usuario,
            material=self.emprestimo.material,
            id=15,
            status=StatusEmprestimo.DEVOLVIDO,
            data_solicitacao=self.emprestimo.data_solicitacao,
            data_confirmacao=self.emprestimo.data_confirmacao,
            data_prevista_devolucao=self.emprestimo.data_prevista_devolucao,
            data_devolucao=self.emprestimo.data_devolucao,
            responsavel_confirmacao=self.emprestimo.responsavel_confirmacao,
        )
        self.assertEqual(reconstruido.dias_atraso(), 3)
        self.assertEqual(reconstruido.calcular_multa(), Decimal("6.00"))


if __name__ == "__main__":
    unittest.main()