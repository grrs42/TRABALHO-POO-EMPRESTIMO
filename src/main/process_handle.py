from src.main.constructor.introduction_process import introduction_process 
from src.main.constructor.people_finder_constructor import people_finder_constructor
from src.main.constructor.people_register_constructor import people_register_constructor
from src.main.constructor.product_finder_constructor import product_finder_constructor
from src.main.constructor.product_register_constructor import product_register_constructor




def start()-> None:
        while True:
            command = introduction_process()
            
            if command == '1': people_register_constructor()
            elif command == '2': people_finder_constructor()
            elif command == '3': product_register_constructor()
            elif command == '4': product_finder_constructor()
            elif command == '0': exit()
            else: print('\n Comando não encontrado! \n')