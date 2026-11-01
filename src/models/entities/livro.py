from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class Livro(Material):
    """Representa um exemplar de livro acadêmico."""

    def __init__(
        self,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        titulo: str,
        editora: str,
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

        self.__titulo = (
            titulo.strip()
            if isinstance(titulo, str)
            else titulo
        )

        self.__editora = (
            editora.strip()
            if isinstance(editora, str)
            else editora
        )

        self.validar_dados_especificos()

    @property
    def titulo(self) -> str:
        return self.__titulo

    @property
    def editora(self) -> str:
        return self.__editora

    def validar_dados_especificos(self) -> None:
        """Verifica os dados bibliográficos obrigatórios."""

        if (
            not isinstance(self.__titulo, str)
            or not self.__titulo
        ):
            raise ValueError(
                "O título do livro é obrigatório."
            )

        if (
            not isinstance(self.__editora, str)
            or not self.__editora
        ):
            raise ValueError(
                "A editora do livro é obrigatória."
            )

    def detalhes_especificos(self) -> dict:
        """Retorna as informações próprias de um livro."""
        return {
            "titulo": self.__titulo,
            "editora": self.__editora
        }