import os
from typing import Dict

class PeopleRegisterView:
    def register_person_view(self) -> Dict:
        os.system('cls||clear')
        print('Registrar pessoa \n\n')
        name = input('Nome completo do aluno a ser cadastrado: \n')
        matricula = input('Matricula do aluno a ser cadastrado: \n')
        new_person_informations = {
            "name":name, "matricula":matricula
        }
        return new_person_informations
    def register_person_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        sucess_message = f''' 
            Usuario cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Infos:
                Nome: {message["attributes"] ["name"]}
                Matricula: { message["attributes"] ["matricula"]}
        '''
        print(sucess_message)
    def register_person_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar usuário!
            
            Erro:{error}
            '''
        print(error_message)
            
    