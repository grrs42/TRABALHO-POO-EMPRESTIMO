from src.views.emprestimo_view import EmprestimoView
from src.controllers.sistema_emprestimos_controller import SistemaEmprestimosController
from src.models.repositories.usuarios_repository import UsuariosRepository
from src.models.repositories.materiais_repository import MateriaisRepository
from src.models.repositories.emprestimos_repository import EmprestimosRepository
from src.models.services.notificador_simulado import NotificadorEmailSimulado


def _controller() -> SistemaEmprestimosController:
    usuarios = UsuariosRepository()
    materiais = MateriaisRepository()
    return SistemaEmprestimosController(
        usuarios,
        materiais,
        EmprestimosRepository(usuarios, materiais),
        NotificadorEmailSimulado(),
    )


def _mostrar_um(view: EmprestimoView, response: dict, titulo: str) -> None:
    if response["success"]:
        view.mostrar_emprestimo(titulo, response["message"])
    else:
        view.mostrar_erro(response["error"])


def _mostrar_lista(view: EmprestimoView, response: dict, titulo: str) -> None:
    if response["success"]:
        view.mostrar_lista(titulo, response["message"])
    else:
        view.mostrar_erro(response["error"])


def solicitar_emprestimo_constructor(matricula: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_codigo_material()
    dados["matricula"] = matricula
    _mostrar_um(view, _controller().solicitar_emprestimo(dados), "Solicitação registrada!")


def historico_estudante_constructor(matricula: str) -> None:
    view = EmprestimoView()
    _mostrar_lista(view, _controller().listar_emprestimos_usuario(matricula), "Meus empréstimos")


def pendencias_estudante_constructor(matricula: str) -> None:
    view = EmprestimoView()
    _mostrar_lista(view, _controller().listar_pendencias_usuario(matricula), "Minhas multas")


def consultar_emprestimo_estudante_constructor(matricula: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_id("Consultar empréstimo")
    response = _controller().consultar_emprestimo(dados, matricula_autenticada=matricula)
    _mostrar_um(view, response, "Empréstimo encontrado")


def listar_pendentes_grupo_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    response = _controller().listar_solicitacoes_pendentes(codigo_grupo)
    _mostrar_lista(view, response, "Solicitações pendentes")


def aprovar_emprestimo_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_aprovacao()
    response = _controller().aprovar_emprestimo(dados, codigo_grupo_autenticado=codigo_grupo)
    _mostrar_um(view, response, "Solicitação aprovada!")


def recusar_emprestimo_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_id("Recusar solicitação")
    response = _controller().recusar_emprestimo(dados, codigo_grupo_autenticado=codigo_grupo)
    _mostrar_um(view, response, "Solicitação recusada!")


def registrar_devolucao_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_id("Registrar devolução")
    response = _controller().registrar_devolucao(dados, codigo_grupo_autenticado=codigo_grupo)
    _mostrar_um(view, response, "Devolução registrada!")


def listar_ativos_grupo_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    response = _controller().listar_emprestimos_ativos(codigo_grupo)
    _mostrar_lista(view, response, "Empréstimos ativos")


def gerar_avisos_atraso_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    response = _controller().gerar_avisos_atraso(codigo_grupo)
    _mostrar_lista(view, response, "Avisos de atraso simulados (gravados em avisos_simulados.log)")


def consultar_emprestimo_grupo_constructor(codigo_grupo: str) -> None:
    view = EmprestimoView()
    dados = view.pedir_id("Consultar empréstimo")
    response = _controller().consultar_emprestimo(dados, codigo_grupo_autenticado=codigo_grupo)
    _mostrar_um(view, response, "Empréstimo encontrado")
