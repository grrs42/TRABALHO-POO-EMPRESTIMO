import os
from typing import Dict

class PeopleFinderView:
    def find_person_view(self) -> Dict:
        os.system('cls||clear')

        print('Buscar Aluno \n\n')
        name = input('Nome completo do aluno: \n')
        matricula = input('matrícula do aluno: \n')

        person_finder_informations = {
            "name": name
        }

        return person_finder_informations