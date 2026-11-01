from src.models.entities.material import Material
from src.models.entities.jaleco import Jaleco
from src.models.entities.livro import Livro
from src.models.entities.calculadora import Calculadora
from src.models.entities.outro_material import OutroMaterial
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class MaterialFactory:
    """Cria a classe concreta conforme a especialização do tipo."""

    _CLASSES = {
        "JALECO": Jaleco,
        "LIVRO": Livro,
        "CALCULADORA": Calculadora,
        "OUTRO": OutroMaterial
    }

    _CAMPOS = {
        "JALECO": {"tamanho"},
        "LIVRO": {"titulo", "editora"},
        "CALCULADORA": {"modelo"},
        "OUTRO": {"descricao"}
    }

    @classmethod
    def criar(
        cls,
        tipo: TipoMaterial,
        grupo: GrupoResponsavel,
        dados_especificos: dict[str, str],
        *,
        marca: str | None = None,
        codigo: str | None = None,
        disponivel: bool = True,
        id: int | None = None
    ) -> Material:
        """Constrói e valida um material especializado."""

        especializacao = tipo.especializacao

        classe_material = cls._CLASSES.get(especializacao)

        if classe_material is None:
            raise ValueError(
                "Especialização de material não reconhecida."
            )

        if not isinstance(dados_especificos, dict):
            raise ValueError(
                "Os dados específicos devem ser um dicionário."
            )

        campos_esperados = cls._CAMPOS[especializacao]

        if set(dados_especificos) != campos_esperados:
            raise ValueError(
                f"Campos esperados para {especializacao}: "
                f"{', '.join(sorted(campos_esperados))}"
            )

        return classe_material(
            tipo=tipo,
            grupo=grupo,
            marca=marca,
            codigo=codigo,
            disponivel=disponivel,
            id=id,
            **dados_especificos
        )