class Usuario:
    def __init__(self, matricula: str, nome: str) -> None:
        self.__matricula = matricula
        self.__nome = nome

    @property
    def matricula(self) -> str:
        return self.__matricula

    @property
    def nome(self) -> str:
        return self.__nome

    def to_dict(self) -> dict:
        return {"matricula": self.__matricula, "nome": self.__nome}

    def __repr__(self) -> str:
        return f"Usuario(matricula='{self.__matricula}', nome='{self.__nome}')"
