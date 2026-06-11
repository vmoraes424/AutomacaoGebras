from __future__ import annotations

from pydantic import BaseModel, Field


class AutomacaoConfigBody(BaseModel):
    dev_pular_clicksign: bool = Field(
        False, description="Não chama a API Clicksign (útil em dev)"
    )
    teste_plune_sem_assinatura: bool = Field(
        False, description="Cria pedido Plune sem esperar assinatura Clicksign"
    )
    dev_hub_sem_aprovacao_plune: bool = Field(
        False, description="Cria pedido HUB após Plune no ganho (dev)"
    )
    pular_hub: bool = Field(False, description="Não cria pedido no HUB")
    formulario_web_enabled: bool = Field(
        True, description="Worker usa formulário web validado"
    )


class AutomacaoConfigResponse(AutomacaoConfigBody):
    updated_at: str | None = None
    mysql_database: str | None = None


class ConfigAccessResponse(BaseModel):
    password_required: bool
