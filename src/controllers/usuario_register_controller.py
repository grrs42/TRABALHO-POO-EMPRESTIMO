from typing import Dict
from src.models.entities.usuario import Usuario
from src.models.repositories.usuarios_repository import UsuariosRepository

class UsuarioRegisterController():
    def __init__(self, repository: UsuariosRepository) -> None:
        self.__repository = repository
    def register(self, new_usuario_informations: Dict) -> Dict:
        try:
            self._validate_fields(new_usuario_informations)
            usuario = Usuario(
                new_usuario_informations["matricula"],
                new_usuario_informations["nome"]
            )
            if self.__repository.select_usuario(usuario.matricula) is not None:
                raise Exception(' Matrícula já cadastrada!')
            self.__repository.insert_usuario(usuario)
            response = self.__format_response(usuario)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
    def _validate_fields(self, new_usuario_informations: Dict) -> None:
        if not new_usuario_informations["nome"].replace(" ", "").isalpha():

            raise Exception(' Campo de nome incorreto!')
        if not new_usuario_informations["matricula"].isdigit():
            raise Exception(' Campo de matrícula incorreto!')
    def __format_response(self, usuario: Usuario) -> Dict:
        return {
            "count": 1,
            "type": "Usuário",
            "attributes": usuario.to_dict()
        }
