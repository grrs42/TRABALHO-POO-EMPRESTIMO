class GrupoResponsavel:
    def __init__(self, codigo: str, nome: str, id: int | None = None) -> None:
        self.__id = id
        self.__codigo = codigo
        self.__nome = nome

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def codigo(self) -> str:
        return self.__codigo

    @property
    def nome(self) -> str:
        return self.__nome

    def to_dict(self) -> dict:
        return {"id": self.__id, "codigo": self.__codigo, "nome": self.__nome}

    def __repr__(self) -> str:
        return f"GrupoResponsavel(id={self.__id}, codigo='{self.__codigo}', nome='{self.__nome}')"
