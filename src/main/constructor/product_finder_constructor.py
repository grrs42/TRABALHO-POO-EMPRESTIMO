from src.views.product_finder_view import ProductFinderView
from src.controllers.product_finder_controller import ProductFinderController

def product_finder_constructor():
    product_finder_view = ProductFinderView()
    product_finder_controller = ProductFinderController()


    
    product_finder_informations = product_finder_view.find_product_view()
    response = product_finder_controller.finder(product_finder_informations)
    if response ["success"]:
        product_finder_view.finder_person_sucess(response["message"])
    else:
        product_finder_view.finder_person_error(response["error"])