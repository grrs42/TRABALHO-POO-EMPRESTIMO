from typing import Dict

class ProductRegisterController():
    def register(self, new_product_informations: Dict) -> Dict:
        try:
            self._validate_fields(new_product_informations)
        #.
            response = self.__format_response(new_product_informations)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
        pass
    def _validate_fields(self, new_product_informations: Dict) -> None:
        if not new_product_informations["name"].replace(" ", "").isalpha():

            raise Exception(' Tipo de material incorreto!')
        try: int (new_product_informations["id"])
        except: raise Exception(' ID do material incorreto!') 
    def __format_response(self, new_product_informations: Dict) -> Dict:
        return {
            "count": 1,
            "type": "Produto",
            "attributes": new_product_informations
        }
        