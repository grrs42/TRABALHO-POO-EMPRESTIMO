
import unicodedata


class TipoMaterial:
    """
    Representa uma categoria de material acadêmico.

    Armazena o identificador, a sigla, o nome e a
    especialização utilizada para determinar a classe
    concreta do material.

    Uma categoria pode representar, por exemplo, um tipo
    de calculadora, jaleco, livro ou outro material.

    A especialização é utilizada pela MaterialFactory
    para criar objetos da classe correspondente.
    """

    # Especializações reconhecidas pela MaterialFactory.
    ESPECIALIZACOES = frozenset({
        "CALCULADORA",
        "JALECO",
        "LIVRO",
        "OUTRO"
    })

    def __init__(
        self,
        sigla: str,
        nome: str,
        id: int | None = None,
        especializacao: str = "OUTRO"
    ) -> None:
        """
        Inicializa uma categoria de material.

        A especialização é normalizada para letras
        maiúsculas antes do armazenamento.

        As demais validações de cadastro são realizadas
        pelo Controller responsável.
        """

        if not isinstance(especializacao, str):
            raise ValueError("Especialização inválida.")

        especializacao = especializacao.strip().upper()

        if especializacao not in self.ESPECIALIZACOES:
            raise ValueError(
                "Especialização não reconhecida."
            )

        self.__id = id
        self.__sigla = sigla
        self.__nome = nome
        self.__especializacao = especializacao

    @property
    def id(self) -> int | None:
        """Retorna o identificador da categoria no banco."""
        return self.__id

    @property
    def sigla(self) -> str:
        """Retorna a sigla da categoria."""
        return self.__sigla

    @property
    def nome(self) -> str:
        """Retorna o nome da categoria."""
        return self.__nome

    @property
    def especializacao(self) -> str:
        """Retorna a especialização associada à categoria."""
        return self.__especializacao

    @staticmethod
    def gerar_sigla(nome: str) -> str:
        """
        Gera uma sigla a partir do nome da categoria.
        """
        sem_acento = (
            unicodedata.normalize("NFKD", nome)
            .encode("ascii", "ignore")
            .decode()
        )
        letras = [
            letra for letra in sem_acento if letra.isalpha()
        ]
        return "".join(letras[:3]).upper()

    def to_dict(self) -> dict:
        """
        Converte a categoria em um dicionário.
        """
        return {
            "id": self.__id,
            "sigla": self.__sigla,
            "nome": self.__nome,
            "especializacao": self.__especializacao
        }

    def __repr__(self) -> str:
        return (
            f"TipoMaterial(id={self.__id}, "
            f"sigla='{self.__sigla}', "
            f"nome='{self.__nome}', "
            f"especializacao='{self.__especializacao}')"
        )