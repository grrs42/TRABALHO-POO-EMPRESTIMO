import unittest

from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.entities.jaleco import Jaleco
from src.models.entities.livro import Livro
from src.models.entities.calculadora import Calculadora
from src.models.entities.outro_material import OutroMaterial
from src.models.factories.material_factory import MaterialFactory


class TestMateriaisEspecializados(unittest.TestCase):

    def setUp(self) -> None:
        self.grupo = GrupoResponsavel(
            "GEES", "Grêmio de Engenharia", id=1
        )

        self.tipo_jaleco = TipoMaterial(
            "JAL", "Jaleco", id=1
        )

        self.tipo_livro = TipoMaterial(
            "LIV", "Livro", id=2
        )

    def test_operacao_comum_em_duas_subclasses(self):
        materiais: list[Material] = [
            Jaleco(
                self.tipo_jaleco,
                self.grupo,
                tamanho=" m "
            ),
            Livro(
                self.tipo_livro,
                self.grupo,
                titulo="Cálculo I",
                editora="LTC"
            )
        ]

        for material in materiais:
            material.validar_dados_especificos()

        fichas = [
            material.to_dict()
            for material in materiais
        ]

        self.assertEqual(fichas[0]["tamanho"], "M")
        self.assertEqual(fichas[1]["titulo"], "Cálculo I")
        self.assertEqual(fichas[1]["editora"], "LTC")
        
    """Esse teste verifica que Material não pode ser instanciada diretamente."""
    def test_material_abstrato_nao_pode_ser_instanciado(self):
        tipo = TipoMaterial(
            sigla="OUT",
            nome="Outros"
        )

        grupo = GrupoResponsavel(
            codigo="TST",
            nome="Grupo de Teste"
        )

        with self.assertRaises(TypeError):
            Material(
                tipo=tipo,
                grupo=grupo
            )
            
    def test_jaleco_rejeita_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            Jaleco(
                self.tipo_jaleco,
                self.grupo,
                tamanho="gigante"
            )

    def test_livro_rejeita_editora_em_branco(self):
        with self.assertRaises(ValueError):
            Livro(
                self.tipo_livro,
                self.grupo,
                titulo="Álgebra Linear",
                editora="  "
            )

    def test_disponibilidade_do_jaleco(self):
        jaleco = Jaleco(
            self.tipo_jaleco,
            self.grupo,
            tamanho="P"
        )

        self.assertTrue(
            jaleco.verificar_disponibilidade()
        )

        jaleco.marcar_indisponivel()

        self.assertFalse(
            jaleco.verificar_disponibilidade()
        )
        
    def test_calculadora_valida_modelo(self):
        tipo = TipoMaterial("CAL", "Calculadora", id=3)

        calculadora = Calculadora(
            tipo=tipo,
            grupo=self.grupo,
            modelo="FX-82MS"
        )

        self.assertEqual(
            calculadora.detalhes_especificos(),
            {"modelo": "FX-82MS"}
        )

        with self.assertRaises(ValueError):
            Calculadora(
                tipo=tipo,
                grupo=self.grupo,
                modelo=" "
            )
            
    
    """Testes para OutroMaterial"""
    def test_outro_material_valida_descricao(self):
        tipo = TipoMaterial("REG", "Régua", id=4)

        regua = OutroMaterial(
            tipo=tipo,
            grupo=self.grupo,
            descricao="Régua de 30 cm"
        )

        self.assertEqual(
            regua.detalhes_especificos(),
            {"descricao": "Régua de 30 cm"}
        )

        with self.assertRaises(ValueError):
            OutroMaterial(
                tipo=tipo,
                grupo=self.grupo,
                descricao=""
            )

    def test_polimorfismo_em_quatro_subclasses(self):
        tipo_calculadora = TipoMaterial(
            "CAL", "Calculadora", id=3
        )

        tipo_regua = TipoMaterial(
            "REG", "Régua", id=4
        )

        materiais: list[Material] = [
            Jaleco(self.tipo_jaleco, self.grupo, "M"),
            Livro(self.tipo_livro, self.grupo, "Cálculo I", "LTC"),
            Calculadora(tipo_calculadora, self.grupo, "FX-82MS"),
            OutroMaterial(tipo_regua, self.grupo, "Régua de 30 cm")
        ]

        for material in materiais:
            material.validar_dados_especificos()

        fichas = [material.to_dict() for material in materiais]

        self.assertEqual(fichas[0]["tamanho"], "M")
        self.assertEqual(fichas[1]["editora"], "LTC")
        self.assertEqual(fichas[2]["modelo"], "FX-82MS")
        self.assertEqual(fichas[3]["descricao"], "Régua de 30 cm")
        
    def test_tipo_material_com_especializacao(self):
        tipo = TipoMaterial(
            sigla="JAL",
            nome="Jaleco",
            especializacao="JALECO"
        )

        self.assertEqual(
            tipo.especializacao,
            "JALECO"
        )
        self.assertEqual(
            tipo.to_dict()["especializacao"],
            "JALECO"
        )


    def test_tipo_material_rejeita_especializacao_invalida(self):
        with self.assertRaises(ValueError):
            TipoMaterial(
                sigla="TES",
                nome="Teste",
                especializacao="DESCONHECIDO"
            )

    def test_fabrica_cria_jaleco(self):
        tipo = TipoMaterial(
            "JAL", "Jaleco",
            especializacao="JALECO"
        )

        material = MaterialFactory.criar(
            tipo=tipo,
            grupo=self.grupo,
            dados_especificos={"tamanho": "M"},
            marca="Marca A"
        )

        self.assertIsInstance(material, Jaleco)
        self.assertEqual(material.tamanho, "M")
        self.assertEqual(material.marca, "Marca A")


    def test_fabrica_cria_outro_material(self):
        tipo = TipoMaterial(
            "REG", "Régua",
            especializacao="OUTRO"
        )

        material = MaterialFactory.criar(
            tipo=tipo,
            grupo=self.grupo,
            dados_especificos={
                "descricao": "Régua metálica de 30 cm"
            }
        )
        self.assertIsInstance(material, OutroMaterial)


    def test_fabrica_rejeita_campos_incorretos(self):
        tipo = TipoMaterial(
            "JAL", "Jaleco",
            especializacao="JALECO"
        )

        with self.assertRaises(ValueError):
            MaterialFactory.criar(
                tipo=tipo,
                grupo=self.grupo,
                dados_especificos={"editora": "LTC"}
            )


    def test_fabrica_rejeita_valor_invalido(self):
        tipo = TipoMaterial(
            "JAL", "Jaleco",
            especializacao="JALECO"
        )

        with self.assertRaises(ValueError):
            MaterialFactory.criar(
                tipo=tipo,
                grupo=self.grupo,
                dados_especificos={"tamanho": "Gigante"}
            )

if __name__ == "__main__":
    unittest.main()