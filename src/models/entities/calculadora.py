from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class Calculadora(Material):
    """Representa um exemplar de calculadora acadêmica."""

    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        modelo: str,
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

        self.__modelo = (
            modelo.strip()
            if isinstance(modelo, str)
            else modelo
        )

        self.validar_dados_especificos()

    @property
    def modelo(self) -> str:
        return self.__modelo

    def validar_dados_especificos(self) -> None:
        """Valida o modelo informado para a calculadora."""

        if (
            not isinstance(self.__modelo, str)
            or not self.__modelo
        ):
            raise ValueError(
                "O modelo da calculadora é obrigatório."
            )

    def detalhes_especificos(self) -> dict:
        """Retorna os atributos específicos da calculadora."""

        return {
            "modelo": self.__modelo
        }