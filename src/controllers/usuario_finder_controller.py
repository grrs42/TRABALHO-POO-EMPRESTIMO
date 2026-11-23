
import re
from typing import Dict
from src.models.entities.usuario import Usuario
from src.models.repositories.usuarios_repository import UsuariosRepository


class UsuarioFinderController:
    """
    Coordena a consulta de estudantes cadastrados.

    Recebe a matrícula informada pela View, valida
    seu formato e consulta o UsuariosRepository.

    Retorna os dados do estudante encontrado ou
    uma mensagem de erro quando a consulta é rejeitada.
    """

    def __init__(self, repository: UsuariosRepository) -> None:
        self.__repository = repository

    def finder(self, usuario_finder_informations: Dict) -> Dict:
        """
        Consulta um estudante pela matrícula.
        """
        try:
            self._validate_fields(usuario_finder_informations)
            usuario = self.__repository.select_usuario(
                usuario_finder_informations["matricula"].strip()
            )
            if usuario is None:
                raise Exception(' Usuário não encontrado!')
            response = self.__format_response(usuario)
            return {"success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def _validate_fields(self, usuario_finder_informations: Dict) -> None:
        """
        Valida o formato da matrícula informada.
        """
        if re.fullmatch(r"[0-9]{10}", usuario_finder_informations["matricula"].strip()) is None:
            raise Exception(' A matrícula deve conter exatamente 10 dígitos!')

    def __format_response(self, usuario: Usuario) -> Dict:
        return {
            "count": 1,
            "type": "Usuário",
            "attributes": usuario.to_dict()
        }