def introduction_page(sessao: dict) -> str:
    print("\n" + "=" * 45)
    print(" SISTEMA DE EMPRÉSTIMOS ACADÊMICOS")
    if sessao["tipo"] == "ESTUDANTE":
        print(f" Conectado: estudante {sessao['identidade']}")
    elif sessao["tipo"] == "GRUPO":
        print(f" Conectado: grupo {sessao['identidade']}")
    print("=" * 45)
    print("1  - Cadastrar usuário")
    print("2  - Consultar usuário")
    print("3  - Cadastrar material")
    print("4  - Consultar material")
    print("10 - Cadastrar tipo de material")

    if sessao["tipo"] is None:
        print("5  - Entrar")
    else:
        print("6  - Sair da conta")

    if sessao["tipo"] == "ESTUDANTE":
        print("-" * 45)
        print("11 - Solicitar empréstimo")
        print("12 - Meus empréstimos")
        print("13 - Minhas multas")
        print("14 - Consultar empréstimo por ID")
    elif sessao["tipo"] == "GRUPO":
        print("-" * 45)
        print("21 - Solicitações pendentes")
        print("22 - Aprovar solicitação")
        print("23 - Recusar solicitação")
        print("24 - Registrar devolução")
        print("25 - Empréstimos ativos")
        print("26 - Gerar avisos de atraso (simulado)")
        print("27 - Consultar empréstimo por ID")

    print("0  - Sair")
    print("=" * 45)

    return input("Escolha uma opção: ").strip()
