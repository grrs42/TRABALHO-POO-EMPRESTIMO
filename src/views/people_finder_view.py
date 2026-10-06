import os
from typing import Dict

class PeopleFinderView:
    def find_person_view(self) -> Dict:
        os.system('cls||clear')

        print('Buscar Aluno \n\n')
        name = input('Nome completo do aluno: \n')
        matricula = input('matrícula do aluno: \n')

        person_finder_informations = {
            "name": name, "matricula": matricula
        }

        return person_finder_informations
    def find_person_sucess(self, message: Dict) -> None:
            os.system('cls||clear')
            sucess_message = f''' 
                Usuario encontrado!
                Tipo: {message["type"]}
                Registros: { message["count"]}
                Infos:
                    Nome: {message["attributes"] ["name"]}
                    Matricula: { message["attributes"] ["matricula"]}
            '''
            print(sucess_message)
    def finder_person_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao encontrar usuário!
            
            Erro:{error}
            '''
        print(error_message)