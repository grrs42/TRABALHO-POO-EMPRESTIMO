import os
from typing import Dict


class EmprestimoView:
    def pedir_codigo_material(self) -> Dict:
        os.system('cls||clear')
        print('Solicitar empréstimo \n')
        codigo = input('Código do material (ex.: CAL-001): \n')
        return {"codigo_material": codigo}

    def pedir_id(self, titulo: str) -> Dict:
        os.system('cls||clear')
        print(f'{titulo} \n')
        emprestimo_id = input('ID do empréstimo: \n')
        return {"id_emprestimo": emprestimo_id}

    def pedir_aprovacao(self) -> Dict:
        os.system('cls||clear')
        print('Aprovar solicitação \n')
        emprestimo_id = input('ID do empréstimo: \n')
        prazo = input('Prazo de devolução (dias corridos): \n')
        return {"id_emprestimo": emprestimo_id, "prazo_dias": prazo}

    def mostrar_emprestimo(self, titulo: str, message: Dict) -> None:
        os.system('cls||clear')
        print(f'\n{titulo}\n')
        self.__imprimir(message["attributes"])

    def mostrar_lista(self, titulo: str, message: Dict) -> None:
        os.system('cls||clear')
        print(f'\n{titulo} — registros: {message["count"]}\n')
        if message["count"] == 0:
            print('    Nenhum registro encontrado.\n')
        for item in message["attributes"]:
            self.__imprimir(item)
        if "total_multa_calculada" in message:
            print(f'Total de multas simuladas: R$ {message["total_multa_calculada"]}')
            print('(Simulação: não há cobrança nem pagamento nesta versão.)\n')

    def mostrar_erro(self, error: str) -> None:
        os.system('cls||clear')
        print(f'\n            Operação não realizada!\n\n            Erro: {error}\n')

    @staticmethod
    def __imprimir(dados: Dict) -> None:
        print(f'    ID: {dados["id"]}')
        print(f'    Estudante: {dados["matricula_usuario"]}')
        print(f'    Material: {dados["codigo_material"]}')
        print(f'    Status: {dados["status"]}')
        print(f'    Solicitado em: {dados["data_solicitacao"]}')
        if dados["data_confirmacao"]:
            print(f'    Aprovado em: {dados["data_confirmacao"]} por {dados["responsavel_confirmacao"]}')
            print(f'    Devolver até: {dados["data_prevista_devolucao"]}')
        if dados["data_devolucao"]:
            print(f'    Devolvido em: {dados["data_devolucao"]}')
        if dados["dias_atraso"]:
            print(f'    Dias de atraso: {dados["dias_atraso"]}')
            print(f'    Multa simulada: R$ {dados["multa_calculada"]}')
        print()
