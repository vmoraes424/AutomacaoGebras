import re

import requests

from .config import (
    PIPEDRIVE_API_TOKEN,
    PLUNE_CENTRO_CUSTO_ID,
    PLUNE_REGIONAL_SUBCENTRO2_MAP,
    PLUNE_SUBCENTRO_CUSTO_ID,
)
from .pipedrive_fields import FIELD_DOCUMENTO, FIELD_REGIONAL, FIELD_VALOR_MENSAL, get_val


class DealValidationError(RuntimeError):
    def __init__(self, deal_id: str, mensagens: list[str]):
        self.deal_id = str(deal_id)
        self.mensagens = mensagens
        super().__init__("; ".join(mensagens))


def _decimal_pipe(valor) -> float | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    normalizado = texto.replace("R$", "").replace(" ", "")
    if "," in normalizado and "." in normalizado:
        if normalizado.rfind(",") > normalizado.rfind("."):
            normalizado = normalizado.replace(".", "").replace(",", ".")
        else:
            normalizado = normalizado.replace(",", "")
    elif "," in normalizado:
        normalizado = normalizado.replace(".", "").replace(",", ".")
    try:
        return float(normalizado)
    except ValueError:
        return None


def _valor_numero_maior_que_um(valor) -> bool:
    numero = _decimal_pipe(valor)
    return numero is not None and numero > 1


def _documento_valido(valor: str) -> bool:
    digits = re.sub(r"\D", "", valor or "")
    return len(digits) in (11, 14)


def validar_deal_para_automacao(deal: dict) -> None:
    deal_id = str(deal.get("id", ""))
    erros = []

    valor_mensal = get_val(deal, FIELD_VALOR_MENSAL)
    if not _valor_numero_maior_que_um(valor_mensal):
        erros.append(
            "Campo obrigatório inválido: Serviço / Valor (valor mensal). "
            f"Informe um número maior que 1. Valor recebido: {valor_mensal!r}."
        )

    documento = get_val(deal, FIELD_DOCUMENTO)
    if not _documento_valido(documento):
        erros.append(
            "Campo obrigatório inválido: CNPJ/CPF. "
            f"Informe um documento com 11 ou 14 dígitos. Valor recebido: {documento!r}."
        )

    regional = get_val(deal, FIELD_REGIONAL).strip()
    if not PLUNE_CENTRO_CUSTO_ID:
        erros.append(
            "Configuração Plune ausente: PLUNE_CENTRO_CUSTO_ID (Centro = Contratos Comerciais)."
        )
    if not PLUNE_SUBCENTRO_CUSTO_ID:
        erros.append(
            "Configuração Plune ausente: PLUNE_SUBCENTRO_CUSTO_ID "
            "(Sub Centro = Gestão de Energia)."
        )
    if not regional:
        erros.append(
            "Campo obrigatório inválido: REGIONAL. Informe a regional para preencher "
            "o Sub Centro Nível 2 no Plune."
        )
    elif regional not in PLUNE_REGIONAL_SUBCENTRO2_MAP:
        disponiveis = ", ".join(sorted(PLUNE_REGIONAL_SUBCENTRO2_MAP)) or "nenhum"
        erros.append(
            "REGIONAL sem mapeamento para SubCentroCusto2Id no Plune. "
            f"Valor recebido: {regional!r}. Configure PLUNE_REGIONAL_SUBCENTRO2_MAP. "
            f"Mapeados hoje: {disponiveis}."
        )

    if erros:
        raise DealValidationError(deal_id, erros)


def _pipedrive_headers() -> dict:
    return {"x-api-token": PIPEDRIVE_API_TOKEN}


def criar_nota_deal(deal_id: str, texto: str) -> None:
    payload = {"deal_id": int(deal_id), "content": texto}
    response = requests.post(
        "https://api.pipedrive.com/v1/notes",
        json=payload,
        headers=_pipedrive_headers(),
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive notes -> {response.status_code}: {response.text[:500]}"
        )


def reabrir_deal(deal_id: str) -> None:
    response = requests.put(
        f"https://api.pipedrive.com/v1/deals/{deal_id}",
        params={"api_token": PIPEDRIVE_API_TOKEN},
        json={"status": "open"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive reopen deal -> {response.status_code}: {response.text[:500]}"
        )
    data = response.json().get("data") or {}
    status = data.get("status")
    if status != "open":
        raise RuntimeError(
            f"Pipedrive reopen deal não confirmou status=open; status retornado={status!r}"
        )


def reabrir_deal_com_erros(deal_id: str, erros: list[str]) -> None:
    itens = "".join(f"<li>{erro}</li>" for erro in erros)
    nota = (
        "<p><strong>Automação Gebras:</strong> o card foi reaberto porque há "
        "campos obrigatórios inválidos para gerar contrato/pedidos no Plune.</p>"
        f"<ul>{itens}</ul>"
        "<p>Corrija os campos e marque o card como ganho novamente.</p>"
    )
    criar_nota_deal(deal_id, nota)
    reabrir_deal(deal_id)
