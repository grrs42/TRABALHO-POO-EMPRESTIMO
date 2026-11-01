
# Sistema de Gerenciamento de Empréstimos Acadêmicos

Projeto desenvolvido para a disciplina de Programação Orientada a Objetos.


**Instituição:** Universidade Federal de Minas Gerais (UFMG)  
**Professora:** Luiza Bernardes Real 

**Alunos:** Gabriel dos Reis, Mariana Moreno e Samara Cordeiro

## Objetivo

Organizar o cadastro e a consulta de materiais acadêmicos disponibilizados por grêmios, laboratórios e outros grupos responsáveis.

O protótipo da Entrega 3 implementa as duas funcionalidades principais:
- Cadastro de exemplares de materiais acadêmicos.
- Consulta de materiais pelo código individual.

## Tecnologias utilizadas

- Python 3.10 ou superior
- PostgreSQL
- DBeaver (opcional, para administrar o banco)
- Biblioteca psycopg2
- Biblioteca python-dotenv

## Organização do projeto

- `src/models/entities/`: entidades e subclasses.
- `src/models/factories/`: fábrica de materiais.
- `src/models/repositories/`: persistência no PostgreSQL.
- `src/controllers/`: lógica dos fluxos de cadastro e consulta.
- `src/views/`: interação pelo terminal.
- `database/schema.sql`: estrutura completa do banco.
- `database/migrations/`: alterações na estrutura anterior.
- `database/seeds/`: dados fictícios de demonstração.
- `tests/`: testes automatizados.
- `run.py`: ponto de entrada da aplicação.

## Configuração do ambiente

Na pasta principal do projeto, crie um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Configuração do PostgreSQL

1. Crie um banco PostgreSQL novo e vazio.
2. Abra um editor SQL conectado a esse banco no DBeaver.
3. Execute o conteúdo de `database/schema.sql`.
4. Execute os arquivos de demonstração nesta ordem:

   - `database/seeds/001_grupo_teste.sql`
   - `database/seeds/002_tipos_material_teste.sql`
   - `database/seeds/003_materiais_teste.sql`

A pasta `migrations/` documenta alterações em bancos existentes.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emprestimos_poo_teste
DB_USER=postgres
DB_PASSWORD=coloque_sua_senha
```

Adapte os valores à sua instalação do PostgreSQL.

## Executando o programa

Com o ambiente configurado, o programa disponibiliza um menu interativo pelo terminal.

As funcionalidades principais do protótipo são:

- Opção 3: registrar material.
- Opção 4: consultar material.
- Opção 10: cadastrar tipo de material.

## Dados de demonstração

O banco de demonstração contém o grupo fictício `GEES` e os seguintes exemplares:

| Código | Material | Atributos específicos |
|---|---|---|
| JAL-001 | Jaleco | Tamanho M |
| LIV-001 | Livro | Título e editora |
| CAL-001 | Calculadora | Modelo C-100 |
| REG-001 | Régua | Descrição de 30 cm |

Esses exemplares são destinados exclusivamente à demonstração.

## Executando os testes

Na raiz do projeto, execute:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Os testes verificam as entidades, a função de instanciar os materiais, validação de dados e os fluxos de cadastro e consulta com repositórios simulados.
