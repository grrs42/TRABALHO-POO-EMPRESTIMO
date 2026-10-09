import os
from typing import Dict

class MaterialRegisterView:
    def register_material_view(self, options: Dict) -> Dict:
        os.system('cls||clear')
        print('Registrar Material \n')
        print('Tipos disponíveis:')
        for tipo in options["tipos"]:
            print(f'    {tipo["sigla"]} - {tipo["nome"]}')
        print('\nGrêmios/Laboratórios:')
        for grupo in options["grupos"]:
            print(f'    {grupo["codigo"]} - {grupo["nome"]} (ID {grupo["id"]:02d})')
        print()
        tipo = input('Tipo do Material (ex: CAL): \n')
        grupo = input('Grêmio/Laboratório responsável (ex: GEES): \n')
        new_material_informations = {
            "tipo": tipo, "grupo": grupo
        }
        return new_material_informations
    def register_material_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        attributes = message["attributes"]
        situacao = 'Disponível' if attributes["disponivel"] else 'Indisponível'
        sucess_message = f'''
            Material cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Informações:
                Código gerado: {attributes["codigo"]}
                Material: {attributes["nome"]}
                Responsável: {attributes["grupo"]["codigo"]} - {attributes["grupo"]["nome"]}
                Situação: {situacao}
        '''
        print(sucess_message)
    def register_material_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar material!

            Erro:{error}
            '''
        print(error_message)
