def introduction_page() -> str:
    print("\n" + "=" * 45)
    print(" SISTEMA DE EMPRÉSTIMOS ACADÊMICOS")
    print("=" * 45)
    print("1  - Cadastrar usuário")
    print("2  - Consultar usuário")
    print("3  - Cadastrar material")
    print("4  - Consultar material")
    print("10 - Cadastrar tipo de material")
    print("0  - Sair")
    print("=" * 45)

    return input("Escolha uma opção: ").strip()
