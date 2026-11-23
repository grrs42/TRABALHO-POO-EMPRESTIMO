
import re
from decimal import Decimal

from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo


class SistemaEmprestimosController:
    """
    Coordena as funcionalidades de gerenciamento de empréstimos.

    Recebe os dados das operações, valida identificadores e
    contextos de acesso e utiliza os repositórios para consultar
    ou modificar os registros.

    Abrange solicitação, aprovação, recusa, devolução, consultas,
    acompanhamento de multas e geração de avisos simulados.

    As regras de estado são definidas pela entidade Emprestimo.
    As operações de persistência e as transações são
    responsabilidade dos repositórios.
    """

    def __init__(
        self,
        usuarios_repository,
        materiais_repository,
        emprestimos_repository,
        notificador=None,
    ) -> None:
        self.__usuarios_repository = usuarios_repository
        self.__materiais_repository = materiais_repository
        self.__emprestimos_repository = emprestimos_repository
        self.__notificador = notificador

    def solicitar_emprestimo(self, dados: dict) -> dict:
        """
        Registra uma solicitação de empréstimo.

        Verifica a existência do estudante e do material,
        além da disponibilidade do exemplar.

        Em caso de sucesso, o repositório cria o empréstimo
        PENDENTE e reserva o exemplar na mesma transação.
        """
        try:
            matricula, codigo = self.__validar_dados_solicitacao(dados)

            usuario = self.__usuarios_repository.select_usuario(matricula)
            if usuario is None:
                raise ValueError("Estudante não encontrado.")

            material = self.__materiais_repository.select_material(codigo)
            if material is None:
                raise ValueError("Material não encontrado.")
            if not material.verificar_disponibilidade():
                raise ValueError("Material indisponível para empréstimo.")

            emprestimo = Emprestimo(usuario=usuario, material=material)
            emprestimo_salvo = self.__emprestimos_repository.registrar_solicitacao(
                emprestimo
            )
            return {
                "success": True,
                "message": {
                    "count": 1,
                    "type": "Empréstimo",
                    "attributes": emprestimo_salvo.to_dict(),
                },
            }
        except (ValueError, TypeError, KeyError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível registrar a solicitação."}

    @staticmethod
    def __validar_dados_solicitacao(dados: dict) -> tuple[str, str]:
        """
        Valida e normaliza os identificadores da solicitação.

        Raises:
            ValueError: Se os dados ou identificadores
                não seguirem os formatos esperados.

        O código deve seguir o formato CAL-001, aceitando
        três ou mais dígitos após o hífen.
        """
        if not isinstance(dados, dict):
            raise ValueError("Os dados da solicitação devem ser um dicionário.")

        matricula = dados.get("matricula")
        codigo = dados.get("codigo_material")

        if not isinstance(matricula, str):
            raise ValueError("Informe uma matrícula.")
        matricula = matricula.strip()
        if re.fullmatch(r"[0-9]{10}", matricula) is None:
            raise ValueError("A matrícula deve conter 10 dígitos.")

        if not isinstance(codigo, str):
            raise ValueError("Informe o código do material.")
        codigo = codigo.strip().upper()
        if re.fullmatch(r"[A-Z]{3}-[0-9]{3,}", codigo) is None:
            raise ValueError("Código inválido. Exemplo: CAL-001.")

        return matricula, codigo

    def aprovar_emprestimo(
        self, dados: dict, codigo_grupo_autenticado: str
    ) -> dict:
        """
        Aprova uma solicitação pendente de empréstimo.

        Valida o ID, o prazo em dias corridos, a autorização
        do grupo e o estado PENDENTE da solicitação.

        O repositório registra a aprovação e o prazo.
        """
        try:
            if not isinstance(dados, dict):
                raise ValueError("Os dados da aprovação devem ser um dicionário.")

            emprestimo_id = self.__validar_numero_positivo(
                dados.get("id_emprestimo"), "ID do empréstimo"
            )
            prazo_dias = self.__validar_numero_positivo(
                dados.get("prazo_dias"), "Prazo em dias"
            )
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            self.__verificar_solicitacao_pendente(emprestimo_id, grupo)

            aprovado = self.__emprestimos_repository.aprovar_solicitacao(
                emprestimo_id, grupo, prazo_dias
            )
            return self.__formatar_emprestimo(aprovado)
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível aprovar a solicitação."}

    def recusar_emprestimo(
        self, dados: dict, codigo_grupo_autenticado: str
    ) -> dict:
        """
        Recusa uma solicitação pendente de empréstimo.

        Valida a autorização do grupo e o estado PENDENTE.
        O repositório altera o estado para RECUSADO e
        libera o exemplar na mesma transação.
        """
        try:
            if not isinstance(dados, dict):
                raise ValueError("Os dados da recusa devem ser um dicionário.")

            emprestimo_id = self.__validar_numero_positivo(
                dados.get("id_emprestimo"), "ID do empréstimo"
            )
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            self.__verificar_solicitacao_pendente(emprestimo_id, grupo)

            recusado = self.__emprestimos_repository.recusar_solicitacao(
                emprestimo_id, grupo
            )
            return self.__formatar_emprestimo(recusado)
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível recusar a solicitação."}

    def registrar_devolucao(
        self, dados: dict, codigo_grupo_autenticado: str
    ) -> dict:
        """
        Registra a devolução de um empréstimo ativo.

        Confirma que o empréstimo está ATIVO e pertence
        ao grupo responsável. O repositório registra
        a devolução e libera o material em uma transação.
        """
        try:
            if not isinstance(dados, dict):
                raise ValueError("Os dados da devolução devem ser um dicionário.")

            emprestimo_id = self.__validar_numero_positivo(
                dados.get("id_emprestimo"), "ID do empréstimo"
            )
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            self.__verificar_emprestimo_ativo(emprestimo_id, grupo)

            devolvido = self.__emprestimos_repository.registrar_devolucao(
                emprestimo_id, grupo
            )
            return self.__formatar_emprestimo(devolvido)
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível registrar a devolução."}

    def consultar_emprestimo(
        self,
        dados: dict,
        matricula_autenticada: str | None = None,
        codigo_grupo_autenticado: str | None = None,
    ) -> dict:
        """
        Consulta um empréstimo pelo identificador.

        Exige exatamente um dos contextos autenticados.
        Estudantes consultam seus próprios empréstimos e
        grupos consultam empréstimos de seus materiais.
        """
        try:
            contexto = self.__validar_contexto_consulta(
                matricula_autenticada, codigo_grupo_autenticado
            )
            if not isinstance(dados, dict):
                raise ValueError("Informe os dados da consulta.")
            emprestimo_id = self.__validar_numero_positivo(
                dados.get("id_emprestimo"), "ID do empréstimo"
            )
            emprestimo = self.__emprestimos_repository.select_emprestimo(
                emprestimo_id
            )
            if emprestimo is None or not self.__pertence_ao_contexto(
                emprestimo, contexto
            ):
                raise ValueError("Empréstimo não encontrado ou acesso não autorizado.")
            return self.__formatar_emprestimo(emprestimo)
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível consultar o empréstimo."}

    def listar_emprestimos_usuario(self, matricula_autenticada: str) -> dict:
        """
        Consulta o histórico de empréstimos de um estudante.

        Verifica se todos os registros recuperados pertencem
        à matrícula informada
        """
        try:
            matricula = self.__validar_matricula_autenticada(matricula_autenticada)
            emprestimos = self.__emprestimos_repository.list_emprestimos_usuario(
                matricula
            )
            self.__validar_lista_usuario(emprestimos, matricula)
            return self.__formatar_lista_emprestimos(emprestimos, "Empréstimos")
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível listar os empréstimos."}

    def listar_solicitacoes_pendentes(
        self, codigo_grupo_autenticado: str
    ) -> dict:
        """
        Lista solicitações pendentes de um grupo responsável.

        Confere o estado e a associação de cada registro
        ao grupo autenticado. Uma lista vazia é válida.
        """
        try:
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            emprestimos = self.__emprestimos_repository.list_emprestimos_pendentes(
                grupo
            )
            self.__validar_lista_emprestimos(emprestimos)
            if any(
                item.material.grupo.codigo.upper() != grupo
                or item.status != StatusEmprestimo.PENDENTE
                for item in emprestimos
            ):
                raise RuntimeError("Resultado inconsistente na consulta de pendências.")
            return self.__formatar_lista_emprestimos(emprestimos, "Solicitações pendentes")
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível listar as solicitações."}

    def listar_emprestimos_ativos(self, codigo_grupo_autenticado: str) -> dict:
        """
        Lista os empréstimos ativos de um grupo responsável.

        Utiliza uma consulta auxiliar que valida os registros
        recuperados. Uma lista vazia é válida.
        """
        try:
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            emprestimos = self.__listar_ativos_do_grupo(grupo)
            return self.__formatar_lista_emprestimos(emprestimos, "Empréstimos ativos")
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível listar os empréstimos ativos."}

    def gerar_avisos_atraso(self, codigo_grupo_autenticado: str) -> dict:
        """
        Gera avisos simulados para empréstimos ativos atrasados.

        Exige que o serviço de notificação esteja configurado.
        Para cada empréstimo atrasado, chama o notificador.
        """
        try:
            grupo = self.__validar_grupo_autenticado(codigo_grupo_autenticado)
            if self.__notificador is None:
                raise ValueError("Serviço de avisos não configurado.")
            atrasados = [
                item for item in self.__listar_ativos_do_grupo(grupo)
                if item.esta_atrasado()
            ]
            for item in atrasados:
                self.__notificador.enviar_aviso_atraso(item)
            return self.__formatar_lista_emprestimos(atrasados, "Avisos de atraso simulados")
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível gerar os avisos."}

    def __listar_ativos_do_grupo(self, grupo: str) -> list:
        """
        Recupera e valida os empréstimos ativos do grupo.
        """
        emprestimos = self.__emprestimos_repository.list_emprestimos_ativos(grupo)
        self.__validar_lista_emprestimos(emprestimos)
        if any(
            item.material.grupo.codigo.upper() != grupo
            or item.status != StatusEmprestimo.ATIVO
            for item in emprestimos
        ):
            raise RuntimeError("Resultado inconsistente na consulta de ativos.")
        return emprestimos

    def listar_pendencias_usuario(self, matricula_autenticada: str) -> dict:
        """
        Consulta multas simuladas associadas a um estudante.

        Utiliza os métodos da entidade Emprestimo para
        calcular os valores de atraso e multa.

        Sem multas, retorna uma lista vazia e total zero.
        Não realiza cobranças nem altera os registros.
        """
        try:
            matricula = self.__validar_matricula_autenticada(matricula_autenticada)
            emprestimos = self.__emprestimos_repository.list_emprestimos_usuario(
                matricula
            )
            self.__validar_lista_usuario(emprestimos, matricula)
            pendencias = [
                item for item in emprestimos if item.calcular_multa() > 0
            ]
            total = sum(
                (item.calcular_multa() for item in pendencias), Decimal("0.00")
            )
            resposta = self.__formatar_lista_emprestimos(pendencias, "Pendências")
            resposta["message"]["total_multa_calculada"] = str(total)
            return resposta
        except (ValueError, TypeError, PermissionError) as erro:
            return {"success": False, "error": str(erro)}
        except Exception:
            return {"success": False, "error": "Não foi possível consultar as pendências."}

    @staticmethod
    def __validar_matricula_autenticada(matricula: str) -> str:
        """
        Verifica o identificador do estudante autenticado.
        """
        if not isinstance(matricula, str):
            raise PermissionError("Conta de estudante não autenticada.")
        normalizada = matricula.strip()
        if re.fullmatch(r"[0-9]{10}", normalizada) is None:
            raise PermissionError("Conta de estudante não autenticada.")
        return normalizada

    @classmethod
    def __validar_contexto_consulta(
        cls,
        matricula: str | None,
        codigo_grupo: str | None,
    ) -> tuple[str, str]:
        """
        Identifica e valida o perfil utilizado em uma consulta.
        """
        if (matricula is None) == (codigo_grupo is None):
            raise PermissionError("Informe exatamente uma conta autenticada para consulta.")
        if matricula is not None:
            return ("usuario", cls.__validar_matricula_autenticada(matricula))
        return ("grupo", cls.__validar_grupo_autenticado(codigo_grupo))

    @staticmethod
    def __pertence_ao_contexto(
        emprestimo: Emprestimo, contexto: tuple[str, str]
    ) -> bool:
        """
        Verifica a autorização de acesso a um empréstimo.
        """
        if not isinstance(emprestimo, Emprestimo):
            return False
        tipo, codigo = contexto
        if tipo == "usuario":
            return emprestimo.usuario.matricula == codigo
        return emprestimo.material.grupo.codigo.upper() == codigo

    @staticmethod
    def __validar_lista_emprestimos(emprestimos: list) -> None:
        """
        Verifica o formato dos resultados do repositório.
        """
        if not isinstance(emprestimos, list) or any(
            not isinstance(item, Emprestimo) for item in emprestimos
        ):
            raise RuntimeError("O repositório retornou uma lista inválida.")

    @classmethod
    def __validar_lista_usuario(cls, emprestimos: list, matricula: str) -> None:
        """
        Verifica se uma lista pertence ao estudante informado.
        """
        cls.__validar_lista_emprestimos(emprestimos)
        if any(item.usuario.matricula != matricula for item in emprestimos):
            raise RuntimeError("O repositório retornou dados de outro estudante.")

    @staticmethod
    def __formatar_lista_emprestimos(
        emprestimos: list[Emprestimo], tipo: str
    ) -> dict:
        """
        Organiza uma lista de empréstimos para apresentação.

        Uma lista vazia é apresentada como resultado válido.
        """
        return {
            "success": True,
            "message": {
                "count": len(emprestimos),
                "type": tipo,
                "attributes": [item.to_dict() for item in emprestimos],
            },
        }

    def __verificar_solicitacao_pendente(
        self, emprestimo_id: int, codigo_grupo: str
    ) -> None:
        """
        Verifica se uma solicitação pode ser processada.

        Não modifica o empréstimo, apenas verifica
        as condições anteriores à aprovação ou recusa.
        """
        emprestimo = self.__emprestimos_repository.select_emprestimo(
            emprestimo_id
        )
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")

        if emprestimo.material.grupo.codigo.upper() != codigo_grupo:
            raise PermissionError("Este grupo não pode operar o material informado.")
        if emprestimo.status != StatusEmprestimo.PENDENTE:
            raise ValueError("Somente solicitações pendentes podem ser processadas.")

    def __verificar_emprestimo_ativo(
        self, emprestimo_id: int, codigo_grupo: str
    ) -> None:
        """
        Verifica se um empréstimo pode ser devolvido.
        """
        emprestimo = self.__emprestimos_repository.select_emprestimo(
            emprestimo_id
        )
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")

        if emprestimo.material.grupo.codigo.upper() != codigo_grupo:
            raise PermissionError("Este grupo não pode operar o material informado.")
        if emprestimo.status != StatusEmprestimo.ATIVO:
            raise ValueError("Somente empréstimos ativos podem ser devolvidos.")

    @staticmethod
    def __validar_grupo_autenticado(codigo: str) -> str:
        """
        Valida o identificador de um grupo autenticado.
        """
        if not isinstance(codigo, str):
            raise PermissionError("Conta do grupo responsável não autenticada.")
        normalizado = codigo.strip().upper()
        if re.fullmatch(r"[A-Z0-9]+", normalizado) is None:
            raise PermissionError("Conta do grupo responsável não autenticada.")
        return normalizado

    @staticmethod
    def __validar_numero_positivo(valor: object, nome: str) -> int:
        """
        Converte e valida um identificador ou prazo positivo.

        Valores booleanos e números fracionários não são aceitos.
        """
        if type(valor) is int:
            numero = valor
        elif isinstance(valor, str) and re.fullmatch(r"[0-9]+", valor.strip()):
            numero = int(valor.strip())
        else:
            raise ValueError(f"{nome} deve ser um número inteiro positivo.")
        if numero <= 0:
            raise ValueError(f"{nome} deve ser um número inteiro positivo.")
        return numero

    @staticmethod
    def __formatar_emprestimo(emprestimo: Emprestimo) -> dict:
        return {
            "success": True,
            "message": {
                "count": 1,
                "type": "Empréstimo",
                "attributes": emprestimo.to_dict(),
            },
        }