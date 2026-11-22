from src.models.repositories.contas_acesso_repository import ContasAcessoRepository


class LoginController:
    MENSAGEM_FALHA = "Login ou senha incorretos."

    def __init__(self, repository: ContasAcessoRepository) -> None:
        self.__repository = repository

    def autenticar(self, dados: dict) -> dict:
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
            return {"success": False, "error": "Não foi possível realizar o login."}
