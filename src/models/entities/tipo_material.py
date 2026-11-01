import unicodedata

class TipoMaterial:
    """Representa uma categoria cadastrável de material acadêmico."""

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
        return self.__id

    @property
    def sigla(self) -> str:
        return self.__sigla

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def especializacao(self) -> str:
        return self.__especializacao

    @staticmethod
    def gerar_sigla(nome: str) -> str:
        """Gera uma sigla de três letras a partir do nome."""
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
