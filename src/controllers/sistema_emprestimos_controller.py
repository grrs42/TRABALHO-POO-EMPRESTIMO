"""Coordena as operações do ciclo de empréstimos acadêmicos.

Este primeiro incremento implementa somente a solicitação.
A reserva do exemplar e a criação do registro são responsabilidade
transacional do EmprestimosRepository.
"""

import re

from src.models.entities.emprestimo import Emprestimo, StatusEmprestimo


class SistemaEmprestimosController:
    def __init__(
        self,
        usuarios_repository,
        materiais_repository,
        emprestimos_repository,
    ) -> None:
        self.__usuarios_repository = usuarios_repository
        self.__materiais_repository = materiais_repository
        self.__emprestimos_repository = emprestimos_repository

    def solicitar_emprestimo(self, dados: dict) -> dict:
        """Registra solicitação pendente de um estudante para um exemplar."""
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
        """Confirma a retirada por um grupo autorizado."""
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

            # O repositório valida novamente estado e grupo sob transação.
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
        """Recusa uma solicitação e solicita a liberação do exemplar."""
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
        """Registra devolução de empréstimo ativo por seu grupo responsável.

        A liberação do material e a mudança de estado devem ocorrer juntas na transação.
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

    def __verificar_solicitacao_pendente(
        self, emprestimo_id: int, codigo_grupo: str
    ) -> None:
        """Pré-validação: banco deve repetir as verificações sob bloqueio."""
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
        """Pré-validação da devolução; transação deve repetir as verificações."""
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
        if not isinstance(codigo, str):
            raise PermissionError("Conta do grupo responsável não autenticada.")
        normalizado = codigo.strip().upper()
        if re.fullmatch(r"[A-Z0-9]+", normalizado) is None:
            raise PermissionError("Conta do grupo responsável não autenticada.")
        return normalizado

    @staticmethod
    def __validar_numero_positivo(valor: object, nome: str) -> int:
        """Aceita número inteiro ou sua representação textual (entrada do terminal)"""
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