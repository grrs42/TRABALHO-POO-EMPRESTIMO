
from src.main.constructor.introduction_process import introduction_process
from src.main.constructor.usuario_finder_constructor import usuario_finder_constructor
from src.main.constructor.usuario_register_constructor import usuario_register_constructor
from src.main.constructor.material_finder_constructor import material_finder_constructor
from src.main.constructor.material_register_constructor import material_register_constructor
from src.main.constructor.tipo_material_register_constructor import tipo_material_register_constructor
from src.main.constructor.login_constructor import login_constructor
from src.main.constructor import emprestimo_constructor as emp
from src.views.login_view import LoginView


# Relaciona as opções do menu às operações permitidas
# para contas autenticadas como estudantes.
ACOES_ESTUDANTE = {
    '11': emp.solicitar_emprestimo_constructor,
    '12': emp.historico_estudante_constructor,
    '13': emp.pendencias_estudante_constructor,
    '14': emp.consultar_emprestimo_estudante_constructor,
}

# Relaciona as opções do menu às operações permitidas
# para contas autenticadas como grupos responsáveis.
ACOES_GRUPO = {
    '21': emp.listar_pendentes_grupo_constructor,
    '22': emp.aprovar_emprestimo_constructor,
    '23': emp.recusar_emprestimo_constructor,
    '24': emp.registrar_devolucao_constructor,
    '25': emp.listar_ativos_grupo_constructor,
    '26': emp.gerar_avisos_atraso_constructor,
    '27': emp.consultar_emprestimo_grupo_constructor,
}


def start() -> None:
    """
    Inicia e coordena o fluxo principal da aplicação.

    O dicionário sessao armazena o perfil autenticado
    e o identificador do estudante ou grupo responsável.

    As opções gerais permitem consultar e cadastrar
    usuários, materiais e categorias.

    Após a autenticação, são disponibilizadas operações
    específicas para estudantes ou grupos responsáveis.

    Cada opção chama o Constructor correspondente,
    responsável por integrar View, Controller e Repository.
    """
    sessao = {"tipo": None, "identidade": None}

    while True:
        command = introduction_process(sessao)

        if command == '1': usuario_register_constructor()
        elif command == '2': usuario_finder_constructor()
        elif command == '3': material_register_constructor()
        elif command == '4': material_finder_constructor()
        elif command == '10': tipo_material_register_constructor()
        elif command == '5' and sessao["tipo"] is None:
            conta = login_constructor()
            if conta is not None:
                sessao.update(conta)
        elif command == '6' and sessao["tipo"] is not None:
            sessao.update({"tipo": None, "identidade": None})
            LoginView().logout_message()
        elif sessao["tipo"] == "ESTUDANTE" and command in ACOES_ESTUDANTE:
            ACOES_ESTUDANTE[command](sessao["identidade"])
        elif sessao["tipo"] == "GRUPO" and command in ACOES_GRUPO:
            ACOES_GRUPO[command](sessao["identidade"])
        elif command == '0': exit()
        else: print('\n Comando não encontrado! \n')