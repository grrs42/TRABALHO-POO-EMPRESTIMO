import unicodedata

class TipoMaterial:
    def __init__(self, sigla: str, nome: str, id: int | None = None) -> None:
        self.__id = id
        self.__sigla = sigla
        self.__nome = nome

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def sigla(self) -> str:
        return self.__sigla

    @property
    def nome(self) -> str:
        return self.__nome

    @staticmethod
    def gerar_sigla(nome: str) -> str:
        # 3 primeiras letras do nome, sem acento e em maiúsculas (ex: "Régua" -> "REG")
        sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
        letras = [letra for letra in sem_acento if letra.isalpha()]
        return "".join(letras[:3]).upper()

    def to_dict(self) -> dict:
        return {"id": self.__id, "sigla": self.__sigla, "nome": self.__nome}

    def __repr__(self) -> str:
        return f"TipoMaterial(id={self.__id}, sigla='{self.__sigla}', nome='{self.__nome}')"
