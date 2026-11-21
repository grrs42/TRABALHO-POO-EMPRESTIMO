"""Coordena as operações do ciclo de empréstimos acadêmicos.

Este primeiro incremento implementa somente a solicitação.
A reserva do exemplar e a criação do registro são responsabilidade
transacional do EmprestimosRepository.
"""

import re

from src.models.entities.emprestimo import Emprestimo


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
        """Registra solicitação pendente de um estudante para um exemplar"""
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