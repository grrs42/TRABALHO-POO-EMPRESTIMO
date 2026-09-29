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
        
        