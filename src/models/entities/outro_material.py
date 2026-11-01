from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class OutroMaterial(Material):
    """Representa materiais sem especialização própria."""

    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        descricao: str,
        codigo: str | None = None,
        disponivel: bool = True,
        id: int | None = None,
        marca: str | None = None
    ) -> None:

        super().__init__(
            tipo=tipo,
            grupo=grupo,
            codigo=codigo,
            disponivel=disponivel,
            id=id,
            marca=marca
        )

        self.__descricao = (
            descricao.strip()
            if isinstance(descricao, str)
            else descricao
        )

        self.validar_dados_especificos()

    @property
    def descricao(self) -> str:
        return self.__descricao

    def validar_dados_especificos(self) -> None:
        """Verifica se o material possui descrição válida."""

        if (
            not isinstance(self.__descricao, str)
            or not self.__descricao
        ):
            raise ValueError(
                "A descrição do material é obrigatória."
            )

    def detalhes_especificos(self) -> dict:
        """Retorna os atributos específicos do material."""

        return {
            "descricao": self.__descricao
        }