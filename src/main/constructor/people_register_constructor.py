from src.views.people_register_view import PeopleRegisterView
from src.controllers.people_register_controller import PeopleRegisterController

def people_register_constructor():
    people_register_view = PeopleRegisterView()
    people_register_controller = PeopleRegisterController()

    new_person_informations = people_register_view.register_person_view()
    response = people_register_controller.register(new_person_informations)

    if response["success"]:
        people_register_view.register_person_sucess(response["message"])
    else:
        people_register_view.register_person_error(response["error"])