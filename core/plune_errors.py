"""Exceções da API Plune (módulo leve para evitar import circular)."""


class PluneError(RuntimeError):
    pass


class PluneApiError(PluneError):
    def __init__(self, message: str, raw_error: str | None = None):
        super().__init__(message)
        self.raw_error = raw_error or message
