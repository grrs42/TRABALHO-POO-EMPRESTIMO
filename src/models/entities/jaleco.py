
from src.models.entities.material import Material
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class Jaleco(Material):
    """
    Representa um exemplar de jaleco acadêmico.

    Especializa a classe abstrata Material, acrescentando
    o tamanho como atributo obrigatório.

    A classe valida o tamanho conforme um conjunto
    de valores permitidos e implementa os métodos
    abstratos definidos por Material.
    """

    # Tamanhos aceitos para o cadastro de jalecos.
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
        """
        Inicializa um exemplar de jaleco.

        Args:
            tipo: Categoria do material.
            grupo: Grupo responsável pelo exemplar.
            tamanho: Tamanho do jaleco, obrigatório.
            codigo: Código individual do exemplar.
            disponivel: Disponibilidade inicial.
            id: Identificador no banco de dados.
            marca: Marca opcional do jaleco.

        O tamanho é normalizado para letras maiúsculas
        e validado após a inicialização dos atributos.
        """

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
        """Retorna o tamanho do jaleco."""
        return self.__tamanho

    def validar_dados_especificos(self) -> None:
        """
        Verifica se o tamanho do jaleco é permitido.

        São aceitos os tamanhos PP, P, M, G, GG e XG.

        Raises:
            ValueError: Se o tamanho informado não
                pertencer ao conjunto de tamanhos aceitos.
        """
        if (
            not isinstance(self.__tamanho, str)
            or self.__tamanho not in self.TAMANHOS_ACEITOS
        ):
            raise ValueError(
                "Tamanho do jaleco inválido. "
                "Use PP, P, M, G, GG ou XG."
            )

    def detalhes_especificos(self) -> dict:
        """
        Retorna os atributos específicos do jaleco.

        Implementa o contrato abstrato de Material,
        permitindo o tratamento polimórfico dos materiais.

        Returns:
            Dicionário contendo o tamanho do jaleco.
        """
        return {
            "tamanho": self.__tamanho
        }