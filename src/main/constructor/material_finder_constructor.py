from src.views.material_finder_view import MaterialFinderView
from src.controllers.material_finder_controller import MaterialFinderController
from src.models.repositories.materiais_repository import MateriaisRepository

def material_finder_constructor():
    materiais_repository = MateriaisRepository()
    material_finder_view = MaterialFinderView()
    material_finder_controller = MaterialFinderController(materiais_repository)

    material_finder_informations = material_finder_view.find_material_view()
    response = material_finder_controller.finder(material_finder_informations)
    if response ["success"]:
        material_finder_view.find_material_sucess(response["message"])
    else:
        material_finder_view.find_material_error(response["error"])
