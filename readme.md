
# Sistema de Gerenciamento de Empréstimos Acadêmicos

Projeto desenvolvido para a disciplina de Programação Orientada a Objetos.


**Instituição:** Universidade Federal de Minas Gerais (UFMG)  
**Professora:** Luiza Bernardes Real 

**Alunos:** Gabriel dos Reis Rezende da Silva e Samara Fernandes Cordeiro

## Objetivo

Organizar o cadastro, a consulta e o empréstimo de materiais acadêmicos disponibilizados por grêmios, laboratórios e outros grupos responsáveis.

Funcionalidades:
- Cadastro e consulta de estudantes (com conta de acesso), tipos de material e exemplares.
- Login de estudante (pela matrícula) ou de grupo responsável (pelo código do grupo).
- Estudante: solicitar empréstimo, consultar histórico, multas simuladas e empréstimo por ID.
- Grupo: listar solicitações pendentes, aprovar (com prazo em dias), recusar, registrar devolução, listar empréstimos ativos, gerar avisos de atraso simulados e consultar empréstimo por ID.

## Tecnologias utilizadas

- Python 3.10 ou >
- PostgreSQL
- DBeaver (opcional, para administrar o banco)
- Biblioteca psycopg2
- Biblioteca python-dotenv

## Organização do projeto

- `src/models/entities/`: entidades e subclasses.
- `src/models/factories/`: fábrica de materiais.
- `src/models/repositories/`: persistência no PostgreSQL.
- `src/models/services/`: serviço de e-mail simulado.
- `src/controllers/`: regras de negócio e coordenação dos fluxos.
- `src/views/`: interação pelo terminal.
- `src/main/`: montagem das dependências (constructors) e menu.
- `database/schema.sql`: estrutura completa do banco.
- `database/migrations/`: alterações para bancos criados em versões anteriores.
- `database/seeds/`: dados fictícios de demonstração.
- `tests/`: testes automatizados.
- `run.py`: ponto de entrada da aplicação.

## Configuração do ambiente

Na pasta principal do projeto, crie um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Configuração do PostgreSQL

**Banco novo:**

1. Crie um banco PostgreSQL novo e vazio.
2. Abra um editor SQL conectado a esse banco no DBeaver.
3. Execute o conteúdo de `database/schema.sql`.
4. Execute os arquivos de demonstração nesta ordem:

   - `database/seeds/001_grupo_teste.sql`
   - `database/seeds/002_tipos_material_teste.sql`
   - `database/seeds/003_materiais_teste.sql`
   - `database/seeds/004_usuarios_contas_teste.sql`

**Banco criado em versão anterior:** execute somente as migrations ainda não aplicadas (`001_atributos_materiais.sql`, `002_emprestimos_contas.sql`) e depois o seed `004_usuarios_contas_teste.sql`. Não execute o `schema.sql` sobre tabelas existentes.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emprestimos_poo
DB_USER=postgres
DB_PASSWORD=coloque_sua_senha

# Opcional: banco separado usado pelos testes de integração
DB_TEST_NAME=emprestimos_poo_teste
```

Adapte os valores à sua instalação do PostgreSQL. O arquivo `.env` não deve ser versionado.

## Executando o programa

```bash
python run.py
```

O menu mostra opções diferentes conforme a conta conectada:

| Opção | Quem | Ação |
|---|---|---|
| 1, 2 | Todos | Cadastrar (com senha) / consultar estudante |
| 3, 4 | Todos | Cadastrar / consultar material |
| 10 | Todos | Cadastrar tipo de material |
| 5 / 6 | Todos | Entrar / sair da conta |
| 11–14 | Estudante | Solicitar empréstimo, meus empréstimos, minhas multas, consultar por ID |
| 21–27 | Grupo | Pendentes, aprovar, recusar, devolução, ativos, avisos de atraso, consultar por ID |

A matrícula e o código do grupo usados nas operações vêm sempre da conta conectada.

## Dados de demonstração

Todos os dados abaixo são fictícios.

| Código | Material | Atributos específicos |
|---|---|---|
| JAL-001 | Jaleco | Tamanho M |
| LIV-001 | Livro | Título e editora |
| CAL-001 | Calculadora | Modelo C-100 |
| REG-001 | Régua | Descrição de 30 cm |

Todos pertencem ao grupo `GEES`. O grupo `LABFIS` não possui materiais e serve para demonstrar que um grupo não pode operar materiais de outro.

Contas de acesso (o banco guarda somente o hash das senhas):

| Login | Tipo | Senha de demonstração |
|---|---|---|
| 2026000001 | Estudante | estudante123 |
| GEES | Grupo | gees1234 |
| LABFIS | Grupo | labfis1234 |

Contas de grupo são criadas somente pelo seed; o cadastro público (opção 1) cria apenas contas de estudante.

## Regras principais

- Matrícula: exatamente 10 dígitos.
- Uma solicitação PENDENTE já reserva o exemplar; aprovação o mantém indisponível; recusa e devolução o liberam. O banco impede mais de um empréstimo aberto por exemplar.
- Prazo de devolução em dias corridos, definido pelo grupo na aprovação.
- Multa simulada de R$ 2,00 por dia corrido após o vencimento; congelada na devolução. Não há cobrança nem pagamento.
- Avisos de atraso são **simulados**: a opção 26 grava o texto do "e-mail" em `avisos_simulados.log`, sem enviar nada.

## Executando os testes

Na raiz do projeto, execute:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Os testes de entidades, controllers, login e avisos usam repositórios simulados e não precisam de banco.

Os testes de `tests/test_emprestimos_repository_db.py` usam PostgreSQL real e só rodam se `DB_TEST_NAME` estiver no `.env`. Prepare esse banco **separado** do banco de demonstração com `schema.sql` e os seeds 001 a 004. Os testes apagam os empréstimos desse banco a cada execução.
