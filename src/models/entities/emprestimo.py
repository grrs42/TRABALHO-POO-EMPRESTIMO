from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum

from src.models.entities.material import Material
from src.models.entities.usuario import Usuario


class StatusEmprestimo(str, Enum):
    PENDENTE = "PENDENTE"
    ATIVO = "ATIVO"
    RECUSADO = "RECUSADO"
    DEVOLVIDO = "DEVOLVIDO"


class Emprestimo:
    """Representa uma solicitação até a recusa ou devolução de um material por um usuário."""

    # Multa por dia de atraso: R$ 2,00 após o vencimento
    MULTA_POR_DIA = Decimal("2.00")

    def __init__(
        self,
        usuario: Usuario,
        material: Material,
        id: int | None = None,
        status: StatusEmprestimo = StatusEmprestimo.PENDENTE,
        data_solicitacao: datetime | None = None,
        data_confirmacao: datetime | None = None,
        data_prevista_devolucao: date | None = None,
        data_devolucao: datetime | None = None,
        responsavel_confirmacao: str | None = None,
    ) -> None:
        if not isinstance(usuario, Usuario):
            raise TypeError("O usuário deve ser um objeto Usuario.")
        if not isinstance(material, Material):
            raise TypeError("O material deve ser um objeto Material.")
        if id is not None and (type(id) is not int or id <= 0):
            raise ValueError("O ID do empréstimo deve ser positivo.")
        if not isinstance(status, StatusEmprestimo):
            raise ValueError("Status do empréstimo inválido.")
        if data_solicitacao is not None and not isinstance(data_solicitacao, datetime):
            raise TypeError("Data da solicitação inválida.")
        if data_confirmacao is not None and not isinstance(data_confirmacao, datetime):
            raise TypeError("Data da confirmação inválida.")
        if data_prevista_devolucao is not None and type(data_prevista_devolucao) is not date:
            raise TypeError("Data prevista de devolução inválida.")
        if data_devolucao is not None and not isinstance(data_devolucao, datetime):
            raise TypeError("Data da devolução inválida.")
        if responsavel_confirmacao is not None:
            if not isinstance(responsavel_confirmacao, str) or not responsavel_confirmacao.strip():
                raise ValueError("Responsável pela confirmação inválido.")
            responsavel_confirmacao = responsavel_confirmacao.strip()

        self.__id = id
        self.__usuario = usuario
        self.__material = material
        self.__status = status
        self.__data_solicitacao = data_solicitacao if data_solicitacao is not None else datetime.now()
        self.__data_confirmacao = data_confirmacao
        self.__data_prevista_devolucao = data_prevista_devolucao
        self.__data_devolucao = data_devolucao
        self.__responsavel_confirmacao = responsavel_confirmacao
        self.__validar_consistencia()

    def __validar_consistencia(self) -> None:
        dados_confirmacao = (
            self.__data_confirmacao,
            self.__data_prevista_devolucao,
            self.__responsavel_confirmacao,
        )
        if self.__status in (StatusEmprestimo.PENDENTE, StatusEmprestimo.RECUSADO):
            if any(campo is not None for campo in (*dados_confirmacao, self.__data_devolucao)):
                raise ValueError("Solicitação pendente ou recusada não pode ter datas de empréstimo.")
        else:
            if any(campo is None for campo in dados_confirmacao):
                raise ValueError("Empréstimo confirmado requer datas e responsável.")
            if self.__data_confirmacao < self.__data_solicitacao:
                raise ValueError("Confirmação anterior à solicitação.")
            if self.__data_prevista_devolucao < self.__data_confirmacao.date():
                raise ValueError("Previsão anterior à confirmação.")
            if self.__status == StatusEmprestimo.ATIVO and self.__data_devolucao is not None:
                raise ValueError("Empréstimo ativo não pode ter uma devolução registrada.")
            if self.__status == StatusEmprestimo.DEVOLVIDO:
                if self.__data_devolucao is None or self.__data_devolucao < self.__data_confirmacao:
                    raise ValueError("Empréstimo devolvido requer data de devolução válida.")

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def material(self) -> Material:
        return self.__material

    @property
    def status(self) -> StatusEmprestimo:
        return self.__status

    @property
    def data_solicitacao(self) -> datetime:
        return self.__data_solicitacao

    @property
    def data_confirmacao(self) -> datetime | None:
        return self.__data_confirmacao

    @property
    def data_prevista_devolucao(self) -> date | None:
        return self.__data_prevista_devolucao

    @property
    def data_devolucao(self) -> datetime | None:
        return self.__data_devolucao

    @property
    def responsavel_confirmacao(self) -> str | None:
        return self.__responsavel_confirmacao

    def aprovar(
        self,
        prazo_dias: int,
        responsavel: str,
        data_confirmacao: datetime | None = None,
    ) -> None:
        """Confirma uma solicitação pendente e define a data de vencimento."""
        if self.__status != StatusEmprestimo.PENDENTE:
            raise ValueError("Somente solicitações pendentes podem ser aprovadas.")
        if type(prazo_dias) is not int or prazo_dias <= 0:
            raise ValueError("O prazo deve ser um número inteiro positivo de dias.")
        if not isinstance(responsavel, str) or not responsavel.strip():
            raise ValueError("O responsável pela confirmação é obrigatório.")
        momento = data_confirmacao if data_confirmacao is not None else datetime.now()
        if not isinstance(momento, datetime):
            raise TypeError("Data de confirmação inválida.")
        if momento < self.__data_solicitacao:
            raise ValueError("Confirmação anterior à solicitação.")

        self.__data_confirmacao = momento
        self.__data_prevista_devolucao = momento.date() + timedelta(days=prazo_dias)
        self.__responsavel_confirmacao = responsavel.strip()
        self.__status = StatusEmprestimo.ATIVO

    def recusar(self) -> None:
        """Encerra uma solicitação ainda pendente."""
        if self.__status != StatusEmprestimo.PENDENTE:
            raise ValueError("Somente solicitações pendentes podem ser recusadas.")
        self.__status = StatusEmprestimo.RECUSADO

    def registrar_devolucao(self, data_devolucao: datetime | None = None) -> None:
        """Encerra um empréstimo ativo, registrando a devolução."""
        if self.__status != StatusEmprestimo.ATIVO:
            raise ValueError("Somente empréstimos ativos podem ser devolvidos.")
        momento = data_devolucao if data_devolucao is not None else datetime.now()
        if not isinstance(momento, datetime):
            raise TypeError("Data de devolução inválida.")
        if momento < self.__data_confirmacao:
            raise ValueError("A devolução não pode preceder a confirmação.")
        self.__data_devolucao = momento
        self.__status = StatusEmprestimo.DEVOLVIDO

    def esta_atrasado(self, hoje: date | None = None) -> bool:
        """Indica atraso somente de empréstimos ainda ativos."""
        if hoje is not None and type(hoje) is not date:
            raise TypeError("Informe uma data válida.")
        referencia = hoje if hoje is not None else date.today()
        return (
            self.__status == StatusEmprestimo.ATIVO
            and referencia > self.__data_prevista_devolucao
        )

    def dias_atraso(self, data_referencia: date | None = None) -> int:
        """Conta dias corridos após o vencimento, sem valores negativos.

        Enquanto ATIVO, conta até data_referencia (ou hoje)
        Quando DEVOLVIDO, usa a data efetiva da devolução e congela o atraso.
        Solicitações PENDENTES e RECUSADAS não geram atraso.
        """
        if data_referencia is not None and type(data_referencia) is not date:
            raise TypeError("A data de referência deve ser uma data válida.")

        if self.__status not in (StatusEmprestimo.ATIVO, StatusEmprestimo.DEVOLVIDO):
            return 0

        if self.__status == StatusEmprestimo.DEVOLVIDO:
            referencia = self.__data_devolucao.date()
        else:
            referencia = data_referencia if data_referencia is not None else date.today()

        return max(0, (referencia - self.__data_prevista_devolucao).days)

    def calcular_multa(self, data_referencia: date | None = None) -> Decimal:
        """Calcula multa de R$ 2,00 por dia corrido.

        Retorna Decimal para evitar imprecisão de ponto flutuante.
        Não registra pagamento nem efetua cobrança financeira.
        """
        return self.MULTA_POR_DIA * self.dias_atraso(data_referencia)

    def to_dict(self) -> dict:
        """Fornece os dados do empréstimo sem expor atributos privados."""
        hoje = date.today()
        return {
            "id": self.__id,
            "matricula_usuario": self.__usuario.matricula,
            "codigo_material": self.__material.codigo,
            "status": self.__status.value,
            "data_solicitacao": self.__data_solicitacao.isoformat(),
            "data_confirmacao": (
                self.__data_confirmacao.isoformat() if self.__data_confirmacao else None
            ),
            "data_prevista_devolucao": (
                self.__data_prevista_devolucao.isoformat()
                if self.__data_prevista_devolucao else None
            ),
            "data_devolucao": self.__data_devolucao.isoformat() if self.__data_devolucao else None,
            "responsavel_confirmacao": self.__responsavel_confirmacao,
            "dias_atraso": self.dias_atraso(hoje),
            "multa_calculada": str(self.calcular_multa(hoje)),
        }