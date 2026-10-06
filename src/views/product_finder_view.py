import os
from typing import Dict

class ProductFinderView:
    def find_product_view(self) -> Dict:
        os.system('cls||clear')
        print('Buscar Material \n\n')
        product = input('Tipo do Material: \n')
        id = input('ID do Material: \n')
        product_finder_informations = {
            "product": product, "id": id
                }
        return product_finder_informations
    def find_product_sucess(self, message: Dict) -> None:
                os.system('cls||clear')
                sucess_message = f''' 
                    Produto encontrado!
                    Tipo: {message["type"]}
                    Registros: { message["count"]}
                    Infos:
                        Produto: {message["attributes"] ["product"]}
                        ID: { message["attributes"] ["id"]}
                '''
                print(sucess_message)
    def finder_product_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao encontrar produto!
            
            Erro:{error}
            '''
        print(error_message)
    
        