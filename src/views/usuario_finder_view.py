import os
from typing import Dict

class UsuarioFinderView:
    def find_usuario_view(self) -> Dict:
        os.system('cls||clear')

        print('Buscar Aluno \n\n')
        matricula = input('matrícula do aluno: \n')

        usuario_finder_informations = {
            "matricula": matricula
        }

        return usuario_finder_informations
    def find_usuario_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        sucess_message = f'''
            Usuario encontrado!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Infos:
                Nome: {message["attributes"] ["nome"]}
                Matricula: { message["attributes"] ["matricula"]}
        '''
        print(sucess_message)
    def find_usuario_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao encontrar usuário!

            Erro:{error}
            '''
        print(error_message)
