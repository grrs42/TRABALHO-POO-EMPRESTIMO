
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
        """
        Inicializa os atributos compartilhados pelos materiais.

        Args:
            tipo: Categoria à qual o material pertence.
            grupo: Organização responsável pelo exemplar.
            codigo: Código individual, quando já gerado.
            disponivel: Situação inicial de disponibilidade.
            id: Identificador do registro no banco de dados.
            marca: Marca opcional do material.
        """
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

        Args:
            sigla: Sigla da categoria do material.
            numero: Número sequencial do exemplar.

        Returns:
            Código no formato SIGLA-NNN, como JAL-001.
        """
        return f"{sigla}-{numero:03d}"

    def verificar_disponibilidade(self) -> bool:
        """
        Consulta a disponibilidade registrada no objeto.

        Returns:
            True se o exemplar estiver disponível;
            False caso contrário.

        Não realiza consultas ao banco de dados.
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

        Raises:
            ValueError: Quando algum atributo específico
                não atende às regras da categoria.
        """
        pass

    @abstractmethod
    def detalhes_especificos(self) -> dict:
        """
        Obtém os atributos específicos do material.

        Returns:
            Dicionário com os campos próprios da subclasse.
        """
        pass

    def to_dict(self) -> dict:
        """
        Converte os dados do material em um dicionário.

        Combina atributos comuns e específicos, utilizando
        o método polimórfico detalhes_especificos().

        Returns:
            Dicionário com os dados do exemplar.
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
        """Retorna uma representação textual resumida do material."""
        return (
            f"Material(id={self.__id}, "
            f"codigo='{self.__codigo}', "
            f"grupo='{self.__grupo.codigo}', "
            f"disponivel={self.__disponivel})"
        )