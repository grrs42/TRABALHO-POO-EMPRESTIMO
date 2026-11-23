
import re
from typing import Dict
from src.models.entities.usuario import Usuario
from src.models.entities.conta_acesso import ContaAcesso
from src.models.repositories.usuarios_repository import UsuariosRepository


class UsuarioRegisterController:
    """
    Coordena o cadastro de estudantes no sistema.

    Recebe os dados informados pela View, valida nome
    e matrícula, cria as entidades Usuario e ContaAcesso
    e solicita sua persistência ao UsuariosRepository.

    O cadastro do estudante e da conta de acesso é
    realizado na mesma transação pelo repositório.
    """

    def __init__(self, repository: UsuariosRepository) -> None:
        self.__repository = repository

    def register(self, new_usuario_informations: Dict) -> Dict:
        """
        Processa o cadastro de um novo estudante.

        Valida os dados, verifica se a matrícula já existe,
        cria a conta de acesso e solicita o cadastro.

        As exceções são capturadas e convertidas em
        respostas compreensíveis para a View.
        """
        try:
            self._validate_fields(new_usuario_informations)
            matricula = new_usuario_informations["matricula"].strip()
            usuario = Usuario(
                matricula,
                new_usuario_informations["nome"].strip()
            )
            conta = ContaAcesso.criar_para_estudante(
                matricula, new_usuario_informations["senha"]
            )
            if self.__repository.select_usuario(usuario.matricula) is not None:
                raise Exception(' Matrícula já cadastrada!')
            self.__repository.insert_usuario(usuario, conta)
            response = self.__format_response(usuario)
            return {"success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}

    def _validate_fields(self, new_usuario_informations: Dict) -> None:
        """
        Valida os campos iniciais do cadastro.
        """
        if not new_usuario_informations["nome"].replace(" ", "").isalpha():
            raise Exception(' Campo de nome incorreto!')
        if re.fullmatch(r"[0-9]{10}", new_usuario_informations["matricula"].strip()) is None:
            raise Exception(' A matrícula deve conter exatamente 10 dígitos!')

    def __format_response(self, usuario: Usuario) -> Dict:
        return {
            "count": 1,
            "type": "Usuário",
            "attributes": usuario.to_dict()
        }