from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel

class Material:
    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        codigo: str | None = None,
        disponivel: bool = True,
        id: int | None = None
    ) -> None:
        self.__id = id
        self.__codigo = codigo
        self.__tipo = tipo
        self.__grupo = grupo
        self.__disponivel = disponivel

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

    @staticmethod
    def gerar_codigo(sigla: str, numero: int) -> str:
        # Sigla do tipo + número sequencial do tipo (ex: "CAL", 1 -> "CAL-001")
        return f"{sigla}-{numero:03d}"

    def verificar_disponibilidade(self) -> bool:
        return self.__disponivel

    def marcar_indisponivel(self) -> None:
        self.__disponivel = False

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "codigo": self.__codigo,
            "nome": self.nome,
            "tipo": self.__tipo.to_dict(),
            "grupo": self.__grupo.to_dict(),
            "disponivel": self.__disponivel
        }

    def __repr__(self) -> str:
        return f"Material(id={self.__id}, codigo='{self.__codigo}', grupo='{self.__grupo.codigo}', disponivel={self.__disponivel})"
