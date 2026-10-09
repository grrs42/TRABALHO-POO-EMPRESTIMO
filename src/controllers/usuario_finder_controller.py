from typing import Dict
from src.models.entities.usuario import Usuario
from src.models.repositories.usuarios_repository import UsuariosRepository

class UsuarioFinderController():
    def __init__(self, repository: UsuariosRepository) -> None:
        self.__repository = repository
    def finder(self, usuario_finder_informations: Dict) -> Dict:
        try:
            self._validate_fields(usuario_finder_informations)
            usuario = self.__repository.select_usuario(
                usuario_finder_informations["matricula"]
            )
            if usuario is None:
                raise Exception(' Usuário não encontrado!')
            response = self.__format_response(usuario)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
    def _validate_fields(self, usuario_finder_informations: Dict) -> None:
        if not usuario_finder_informations["matricula"].isdigit():
            raise Exception(' Campo de matrícula incorreto!')
    def __format_response(self, usuario: Usuario) -> Dict:
        return {
            "count": 1,
            "type": "Usuário",
            "attributes": usuario.to_dict()
        }
