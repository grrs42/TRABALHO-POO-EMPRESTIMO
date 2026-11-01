import os
from typing import Dict

class MaterialFinderView:
    def find_material_view(self) -> Dict:
        os.system('cls||clear')
        print('Buscar Material \n\n')
        codigo = input('Código do Material: \n')
        material_finder_informations = {
            "codigo": codigo
        }
        return material_finder_informations
    def find_material_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        situacao = 'Disponível' if message["attributes"]["disponivel"] else 'Indisponível'
        sucess_message = f'''
            Material encontrado!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Infos:
                Código: {message["attributes"] ["codigo"]}
                Material: {message["attributes"] ["nome"]}
                Responsável: {message["attributes"]["grupo"]["codigo"]} - {message["attributes"]["grupo"]["nome"]}
                Situação: {situacao}
        '''
        print(sucess_message)
        
        # Exibe os atributos comuns e específicos do material.
        attributes = message["attributes"]
        campos = {
            "marca": "Marca",
            "modelo": "Modelo",
            "tamanho": "Tamanho",
            "titulo": "Título",
            "editora": "Editora",
            "descricao": "Descrição"
        }

        for campo, rotulo in campos.items():
            valor = attributes.get(campo)

            if valor is not None:
                print(f"                {rotulo}: {valor}")

    def find_material_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao encontrar material!

            Erro:{error}
            '''
        print(error_message)
