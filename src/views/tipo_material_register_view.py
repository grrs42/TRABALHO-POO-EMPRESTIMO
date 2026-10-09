import os
from typing import Dict

class TipoMaterialRegisterView:
    def register_tipo_view(self) -> Dict:
        os.system('cls||clear')
        print('Registrar Tipo de Material \n\n')
        nome = input('Nome do novo tipo (ex: Calculadora): \n')
        new_tipo_informations = {
            "nome": nome
        }
        return new_tipo_informations
    def register_tipo_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        sucess_message = f'''
            Tipo de material cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Informações:
                Nome: {message["attributes"] ["nome"]}
                Sigla: {message["attributes"] ["sigla"]}
        '''
        print(sucess_message)
    def register_tipo_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar tipo de material!

            Erro:{error}
            '''
        print(error_message)
