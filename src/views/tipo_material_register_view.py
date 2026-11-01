import os
from typing import Dict

class TipoMaterialRegisterView:    
    def register_tipo_view(self) -> Dict:
        """Recebe os dados para cadastrar um tipo de material."""

        os.system('cls||clear')
        print('Registrar Tipo de Material\n')
        nome = input('Nome do novo tipo (ex: Calculadora):\n')
        
        print('\nEspecializações disponíveis:')
        print('  CALCULADORA')
        print('  JALECO')
        print('  LIVRO')
        print('  OUTRO')

        especializacao = input(
            '\nInforme a especialização '
            '(Enter para OUTRO):\n'
        ).strip().upper()

        if not especializacao:
            especializacao = "OUTRO"

        return {
            "nome": nome,
            "especializacao": especializacao
        }
    

    def register_tipo_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        sucess_message = f'''
            Tipo de material cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Informações:
                Nome: {message["attributes"] ["nome"]}
                Sigla: {message["attributes"] ["sigla"]}
                Especialização: {message["attributes"]["especializacao"]}
        '''
        print(sucess_message)
    def register_tipo_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar tipo de material!

            Erro:{error}
            '''
        print(error_message)
