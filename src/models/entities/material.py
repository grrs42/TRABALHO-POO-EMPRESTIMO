
from abc import ABC, abstractmethod
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class Material(ABC):
    """
    Classe abstrata que representa um exemplar físico de material acadêmico.

    Reúne os atributos comuns aos diferentes materiais, como código,
    categoria, grupo responsável, marca e disponibilidade.

    As subclasses implementam a validação e a apresentação de seus
    atributos específicos.

    Cada objeto representa um exemplar individual, permitindo
    controlar sua disponibilidade separadamente.
    """

    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        codigo: str | None = None,
        disponivel: bool = True,
        id: int | None = None,
        marca: str | None = None
    ) -> None:
        self.__id = id
        self.__codigo = codigo
        self.__tipo = tipo
        self.__grupo = grupo
        self.__disponivel = disponivel
        self.__marca = marca

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def codigo(self) -> str | None:
        return self.__codigo

    @property
    def nome(self) -> str:
        return self.__tipo.nome

    @property
    def tipo(self) -> TipoMaterial:
        return self.__tipo

    @property
    def grupo(self) -> GrupoResponsavel:
        return self.__grupo

    @property
    def marca(self) -> str | None:
        return self.__marca

    @staticmethod
    def gerar_codigo(sigla: str, numero: int) -> str:
        """
        Monta o código individual de um exemplar.
        """
        return f"{sigla}-{numero:03d}"

    def verificar_disponibilidade(self) -> bool:
        """
        Consulta a disponibilidade registrada no objeto.
        """
        return self.__disponivel

    def marcar_indisponivel(self) -> None:
        """
        Altera a disponibilidade do objeto para False.

        A alteração ocorre apenas na instância em memória.
        A persistência no PostgreSQL é responsabilidade
        dos repositórios.
        """
        self.__disponivel = False

    @abstractmethod
    def validar_dados_especificos(self) -> None:
        """
        Valida os atributos próprios da especialização.
        Deve ser implementado pelas subclasses concretas.
        """
        pass

    @abstractmethod
    def detalhes_especificos(self) -> dict:
        """
        Obtém os atributos específicos do material.
        """
        pass

    def to_dict(self) -> dict:
        """
        Converte os dados do material em um dicionário.

        Combina atributos comuns e específicos, utilizando
        o método polimórfico detalhes_especificos()
        """
        return {
            "id": self.__id,
            "codigo": self.__codigo,
            "nome": self.nome,
            "tipo": self.__tipo.to_dict(),
            "grupo": self.__grupo.to_dict(),
            "disponivel": self.__disponivel,
            "marca": self.__marca,
            **self.detalhes_especificos()
        }

    def __repr__(self) -> str:
        return (
            f"Material(id={self.__id}, "
            f"codigo='{self.__codigo}', "
            f"grupo='{self.__grupo.codigo}', "
            f"disponivel={self.__disponivel})"
        )