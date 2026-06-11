from __future__ import annotations


class FormularioDomainError(Exception):
    """Erro base do contexto formulário."""


class DealFormNotFoundError(FormularioDomainError):
    def __init__(self, deal_id: int) -> None:
        self.deal_id = deal_id
        super().__init__(f"Formulário do deal {deal_id} não encontrado.")


class DealFormNotEditableError(FormularioDomainError):
    def __init__(self, deal_id: int, status: str) -> None:
        self.deal_id = deal_id
        self.status = status
        super().__init__(
            f"Formulário do deal {deal_id} não pode ser editado (status={status})."
        )


class DealNotInContratoStageError(FormularioDomainError):
    def __init__(self, deal_id: int) -> None:
        self.deal_id = deal_id
        super().__init__(
            f"Deal {deal_id} não está aberto na etapa Contrato; "
            "formulário indisponível."
        )
