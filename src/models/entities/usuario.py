
class Usuario:
    """
    Representa um estudante cadastrado no sistema.

    Armazena a matrícula, utilizada como identificador
    do estudante e seu nome.

    O estudante pode ser associado a solicitações e
    empréstimos de materiais acadêmicos.

    Os dados de autenticação são mantidos separadamente
    pela entidade ContaAcesso.
    """

    def __init__(self, matricula: str, nome: str) -> None:
        """
        Inicializa um estudante com matrícula e nome.

        Os atributos são armazenados de forma encapsulada.
        A validação dos dados de cadastro é realizada
        pelo Controller responsável.
        """
        self.__matricula = matricula
        self.__nome = nome

    @property
    def matricula(self) -> str:
        """Retorna a matrícula do estudante."""
        return self.__matricula

    @property
    def nome(self) -> str:
        """Retorna o nome do estudante."""
        return self.__nome

    def to_dict(self) -> dict:
        """
        Converte os dados do estudante em um dicionário.
        """
        return {
            "matricula": self.__matricula,
            "nome": self.__nome
        }

    def __repr__(self) -> str:
        return (
            f"Usuario(matricula='{self.__matricula}', "
            f"nome='{self.__nome}')"
        )