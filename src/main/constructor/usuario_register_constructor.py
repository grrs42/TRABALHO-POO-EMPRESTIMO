from src.views.usuario_register_view import UsuarioRegisterView
from src.controllers.usuario_register_controller import UsuarioRegisterController
from src.models.repositories.usuarios_repository import UsuariosRepository

def usuario_register_constructor():
    usuarios_repository = UsuariosRepository()
    usuario_register_view = UsuarioRegisterView()
    usuario_register_controller = UsuarioRegisterController(usuarios_repository)

    new_usuario_informations = usuario_register_view.register_usuario_view()
    response = usuario_register_controller.register(new_usuario_informations)

    if response["success"]:
        usuario_register_view.register_usuario_sucess(response["message"])
    else:
        usuario_register_view.register_usuario_error(response["error"])
