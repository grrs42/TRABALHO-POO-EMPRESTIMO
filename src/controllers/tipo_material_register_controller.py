
from typing import Dict
from src.models.entities.tipo_material import TipoMaterial
from src.models.repositories.tipos_material_repository import TiposMaterialRepository


class TipoMaterialRegisterController:
    """
    Coordena o cadastro de categorias de materiais acadêmicos.

    Recebe os dados informados pela View, valida o nome
    e cria uma instância de TipoMaterial.

    A sigla da categoria é gerada automaticamente a partir
    do nome. O Controller verifica se essa sigla já existe
    antes de solicitar o cadastro no PostgreSQL.

    A especialização define qual classe concreta será
    utilizada pela MaterialFactory para criar exemplares.
    """

    def __init__(self, repository: TiposMaterialRepository) -> None:
        self.__repository = repository

    def register(self, new_tipo_informations: Dict) -> Dict:
        """
        Processa o cadastro de uma categoria de material.

        Etapas:
        Valida o nome informado.
        Gera a sigla a partir do nome.
        Define e valida a especialização.
        Verifica o tamanho e a unicidade da sigla.
        Solicita o cadastro ao repositório.

        Se a especialização não for informada, utiliza OUTRO.
        """
        try:
            self._validate_fields(new_tipo_informations)
            nome = new_tipo_informations["nome"].strip()
            tipo = TipoMaterial(
                sigla=TipoMaterial.gerar_sigla(nome),
                nome=nome,
                especializacao=new_tipo_informations.get(
                    "especializacao", "OUTRO"
                )
            )
            if len(tipo.sigla) < 3:
                raise Exception(' O nome do tipo precisa ter pelo menos 3 letras!')
            existente = self.__repository.select_tipo(tipo.sigla)
            if existente is not None:
                raise Exception(f' Já existe um tipo com a sigla {tipo.sigla} ({existente.nome})!')
            saved_tipo = self.__repository.insert_tipo(tipo)
            response = self.__format_response(saved_tipo)
            return {"success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def _validate_fields(self, new_tipo_informations: Dict) -> None:
        """
        Valida o nome informado para a categoria.

        A verificação do tamanho mínimo da sigla e sua
        unicidade é realizada posteriormente pelo register().
        """
        if not new_tipo_informations["nome"].replace(" ", "").isalpha():
            raise Exception(' Nome do tipo de material incorreto!')

    def __format_response(self, tipo: TipoMaterial) -> Dict:
        return {
            "count": 1,
            "type": "Tipo de Material",
            "attributes": tipo.to_dict()
        }