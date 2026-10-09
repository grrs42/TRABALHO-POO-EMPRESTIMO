from src.views.tipo_material_register_view import TipoMaterialRegisterView
from src.controllers.tipo_material_register_controller import TipoMaterialRegisterController
from src.models.repositories.tipos_material_repository import TiposMaterialRepository

def tipo_material_register_constructor():
    tipos_material_repository = TiposMaterialRepository()
    tipo_material_register_view = TipoMaterialRegisterView()
    tipo_material_register_controller = TipoMaterialRegisterController(tipos_material_repository)

    new_tipo_informations = tipo_material_register_view.register_tipo_view()
    response = tipo_material_register_controller.register(new_tipo_informations)
    if response ["success"]:
        tipo_material_register_view.register_tipo_sucess(response["message"])
    else:
        tipo_material_register_view.register_tipo_error(response["error"])
