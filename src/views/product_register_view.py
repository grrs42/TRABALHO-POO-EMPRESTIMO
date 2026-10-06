import os
from typing import Dict

class ProductRegisterView:
    def register_product_view(self) -> Dict:
        os.system('cls||clear')
        print('Registrar Material \n\n')
        product = input('Tipo do Material: \n')
        id = input('ID do Material: \n')
        new_product_informations = {
            "product": product, "id": id
                }
        return new_product_informations
    def register_person_sucess(self, message: Dict) -> None:
            os.system('cls||clear')
            sucess_message = f''' 
                Material cadastrado com sucesso!
                Tipo: {message["type"]}
                Registros: { message["count"]}
                Informações:
                    Nome: {message["attributes"] ["product"]}
                    Matricula: { message["attributes"] ["id"]}
            '''
            print(sucess_message)
    def register_person_error(self, error:str) -> None:
            os.system('cls||clear')
            error_message = f'''
                Erro ao cadastrar material!
                
                Erro:{error}
                '''
            print(error_message)
            
        