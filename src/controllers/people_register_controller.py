from typing import Dict

class PeopleRegisterController():
    def register(self, new_person_informations: Dict) -> Dict:
        try:
            self._validate_fields(new_person_informations)
        #.
            response = self.__format_response(new_person_informations)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
        pass
    def _validate_fields(self, new_person_informations: Dict) -> None:
        if not new_person_informations["name"].replace(" ", "").isalpha():

            raise Exception(' Campo de nome incorreto!')
        try: int (new_person_informations["matricula"])
        except: raise Exception(' Campo de matrícula incorreto!') 
    def __format_response(self, new_person_informations: Dict) -> Dict:
        return {
            "count": 1,
            "type": "Pessoa",
            "attributes": new_person_informations
        }
        