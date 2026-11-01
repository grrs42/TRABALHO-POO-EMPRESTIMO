import os
from typing import Dict

class MaterialRegisterView:
    def register_material_view(self, options: Dict) -> Dict:
        os.system('cls||clear')
        print('Registrar Material\n')
        print('Tipos disponíveis:')
    
        for tipo in options["tipos"]:
            print(f'  {tipo["sigla"]} - {tipo["nome"]}')
        print('\nGrêmios/Laboratórios:')
        
        for grupo in options["grupos"]:
            print(f'  {grupo["codigo"]} - {grupo["nome"]}')

        tipo_sigla = input(
            '\nTipo do material (ex: JAL): '
        ).strip().upper()

        grupo_codigo = input(
            'Grupo responsável (ex: GEES): '
        ).strip().upper()

        marca = input(
            'Marca (opcional): '
        ).strip() or None

        tipo_selecionado = next(
            (
                tipo for tipo in options["tipos"]
                if tipo["sigla"] == tipo_sigla
            ),
            None
        )

        campos_por_especializacao = {
            "JALECO": ["tamanho"],
            "LIVRO": ["titulo", "editora"],
            "CALCULADORA": ["modelo"],
            "OUTRO": ["descricao"]
        }

        dados_especificos = {}

        if tipo_selecionado is not None:
            especializacao = tipo_selecionado["especializacao"]

            campos = campos_por_especializacao[especializacao]

            for campo in campos:
                valor = input(
                    f'{campo.capitalize()}: '
                ).strip()

                dados_especificos[campo] = valor

        return {
            "tipo": tipo_sigla,
            "grupo": grupo_codigo,
            "marca": marca,
            "dados_especificos": dados_especificos
        }
    
    def register_material_sucess(self, message: Dict) -> None:
        os.system('cls||clear')
        attributes = message["attributes"]
        situacao = 'Disponível' if attributes["disponivel"] else 'Indisponível'
        sucess_message = f'''
            Material cadastrado com sucesso!
            Tipo: {message["type"]}
            Registros: { message["count"]}
            Informações:
                Código gerado: {attributes["codigo"]}
                Material: {attributes["nome"]}
                Responsável: {attributes["grupo"]["codigo"]} - {attributes["grupo"]["nome"]}
                Situação: {situacao}
        '''
        print(sucess_message)
        print("Atributos específicos:")

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
                print(f"  {rotulo}: {valor}")
            
        
    def register_material_error(self, error:str) -> None:
        os.system('cls||clear')
        error_message = f'''
            Erro ao cadastrar material!

            Erro:{error}
            '''
        print(error_message)
