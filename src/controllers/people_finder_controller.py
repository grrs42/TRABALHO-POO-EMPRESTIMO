from typing import Dict

class PeopleFinderController():
    def finder(self, person_finder_informations: Dict) -> Dict:
        try:
            self._validate_fields(person_finder_informations)
        #.
            response = self.__format_response(person_finder_informations)
            return { "success": True, "message": response}
        except Exception as exception:
            return {"success": False, "error": str(exception)}
        pass
    def _validate_fields(self, person_finder_informations: Dict) -> None:
        if not person_finder_informations["name"].replace(" ", "").isalpha():

            raise Exception(' Campo de nome incorreto!')
        try: int (person_finder_informations["matricula"])
        except: raise Exception(' Campo de matrícula incorreto!') 
    def __format_response(self, person_finder_informations: Dict) -> Dict:
        return {
            "count": 1,
            "type": "Pessoa",
            "attributes": person_finder_informations
    #Adicionar não está no banco de dados
        }
        