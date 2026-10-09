from src.views.material_register_view import MaterialRegisterView
from src.controllers.material_register_controller import MaterialRegisterController
from src.models.repositories.materiais_repository import MateriaisRepository
from src.models.repositories.tipos_material_repository import TiposMaterialRepository
from src.models.repositories.grupos_responsaveis_repository import GruposResponsaveisRepository

def material_register_constructor():
    material_register_view = MaterialRegisterView()
    material_register_controller = MaterialRegisterController(
        MateriaisRepository(),
        TiposMaterialRepository(),
        GruposResponsaveisRepository()
    )

    options = material_register_controller.get_options()
    if not options["success"]:
        material_register_view.register_material_error(options["error"])
        return

    new_material_informations = material_register_view.register_material_view(options["message"])
    response = material_register_controller.register(new_material_informations)
    if response ["success"]:
        material_register_view.register_material_sucess(response["message"])
    else:
        material_register_view.register_material_error(response["error"])
