from typing import Dict
from src.models.entities.tipo_material import TipoMaterial
from src.models.repositories.tipos_material_repository import TiposMaterialRepository

class TipoMaterialRegisterController():
    def __init__(self, repository: TiposMaterialRepository) -> None:
        self.__repository = repository
    def register(self, new_tipo_informations: Dict) -> Dict:
        try:
            self._validate_fields(new_tipo_informations)
            nome = new_tipo_informations["nome"].strip()
            tipo = TipoMaterial(TipoMaterial.gerar_sigla(nome), nome)
            if len(tipo.sigla) < 3:
                raise Exception(' O nome do tipo precisa ter pelo menos 3 letras!')
            existente = self.__repository.select_tipo(tipo.sigla)
            if existente is not None:
                raise Exception(f' Já existe um tipo com a sigla {tipo.sigla} ({existente.nome})!')
            saved_tipo = self.__repository.insert_tipo(tipo)
            response = self.__format_response(saved_tipo)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
    def _validate_fields(self, new_tipo_informations: Dict) -> None:
        if not new_tipo_informations["nome"].replace(" ", "").isalpha():
            raise Exception(' Nome do tipo de material incorreto!')
    def __format_response(self, tipo: TipoMaterial) -> Dict:
        return {
            "count": 1,
            "type": "Tipo de Material",
            "attributes": tipo.to_dict()
        }
