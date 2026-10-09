from src.main.constructor.introduction_process import introduction_process 
from src.main.constructor.usuario_finder_constructor import usuario_finder_constructor
from src.main.constructor.usuario_register_constructor import usuario_register_constructor
from src.main.constructor.material_finder_constructor import material_finder_constructor
from src.main.constructor.material_register_constructor import material_register_constructor
from src.main.constructor.tipo_material_register_constructor import tipo_material_register_constructor




def start()-> None:
        while True:
            command = introduction_process()
            
            if command == '1': usuario_register_constructor()
            elif command == '2': usuario_finder_constructor()
            elif command == '3': material_register_constructor()
            elif command == '4': material_finder_constructor()
            elif command == '10': tipo_material_register_constructor()
            elif command == '0': exit()
            else: print('\n Comando não encontrado! \n')