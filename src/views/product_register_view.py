import os
from typing import Dict

class ProductRegisterView:
    def register_product_view(self) -> Dict:
        os.system('cls||clear')
        print('Registrar Material \n\n')
        product = input('Tipo do Material: \n')
        product_name = input('Nome do Material: \n')
        new_product_informations = {
            "product": product, "product_name": product_name
                }
        return new_product_informations
        
        