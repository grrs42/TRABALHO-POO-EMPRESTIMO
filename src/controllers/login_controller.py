
from src.models.repositories.contas_acesso_repository import ContasAcessoRepository


class LoginController:
    """
    Coordena a autenticação de contas de acesso.

    Recebe login e senha, consulta a conta correspondente
    no ContasAcessoRepository e solicita a verificação
    da senha à entidade ContaAcesso.

    Quando a autenticação é válida, retorna o perfil
    e a identidade associados à conta.

    A manutenção da sessão autenticada é realizada
    pelo fluxo principal da aplicação.
    """

    # Mensagem genérica para falhas de autenticação.
    MENSAGEM_FALHA = "Login ou senha incorretos."

    def __init__(self, repository: ContasAcessoRepository) -> None:
        """
        Inicializa o Controller de autenticação.

        Args:
            repository: Repositório responsável por
                localizar contas de acesso no PostgreSQL.
        """
        self.__repository = repository

    def autenticar(self, dados: dict) -> dict:
        """
        Verifica as credenciais de uma conta de acesso.

        Etapas:
        Valida o formato dos dados recebidos
        Normaliza o login informado
        Consulta a conta de acesso
        Verifica a senha informada
        Retorna o perfil e a identidade da conta

        A senha é verificada por ContaAcesso, sem
        comparação direta de senhas em texto puro.

        Este método não cria nem encerra sessões e
        não modifica os registros do banco de dados.
        """
        try:
            if not isinstance(dados, dict):
                raise ValueError(self.MENSAGEM_FALHA)

            login = dados.get("login")
            senha = dados.get("senha")

            if not isinstance(login, str) or not isinstance(senha, str):
                raise ValueError(self.MENSAGEM_FALHA)

            login = login.strip()
            if not login.isdigit():
                login = login.upper()

            conta = self.__repository.select_conta(login)
            if conta is None or not conta.verificar_senha(senha):
                raise ValueError(self.MENSAGEM_FALHA)

            return {
                "success": True,
                "message": {
                    "tipo": conta.tipo,
                    "identidade": conta.identidade,
                },
            }

        except ValueError as erro:
            return {"success": False, "error": str(erro)}

        except Exception:
            return {
                "success": False,
                "error": "Não foi possível realizar o login."
            }