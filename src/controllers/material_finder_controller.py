
from typing import Dict
from src.models.entities.material import Material
from src.models.repositories.materiais_repository import MateriaisRepository


class MaterialFinderController:
    """
    Coordena a consulta de exemplares de materiais.

    Recebe o código informado pela view, valida seu
    formato inicial e consulta o MateriaisRepository.

    Retorna os dados do exemplar encontrado, incluindo
    sua categoria, grupo responsável, atributos
    específicos e disponibilidade.

    A operação realiza somente leitura dos registros.
    """

    def __init__(self, repository: MateriaisRepository) -> None:
        """
        Inicializa o Controller de consulta de materiais.
        """
        self.__repository = repository

    def finder(self, material_finder_informations: Dict) -> Dict:
        """
        Consulta um exemplar pelo código individual.
        """
        try:
            self._validate_fields(material_finder_informations)
            material = self.__repository.select_material(
                material_finder_informations["codigo"].upper()
            )
            if material is None:
                raise Exception(' Material não encontrado!')
            response = self.__format_response(material)
            return {"success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def _validate_fields(self, material_finder_informations: Dict) -> None:
        """
        Realiza a validação inicial do código informado.

        A verificação da existência do exemplar é
        realizada posteriormente pelo repositório.
        """
        if not material_finder_informations["codigo"].replace("-", "").isalnum():
            raise Exception(' Código do material incorreto!')

    def __format_response(self, material: Material) -> Dict:
        return {
            "count": 1,
            "type": "Material",
            "attributes": material.to_dict()
        }