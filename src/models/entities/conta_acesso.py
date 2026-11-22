import hashlib
import hmac
import os


class ContaAcesso:
    ESTUDANTE = "ESTUDANTE"
    GRUPO = "GRUPO"
    TAMANHO_MINIMO_SENHA = 6
    ITERACOES = 200_000

    def __init__(
        self,
        login: str,
        tipo: str,
        senha_hash: str,
        salt: str,
        usuario_matricula: str | None = None,
        grupo_codigo: str | None = None,
    ) -> None:
        if not isinstance(login, str) or not login.strip():
            raise ValueError("Login inválido.")
        if tipo not in (self.ESTUDANTE, self.GRUPO):
            raise ValueError("Tipo de conta inválido.")
        if tipo == self.ESTUDANTE and (usuario_matricula is None or grupo_codigo is not None):
            raise ValueError("Conta de estudante deve estar vinculada somente a uma matrícula.")
        if tipo == self.GRUPO and (grupo_codigo is None or usuario_matricula is not None):
            raise ValueError("Conta de grupo deve estar vinculada somente a um grupo.")
        if not senha_hash or not salt:
            raise ValueError("Hash e salt da senha são obrigatórios.")

        self.__login = login.strip()
        self.__tipo = tipo
        self.__senha_hash = senha_hash
        self.__salt = salt
        self.__usuario_matricula = usuario_matricula
        self.__grupo_codigo = grupo_codigo

    @classmethod
    def criar_para_estudante(cls, matricula: str, senha: str) -> "ContaAcesso":
        senha_hash, salt = cls.gerar_hash(senha)
        return cls(
            login=matricula,
            tipo=cls.ESTUDANTE,
            senha_hash=senha_hash,
            salt=salt,
            usuario_matricula=matricula,
        )

    @classmethod
    def gerar_hash(cls, senha: str, salt: str | None = None) -> tuple[str, str]:
        if not isinstance(senha, str) or len(senha) < cls.TAMANHO_MINIMO_SENHA:
            raise ValueError(
                f"A senha deve ter pelo menos {cls.TAMANHO_MINIMO_SENHA} caracteres."
            )
        salt = salt if salt is not None else os.urandom(16).hex()
        senha_hash = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(salt), cls.ITERACOES
        ).hex()
        return senha_hash, salt

    def verificar_senha(self, senha: str) -> bool:
        if not isinstance(senha, str) or not senha:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(self.__salt), self.ITERACOES
        ).hex()
        return hmac.compare_digest(calculado, self.__senha_hash)

    @property
    def login(self) -> str:
        return self.__login

    @property
    def tipo(self) -> str:
        return self.__tipo

    @property
    def senha_hash(self) -> str:
        return self.__senha_hash

    @property
    def salt(self) -> str:
        return self.__salt

    @property
    def usuario_matricula(self) -> str | None:
        return self.__usuario_matricula

    @property
    def grupo_codigo(self) -> str | None:
        return self.__grupo_codigo

    @property
    def identidade(self) -> str:
        if self.__tipo == self.ESTUDANTE:
            return self.__usuario_matricula
        return self.__grupo_codigo
