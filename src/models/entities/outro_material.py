
from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class OutroMaterial(Material):
    """
    Representa materiais acadêmicos sem especialização
    própria entre calculadoras, jalecos e livros.

    Especializa a classe abstrata Material, utilizando
    uma descrição obrigatória para identificar as
    características específicas do exemplar.

    Implementa os métodos abstratos de validação e
    apresentação dos dados específicos.
    """

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
        """
        Inicializa um exemplar de outro material acadêmico.

        Args:
            tipo: Categoria do material.
            grupo: Grupo responsável pelo exemplar.
            descricao: Descrição obrigatória do material.
            codigo: Código individual do exemplar.
            disponivel: Disponibilidade inicial.
            id: Identificador no banco de dados.
            marca: Marca opcional do material.

        Os atributos comuns são inicializados por Material.
        A descrição é normalizada e validada na criação.
        """

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
        """Retorna a descrição específica do material."""
        return self.__descricao

    def validar_dados_especificos(self) -> None:
        """
        Verifica se a descrição do material é válida.

        A descrição deve ser uma string não vazia,
        desconsiderando espaços nas extremidades.

        Raises:
            ValueError: Se a descrição estiver ausente,
                vazia ou não for uma string válida.
        """
        if (
            not isinstance(self.__descricao, str)
            or not self.__descricao
        ):
            raise ValueError(
                "A descrição do material é obrigatória."
            )

    def detalhes_especificos(self) -> dict:
        """
        Retorna os atributos específicos do material.

        Implementa o contrato abstrato de Material,
        permitindo o tratamento polimórfico dos materiais.

        Returns:
            Dicionário contendo a descrição do exemplar.
        """
        return {
            "descricao": self.__descricao
        }