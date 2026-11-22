import os
from getpass import getpass
from typing import Dict


class LoginView:
    def login_view(self) -> Dict:
        os.system('cls||clear')
        print('Entrar \n')
        print('Estudante: use sua matrícula. Grupo: use o código do grupo (ex.: GEES).\n')
        login = input('Login: \n')
        senha = getpass('Senha: \n')
        return {"login": login, "senha": senha}

    def login_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        tipo = "estudante" if message["tipo"] == "ESTUDANTE" else "grupo"
        print(f'\n            Login realizado como {tipo} {message["identidade"]}.\n')

    def login_error(self, error: str) -> None:
        os.system('cls||clear')
        print(f'\n            Erro ao entrar!\n\n            Erro: {error}\n')

    def logout_message(self) -> None:
        os.system('cls||clear')
        print('\n            Você saiu da conta.\n')
