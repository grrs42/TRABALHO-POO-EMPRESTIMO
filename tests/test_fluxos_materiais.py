
import unittest
from unittest.mock import Mock

from src.controllers.material_register_controller import MaterialRegisterController
from src.controllers.material_finder_controller import MaterialFinderController
from src.models.entities.jaleco import Jaleco
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel
from src.models.factories.material_factory import MaterialFactory


class TestFluxosMateriais(unittest.TestCase):
    """Testa cadastro e consulta com persistência simulada."""

    def setUp(self):
        self.tipo = TipoMaterial(
            sigla="JAL",
            nome="Jaleco",
            id=1,
            especializacao="JALECO"
        )

        self.grupo = GrupoResponsavel(
            codigo="GEES",
            nome="Grupo de Teste",
            id=1
        )

        # Simula os repositórios sem acessar o PostgreSQL.
        self.materiais_repo = Mock()
        self.tipos_repo = Mock()
        self.grupos_repo = Mock()

        self.tipos_repo.select_tipo.return_value = self.tipo
        self.grupos_repo.select_grupo.return_value = self.grupo

        # Armazena os materiais apenas durante cada teste.
        self.banco_simulado = {}

        self.materiais_repo.insert_material.side_effect = self._salvar
        self.materiais_repo.select_material.side_effect = (
            self.banco_simulado.get
        )

        self.cadastro = MaterialRegisterController(
            self.materiais_repo,
            self.tipos_repo,
            self.grupos_repo
        )

        self.consulta = MaterialFinderController(
            self.materiais_repo
        )

    def _salvar(self, material):
        """Simula a persistência de um exemplar válido."""
        codigo = f"JAL-{len(self.banco_simulado) + 1:03d}"

        salvo = MaterialFactory.criar(
            tipo=material.tipo,
            grupo=material.grupo,
            dados_especificos=material.detalhes_especificos(),
            marca=material.marca,
            codigo=codigo,
            id=len(self.banco_simulado) + 1
        )

        self.banco_simulado[codigo] = salvo
        return salvo

    def test_cadastro_valido(self):
        resposta = self.cadastro.register({
            "tipo": "JAL",
            "grupo": "GEES",
            "marca": "Marca X",
            "dados_especificos": {"tamanho": "M"}
        })

        self.assertTrue(resposta["success"], resposta)
        self.assertIn("JAL-001", self.banco_simulado)

        material = self.banco_simulado["JAL-001"]

        self.assertIsInstance(material, Jaleco)
        self.assertEqual(material.tamanho, "M")
        self.assertEqual(material.marca, "Marca X")

        self.materiais_repo.insert_material.assert_called_once()

    def test_cadastro_invalido_preserva_estado(self):
        quantidade_antes = len(self.banco_simulado)

        resposta = self.cadastro.register({
            "tipo": "JAL",
            "grupo": "GEES",
            "marca": "Marca X",
            "dados_especificos": {"tamanho": "Gigante"}
        })

        self.assertFalse(resposta["success"])
        self.assertEqual(
            len(self.banco_simulado),
            quantidade_antes
        )

        # O repositório não deve receber uma tentativa de INSERT.
        self.materiais_repo.insert_material.assert_not_called()

    def test_consulta_material_existente(self):
        material = MaterialFactory.criar(
            tipo=self.tipo,
            grupo=self.grupo,
            dados_especificos={"tamanho": "M"},
            marca="Marca X",
            codigo="JAL-001",
            id=1
        )

        self.banco_simulado["JAL-001"] = material

        resposta = self.consulta.finder({
            "codigo": "jal-001"
        })

        self.assertTrue(resposta["success"], resposta)

        atributos = resposta["message"]["attributes"]

        self.assertEqual(atributos["codigo"], "JAL-001")
        self.assertEqual(atributos["tamanho"], "M")
        self.assertEqual(atributos["marca"], "Marca X")

        self.materiais_repo.select_material.assert_called_once_with(
            "JAL-001"
        )

    def test_consulta_material_inexistente(self):
        resposta = self.consulta.finder({
            "codigo": "JAL-999"
        })

        self.assertFalse(resposta["success"])
        self.assertEqual(len(self.banco_simulado), 0)
        self.materiais_repo.insert_material.assert_not_called()


if __name__ == "__main__":
    unittest.main()
