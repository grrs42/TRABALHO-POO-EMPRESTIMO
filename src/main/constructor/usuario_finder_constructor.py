from src.views.usuario_finder_view import UsuarioFinderView
from src.controllers.usuario_finder_controller import UsuarioFinderController
from src.models.repositories.usuarios_repository import UsuariosRepository

def usuario_finder_constructor():
    usuarios_repository = UsuariosRepository()
    usuario_finder_view = UsuarioFinderView()
    usuario_finder_controller = UsuarioFinderController(usuarios_repository)

    usuario_finder_informations = usuario_finder_view.find_usuario_view()
    response = usuario_finder_controller.finder(usuario_finder_informations)
    if response ["success"]:
        usuario_finder_view.find_usuario_sucess(response["message"])
    else:
        usuario_finder_view.find_usuario_error(response["error"])
