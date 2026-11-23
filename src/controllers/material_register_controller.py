
from typing import Dict
from src.models.entities.material import Material
from src.models.repositories.materiais_repository import MateriaisRepository
from src.models.repositories.tipos_material_repository import TiposMaterialRepository
from src.models.repositories.grupos_responsaveis_repository import GruposResponsaveisRepository
from src.models.factories.material_factory import MaterialFactory


class MaterialRegisterController:
    """
    Coordena o cadastro de exemplares de materiais acadêmicos.

    Recebe os dados enviados pela View, valida os campos
    iniciais e consulta os repositórios para identificar
    a categoria e o grupo responsável.

    Utiliza a MaterialFactory para criar o objeto da classe
    concreta correspondente à especialização do material.

    A persistência e a geração do código individual do
    exemplar são realizadas pelo MateriaisRepository.
    """

    def __init__(
        self,
        materiais_repository: MateriaisRepository,
        tipos_repository: TiposMaterialRepository,
        grupos_repository: GruposResponsaveisRepository
    ) -> None:
        self.__materiais_repository = materiais_repository
        self.__tipos_repository = tipos_repository
        self.__grupos_repository = grupos_repository

    def get_options(self) -> Dict:
        """
        Recupera as categorias e os grupos cadastrados.
        """
        try:
            options = {
                "tipos": [tipo.to_dict() for tipo in self.__tipos_repository.list_tipos()],
                "grupos": [grupo.to_dict() for grupo in self.__grupos_repository.list_grupos()]
            }
            return {"success": True, "message": options}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def register(self, new_material_informations: Dict) -> Dict:
        """
        Processa o cadastro de um exemplar de material.
        
        Etapas:
        Valida os campos iniciais.
        Verifica a existência do tipo e do grupo.
        Cria o material pela MaterialFactory.
        Solicita sua persistência ao repositório.
        Retorna as informações do exemplar salvo.

        As validações dos atributos específicos são
        realizadas pela classe concreta do material.
        """
        try:
            self._validate_fields(new_material_informations)
            tipo = self.__tipos_repository.select_tipo(new_material_informations["tipo"].upper())
            if tipo is None:
                raise Exception(' Tipo de material não encontrado!')
            grupo = self.__grupos_repository.select_grupo(new_material_informations["grupo"].upper())
            if grupo is None:
                raise Exception(' Grêmio/laboratório não encontrado!')

            material = MaterialFactory.criar(
                tipo=tipo,
                grupo=grupo,
                dados_especificos=new_material_informations[
                    "dados_especificos"
                ],
                marca=new_material_informations.get("marca")
            )
            saved_material = self.__materiais_repository.insert_material(material)
            response = self.__format_response(saved_material)
            return {"success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def _validate_fields(self, new_material_informations: Dict) -> None:
        """
        Valida os identificadores iniciais do cadastro.
        """
        tipo = new_material_informations["tipo"]
        if len(tipo) != 3 or not tipo.isalpha():
            raise Exception(' Tipo de material incorreto! Informe a sigla de 3 letras (ex: CAL).')
        if not new_material_informations["grupo"].isalnum():
            raise Exception(' Código do grêmio/laboratório incorreto!')

    def __format_response(self, material: Material) -> Dict:
        return {
            "count": 1,
            "type": "Material",
            "attributes": material.to_dict()
        }