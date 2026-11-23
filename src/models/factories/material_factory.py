
from src.models.entities.material import Material
from src.models.entities.jaleco import Jaleco
from src.models.entities.livro import Livro
from src.models.entities.calculadora import Calculadora
from src.models.entities.outro_material import OutroMaterial
from src.models.entities.tipo_material import TipoMaterial
from src.models.entities.grupo_responsavel import GrupoResponsavel


class MaterialFactory:
    """
    Centraliza a criação de objetos especializados de Material.

    Seleciona a classe concreta a partir da especialização
    definida em TipoMaterial.

    É utilizada tanto no cadastro de novos exemplares quanto
    na reconstrução de objetos recuperados do PostgreSQL.
    """

    # Relaciona cada especialização à sua classe concreta.
    _CLASSES = {
        "JALECO": Jaleco,
        "LIVRO": Livro,
        "CALCULADORA": Calculadora,
        "OUTRO": OutroMaterial
    }

    # Define os campos específicos exigidos por especialização.
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
        """
        Cria ou reconstrói um material de sua classe concreta.
        Returns:
            Instância de Calculadora, Jaleco, Livro ou
            OutroMaterial, conforme a especialização
            
        A validação dos valores específicos é realizada
        pela classe concreta instanciada.
        """
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