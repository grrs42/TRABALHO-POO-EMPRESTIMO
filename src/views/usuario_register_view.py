import os
from typing import Dict

class UsuarioRegisterView:
    def register_usuario_view(self) -> Dict:
        os.system('cls||clear')
        print('Registrar usuário \n\n')
        nome = input('Nome completo do aluno a ser cadastrado: \n')
        matricula = input('Matricula do aluno a ser cadastrado: \n')
        new_usuario_informations = {
            "nome": nome, "matricula": matricula
        }
        return new_usuario_informations
    def register_usuario_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        sucess_message = f'''
            Usuário cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Informações:
                Nome: {message["attributes"] ["nome"]}
                Matricula: { message["attributes"] ["matricula"]}
        '''
        print(sucess_message)
    def register_usuario_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar usuário!

            Erro:{error}
            '''
        print(error_message)
