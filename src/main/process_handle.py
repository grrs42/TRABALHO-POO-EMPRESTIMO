from src.main.constructor.introduction_process import introduction_process 
def start()-> None:
        while True:
            command = introduction_process()
            
            if command == '1': print('Insira o nome a ser cadastrado:')
            elif command == '2': print('Insira o nome a ser buscado no banco de dados')
            elif command == '5': exit()
            else: print('\n Comando não encontrado! \n')