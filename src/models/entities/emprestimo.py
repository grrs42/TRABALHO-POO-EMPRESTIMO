
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum

from src.models.entities.material import Material
from src.models.entities.usuario import Usuario


class StatusEmprestimo(str, Enum):
    """
    Define os estados possíveis de uma solicitação de empréstimo.

    PENDENTE: solicitação registrada, aguardando análise.
    ATIVO: solicitação aprovada, com prazo de devolução.
    RECUSADO: solicitação rejeitada pelo grupo responsável.
    DEVOLVIDO: empréstimo encerrado após a devolução.
    """

    PENDENTE = "PENDENTE"
    ATIVO = "ATIVO"
    RECUSADO = "RECUSADO"
    DEVOLVIDO = "DEVOLVIDO"


class Emprestimo:
    """
    Representa uma solicitação e seu ciclo de empréstimo.

    Associa um estudante a um exemplar de material acadêmico
    e controla seu estado, datas, prazo e multa simulada.

    Uma mesma entidade representa tanto a solicitação pendente
    quanto o empréstimo aprovado ou encerrado.

    As mudanças de estado são realizadas por operações
    específicas, evitando alterações diretas que desrespeitem
    as regras do domínio.
    """

    # Valor simulado da multa por dia corrido de atraso.
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
        """
        Inicializa uma solicitação ou reconstrói um empréstimo.

        Args:
            usuario: Estudante associado ao empréstimo.
            material: Exemplar de material solicitado.
            id: Identificador do registro no banco.
            status: Estado atual do empréstimo.
            data_solicitacao: Momento em que foi solicitado.
                Utiliza o momento atual quando omitido.
            data_confirmacao: Momento da aprovação.
            data_prevista_devolucao: Data limite de devolução.
            data_devolucao: Momento da devolução efetiva.
            responsavel_confirmacao: Identificação do
                responsável que confirmou o empréstimo.

        Raises:
            TypeError: Quando objetos ou datas apresentam
                tipos incompatíveis.
            ValueError: Quando identificador, estado ou
                informações do empréstimo são inválidos.

        Os dados são verificados antes da inicialização
        e submetidos à validação de consistência.
        """
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
        """
        Verifica a coerência entre o estado e as datas.

        Solicitações pendentes ou recusadas não podem possuir
        informações de aprovação ou devolução.

        Empréstimos ativos e devolvidos exigem confirmação,
        prazo e identificação do responsável.
        """
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
        """Retorna o identificador do empréstimo."""
        return self.__id

    @property
    def usuario(self) -> Usuario:
        """Retorna o estudante associado ao empréstimo."""
        return self.__usuario

    @property
    def material(self) -> Material:
        """Retorna o exemplar associado ao empréstimo."""
        return self.__material

    @property
    def status(self) -> StatusEmprestimo:
        """Retorna o estado atual do empréstimo."""
        return self.__status

    @property
    def data_solicitacao(self) -> datetime:
        """Retorna o momento em que a solicitação foi criada."""
        return self.__data_solicitacao

    @property
    def data_confirmacao(self) -> datetime | None:
        """Retorna o momento da aprovação, quando existente."""
        return self.__data_confirmacao

    @property
    def data_prevista_devolucao(self) -> date | None:
        """Retorna a data limite de devolução, quando definida."""
        return self.__data_prevista_devolucao

    @property
    def data_devolucao(self) -> datetime | None:
        """Retorna o momento da devolução, quando registrada."""
        return self.__data_devolucao

    @property
    def responsavel_confirmacao(self) -> str | None:
        """Retorna a identificação do responsável pela aprovação."""
        return self.__responsavel_confirmacao

    def aprovar(
        self,
        prazo_dias: int,
        responsavel: str,
        data_confirmacao: datetime | None = None,
    ) -> None:
        """
        Aprova uma solicitação pendente de empréstimo.
        """
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
        """
        Recusa uma solicitação de empréstimo pendente.
        """
        if self.__status != StatusEmprestimo.PENDENTE:
            raise ValueError("Somente solicitações pendentes podem ser recusadas.")
        self.__status = StatusEmprestimo.RECUSADO

    def registrar_devolucao(self, data_devolucao: datetime | None = None) -> None:
        """
        Registra a devolução de um empréstimo ativo.
        """
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
        """
        Verifica se um empréstimo ativo está atrasado.
        """
        if hoje is not None and type(hoje) is not date:
            raise TypeError("Informe uma data válida.")
        referencia = hoje if hoje is not None else date.today()
        return (
            self.__status == StatusEmprestimo.ATIVO
            and referencia > self.__data_prevista_devolucao
        )

    def dias_atraso(self, data_referencia: date | None = None) -> int:
        """
        Calcula os dias corridos de atraso do empréstimo.

        Solicitações pendentes ou recusadas retornam zero.
        Para empréstimos ativos, utiliza a data de referência.
        Para empréstimos devolvidos, utiliza a data efetiva
        da devolução, impedindo que o atraso continue aumentando.
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
        """
        Calcula a multa simulada por atraso na devolução.

        O cálculo utiliza dias_atraso(), respeitando
        a data de devolução para empréstimos encerrados.
        """
        return self.MULTA_POR_DIA * self.dias_atraso(data_referencia)

    def to_dict(self) -> dict:
        """
        Converte os dados do empréstimo em um dicionário.

        As datas são convertidas para o formato ISO.
        A multa é convertida para string.

        Os valores de atraso e multa são calculados
        usando a data atual, sem alterar o objeto.
        """
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