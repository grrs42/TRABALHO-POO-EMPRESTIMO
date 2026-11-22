from src.views.login_view import LoginView
from src.controllers.login_controller import LoginController
from src.models.repositories.contas_acesso_repository import ContasAcessoRepository


def login_constructor() -> dict | None:
    login_view = LoginView()
    login_controller = LoginController(ContasAcessoRepository())

    dados = login_view.login_view()
    response = login_controller.autenticar(dados)
    if response["success"]:
        login_view.login_sucess(response["message"])
        return response["message"]
    login_view.login_error(response["error"])
    return None
