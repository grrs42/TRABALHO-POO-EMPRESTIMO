from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel

"""Classe Jaleco, que herda de Material."""
class Jaleco(Material):
    """Representa um exemplar de jaleco"""

    TAMANHOS_ACEITOS = frozenset({
        "PP", "P", "M", "G", "GG", "XG"
    })

    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        tamanho: str,
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

        self.__tamanho = (
            tamanho.strip().upper()
            if isinstance(tamanho, str)
            else tamanho
        )

        self.validar_dados_especificos()

    @property
    def tamanho(self) -> str:
        return self.__tamanho

    def validar_dados_especificos(self) -> None:
        """Verifica se o tamanho pertence aos valores aceitos."""
        if (
            not isinstance(self.__tamanho, str)
            or self.__tamanho not in self.TAMANHOS_ACEITOS
        ):
            raise ValueError(
                "Tamanho do jaleco inválido. "
                "Use PP, P, M, G, GG ou XG."
            )

    def detalhes_especificos(self) -> dict:
        """Retorna os dados particulares do jaleco."""
        return {
            "tamanho": self.__tamanho
        }