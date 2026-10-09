from typing import Dict
from src.models.entities.material import Material
from src.models.repositories.materiais_repository import MateriaisRepository

class MaterialFinderController():
    def __init__(self, repository: MateriaisRepository) -> None:
        self.__repository = repository
    def finder(self, material_finder_informations: Dict) -> Dict:
        try:
            self._validate_fields(material_finder_informations)
            material = self.__repository.select_material(
                material_finder_informations["codigo"].upper()
            )
            if material is None:
                raise Exception(' Material não encontrado!')
            response = self.__format_response(material)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
    def _validate_fields(self, material_finder_informations: Dict) -> None:
        if not material_finder_informations["codigo"].replace("-", "").isalnum():
            raise Exception(' Código do material incorreto!')
    def __format_response(self, material: Material) -> Dict:
        return {
            "count": 1,
            "type": "Material",
            "attributes": material.to_dict()
        }
