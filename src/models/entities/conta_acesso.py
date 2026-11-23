
import hashlib
import hmac
import os


class ContaAcesso:
    """
    Representa uma conta utilizada para autenticação.

    Armazena o login, o tipo de perfil, o hash da senha,
    o salt e o vínculo com um estudante ou grupo responsável.

    Cada conta pertence exclusivamente a um dos perfis:
    ESTUDANTE ou GRUPO.

    As senhas não são armazenadas em texto puro.
    O sistema utiliza PBKDF2-HMAC-SHA256 com salt
    para gerar e verificar os hashes das senhas.

    Esta classe representa as credenciais de acesso,
    mantendo-as separadas das entidades do domínio.
    """

    # Perfis de autenticação reconhecidos pelo sistema.
    ESTUDANTE = "ESTUDANTE"
    GRUPO = "GRUPO"

    # Parâmetros utilizados no processamento das senhas.
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
        """
        Inicializa uma conta de acesso.

        Args:
            login: Identificador utilizado na autenticação.
            tipo: Perfil ESTUDANTE ou GRUPO.
            senha_hash: Hash da senha previamente gerado.
            salt: Valor utilizado na geração do hash.
            usuario_matricula: Matrícula vinculada à conta
                de estudante, quando aplicável.
            grupo_codigo: Código vinculado à conta
                de grupo, quando aplicável.

        Raises:
            ValueError: Se o login ou o tipo forem inválidos,
                se o vínculo não corresponder ao perfil ou
                se o hash e o salt estiverem ausentes.

        A conta deve estar vinculada a uma matrícula
        ou a um grupo responsável, nunca aos dois.
        """
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
        """
        Cria uma conta vinculada a um estudante.

        Args:
            matricula: Matrícula utilizada como login.
            senha: Senha em texto puro informada no cadastro.

        Returns:
            Instância de ContaAcesso com perfil ESTUDANTE,
            hash, salt e vínculo com a matrícula.

        Raises:
            ValueError: Se a senha não atender ao tamanho
                mínimo exigido por gerar_hash().

        A senha é convertida em hash antes da criação
        do objeto e não fica armazenada em texto puro.
        """
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
        """
        Gera o hash de uma senha utilizando PBKDF2-HMAC.

        Args:
            senha: Senha em texto puro.
            salt: Valor hexadecimal opcional.
                Quando omitido, é gerado aleatoriamente.

        Returns:
            Tupla contendo o hash e o salt, ambos
            representados como strings hexadecimais.

        Raises:
            ValueError: Se a senha não for uma string
                com pelo menos seis caracteres.

        O algoritmo utiliza SHA-256 e a quantidade
        de iterações definida pela classe.
        """
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
        """
        Verifica se a senha informada corresponde à conta.

        Args:
            senha: Senha em texto puro a ser verificada.

        Returns:
            True se o hash calculado corresponder
            ao hash armazenado; False caso contrário.

        Senhas vazias ou valores que não sejam strings
        são rejeitados com retorno False.

        A comparação utiliza hmac.compare_digest().
        Não altera os dados da conta.
        """
        if not isinstance(senha, str) or not senha:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(self.__salt), self.ITERACOES
        ).hex()
        return hmac.compare_digest(calculado, self.__senha_hash)

    @property
    def login(self) -> str:
        """Retorna o identificador utilizado no login."""
        return self.__login

    @property
    def tipo(self) -> str:
        """Retorna o perfil da conta de acesso."""
        return self.__tipo

    @property
    def senha_hash(self) -> str:
        """Retorna o hash armazenado da senha."""
        return self.__senha_hash

    @property
    def salt(self) -> str:
        """Retorna o salt utilizado na geração do hash."""
        return self.__salt

    @property
    def usuario_matricula(self) -> str | None:
        """Retorna a matrícula vinculada, quando existente."""
        return self.__usuario_matricula

    @property
    def grupo_codigo(self) -> str | None:
        """Retorna o código do grupo vinculado, quando existente."""
        return self.__grupo_codigo

    @property
    def identidade(self) -> str:
        """
        Retorna o identificador associado ao perfil.

        Returns:
            Matrícula do estudante, para contas ESTUDANTE,
            ou código do grupo, para contas GRUPO.

        Permite identificar a entidade associada
        à conta autenticada.
        """
        if self.__tipo == self.ESTUDANTE:
            return self.__usuario_matricula
        return self.__grupo_codigo