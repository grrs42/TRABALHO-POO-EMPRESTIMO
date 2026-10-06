from typing import Dict

class ProductFinderController():
    def finder(self, product_finder_informations: Dict) -> Dict:
        try:
            self._validate_fields(product_finder_informations)
        #.
            response = self.__format_response(product_finder_informations)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
        pass
    def _validate_fields(self, product_finder_informations: Dict) -> None:
        if not product_finder_informations["product"].replace(" ", "").isalpha():

            raise Exception(' Campo de produto incorreto!')
        try: int (product_finder_informations["id"])
        except: raise Exception(' ID do produto incorreto!') 
    def __format_response(self, product_finder_informations: Dict) -> Dict:
        return {
            "count": 1,
            "type": "Pessoa",
            "attributes": product_finder_informations
    #Adicionar não está no banco de dados
        }
        