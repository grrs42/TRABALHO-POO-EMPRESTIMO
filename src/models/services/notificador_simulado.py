from datetime import date, datetime

from src.models.entities.emprestimo import Emprestimo


class NotificadorEmailSimulado:
    def __init__(self, caminho_arquivo: str = "avisos_simulados.log") -> None:
        self.__caminho_arquivo = caminho_arquivo

    @property
    def caminho_arquivo(self) -> str:
        return self.__caminho_arquivo

    def enviar_aviso_atraso(self, emprestimo: Emprestimo, hoje: date | None = None) -> str:
        if not isinstance(emprestimo, Emprestimo):
            raise TypeError("Informe um empréstimo.")
        if not emprestimo.esta_atrasado(hoje):
            raise ValueError("Empréstimo sem atraso: aviso não enviado.")

        referencia = hoje if hoje is not None else date.today()
        mensagem = (
            f"{datetime.now().isoformat(timespec='seconds')} | "
            f"PARA: estudante {emprestimo.usuario.matricula} | "
            f"ASSUNTO: Devolução atrasada | "
            f"Empréstimo {emprestimo.id}, material {emprestimo.material.codigo}: "
            f"vencimento em {emprestimo.data_prevista_devolucao.isoformat()}, "
            f"{emprestimo.dias_atraso(referencia)} dia(s) de atraso, "
            f"multa simulada R$ {emprestimo.calcular_multa(referencia)}."
        )
        with open(self.__caminho_arquivo, "a", encoding="utf-8") as arquivo:
            arquivo.write(mensagem + "\n")
        return mensagem
