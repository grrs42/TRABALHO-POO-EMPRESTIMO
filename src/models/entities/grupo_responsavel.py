
class GrupoResponsavel:
    """
    Representa uma organização acadêmica responsável por materiais.

    Pode representar grêmios estudantis, laboratórios
    ou outros grupos que disponibilizam exemplares
    para empréstimo.

    Armazena o identificador do banco, o código do
    grupo e seu nome.

    Os grupos são associados aos materiais cadastrados,
    permitindo identificar a organização responsável
    por cada exemplar.
    """

    def __init__(
        self,
        codigo: str,
        nome: str,
        id: int | None = None
    ) -> None:
        """
        Inicializa um grupo responsável.

        Args:
            codigo: Código identificador do grupo.
            nome: Nome da organização acadêmica.
            id: Identificador do registro no PostgreSQL,
                quando disponível.

        Os atributos são armazenados de forma encapsulada.

        Nesta versão, os grupos são previamente cadastrados
        por scripts de inicialização do banco de dados.
        """
        self.__id = id
        self.__codigo = codigo
        self.__nome = nome

    @property
    def id(self) -> int | None:
        """Retorna o identificador do grupo no banco."""
        return self.__id

    @property
    def codigo(self) -> str:
        """Retorna o código do grupo responsável."""
        return self.__codigo

    @property
    def nome(self) -> str:
        """Retorna o nome do grupo responsável."""
        return self.__nome

    def to_dict(self) -> dict:
        """
        Converte os dados do grupo em um dicionário.

        Returns:
            Dicionário contendo ID, código e nome do grupo.

        Não altera os atributos do objeto.
        """
        return {
            "id": self.__id,
            "codigo": self.__codigo,
            "nome": self.__nome
        }

    def __repr__(self) -> str:
        """Retorna uma representação textual do grupo."""
        return (
            f"GrupoResponsavel(id={self.__id}, "
            f"codigo='{self.__codigo}', "
            f"nome='{self.__nome}')"
        )