"""Schema Pydantic do formulário web v1 (chaves legíveis)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .pipedrive_fields import (
    FIELD_CEP,
    FIELD_CIDADE,
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_CONTATO_CONTRATANTE,
    FIELD_CONTATO_FINANCEIRO,
    FIELD_CONTATO_PRINCIPAL,
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_DOCUMENTO,
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_GEBRAS,
    FIELD_EMAIL_DIRETOR_GEBRAS,
    FIELD_ENDERECO,
    FIELD_FILIAL,
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_INSCRICAO_ESTADUAL,
    FIELD_INSCRICAO_MUNICIPAL,
    FIELD_NOME_CLIENTE,
    FIELD_NOTAS,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_PERCENTUAL_EXITO,
    FIELD_QTD_SOLE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_QUANTIDADE_UCS,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
)


class _FormSection(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ClienteV1(_FormSection):
    contratante: str = ""
    documento: str = ""
    endereco: str = ""
    cep: str = ""
    municipio_estado: str = ""
    inscricao_estadual: str = ""
    inscricao_municipal: str = ""
    notas: str = ""
    codigo_cliente_instalacao: str = ""


class ServicosV1(_FormSection):
    sole_web: int = 0
    sole_consultoria: int = 0
    gestao_acl: int = 0
    gestao_usina_fotovoltaica: int = 0
    gestao_qualidade_energia: int = 0
    quantidade_ucs: int = 0

    @field_validator(
        "sole_web",
        "sole_consultoria",
        "gestao_acl",
        "gestao_usina_fotovoltaica",
        "gestao_qualidade_energia",
        "quantidade_ucs",
        mode="before",
    )
    @classmethod
    def _coerce_int(cls, value: Any) -> int:
        if value is None or value == "":
            return 0
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0


class ValoresV1(_FormSection):
    valor_recorrencia: str = ""
    valor_implantacao: str = ""


class DatasV1(_FormSection):
    data_pagamento_implantacao: str = ""
    data_primeira_cobranca: str = ""


class ComercialV1(_FormSection):
    filial: str = ""
    regional: str = ""
    consultor: str = ""
    percentual_exito: str = ""


class SignatariosV1(_FormSection):
    email_assinante_contrato: str = ""
    email_consultor_gebras: str = ""
    email_coordenador_gebras: str = ""
    email_diretor_gebras: str = ""
    email_financeiro_contratante: str = ""
    email_gestor_contratante: str = ""


class HubV1(_FormSection):
    observacoes_detalhes: str = ""


class AnexosV1(_FormSection):
    proposta_comercial_anexada: bool = False


class FormPayloadV1(_FormSection):
    schema_version: str = "v1"
    cliente: ClienteV1 = Field(default_factory=ClienteV1)
    servicos: ServicosV1 = Field(default_factory=ServicosV1)
    valores: ValoresV1 = Field(default_factory=ValoresV1)
    datas: DatasV1 = Field(default_factory=DatasV1)
    comercial: ComercialV1 = Field(default_factory=ComercialV1)
    signatarios: SignatariosV1 = Field(default_factory=SignatariosV1)
    hub: HubV1 = Field(default_factory=HubV1)
    anexos: AnexosV1 = Field(default_factory=AnexosV1)


# Chave legível do formulário → hash Pipedrive (custom_fields)
FORM_PATH_TO_PIPE: dict[str, str] = {
    "cliente.contratante": FIELD_NOME_CLIENTE,
    "cliente.documento": FIELD_DOCUMENTO,
    "cliente.endereco": FIELD_ENDERECO,
    "cliente.cep": FIELD_CEP,
    "cliente.municipio_estado": FIELD_CIDADE,
    "cliente.inscricao_estadual": FIELD_INSCRICAO_ESTADUAL,
    "cliente.inscricao_municipal": FIELD_INSCRICAO_MUNICIPAL,
    "cliente.notas": FIELD_NOTAS,
    "cliente.codigo_cliente_instalacao": FIELD_CODIGO_CLIENTE_INSTALACAO,
    "servicos.sole_web": FIELD_QTD_SOLE,
    "servicos.sole_consultoria": FIELD_QUALIDADE_ENERGIA,
    "servicos.gestao_acl": FIELD_GESTAO_ACL,
    "servicos.gestao_usina_fotovoltaica": FIELD_GESTAO_USINA_FOTOVOLTAICA,
    "servicos.gestao_qualidade_energia": FIELD_INDICADORES_QUALIDADE,
    "servicos.quantidade_ucs": FIELD_QUANTIDADE_UCS,
    "valores.valor_recorrencia": FIELD_VALOR_MENSAL,
    "valores.valor_implantacao": FIELD_VALOR_IMPLANTACAO,
    "datas.data_pagamento_implantacao": FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    "datas.data_primeira_cobranca": FIELD_DATA_PRIMEIRA_COBRANCA,
    "comercial.filial": FIELD_FILIAL,
    "comercial.regional": FIELD_REGIONAL,
    "comercial.consultor": FIELD_SUBCENTRO_NIVEL_3,
    "comercial.percentual_exito": FIELD_PERCENTUAL_EXITO,
    "signatarios.email_assinante_contrato": FIELD_CONTATO_PRINCIPAL,
    "signatarios.email_consultor_gebras": FIELD_EMAIL_CONSULTOR_GEBRAS,
    "signatarios.email_coordenador_gebras": FIELD_EMAIL_COORDENADOR_GEBRAS,
    "signatarios.email_diretor_gebras": FIELD_EMAIL_DIRETOR_GEBRAS,
    "signatarios.email_financeiro_contratante": FIELD_CONTATO_FINANCEIRO,
    "signatarios.email_gestor_contratante": FIELD_CONTATO_CONTRATANTE,
    "hub.observacoes_detalhes": FIELD_OBSERVACOES_DETALHES,
}

PIPE_TO_FORM_PATH: dict[str, str] = {v: k for k, v in FORM_PATH_TO_PIPE.items()}


def parse_form_payload_v1(payload: dict[str, Any]) -> FormPayloadV1:
    return FormPayloadV1.model_validate(payload or {})


def form_payload_to_deal_dict(deal_id: int, payload: FormPayloadV1) -> dict[str, Any]:
    """Converte payload v1 para dict deal (custom_fields legíveis — validação interna)."""
    cf: dict[str, Any] = {}
    for path, pipe_hash in FORM_PATH_TO_PIPE.items():
        section, _, field = path.partition(".")
        section_data = getattr(payload, section)
        value = getattr(section_data, field)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            cf[pipe_hash] = str(value)
        else:
            cf[pipe_hash] = str(value or "")
    return {"id": deal_id, "custom_fields": cf}
