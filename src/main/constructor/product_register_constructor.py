from src.views.product_register_view import ProductRegisterView
from src.controllers.product_register_controller import ProductRegisterController

def product_register_constructor():
    product_register_view = ProductRegisterView()
    product_register_controller = ProductRegisterController()
    #...
    new_product_informations = product_register_view.register_product_view()
    response = product_register_controller.register(new_product_informations)
    if response ["success"]:
        product_register_view.register_person_sucess["message"]
    else:
        product_register_view.register_person_error["error"]
