"""Etapas do funil Pipedrive (portal lista Contrato; worker dispara via formulário web)."""

from __future__ import annotations

import unicodedata
from typing import Any

import requests

from core.config import PIPEDRIVE_API_TOKEN
from core.gebras_defaults import (
    PIPEDRIVE_STAGE_CONTRATO_NOME,
    PIPEDRIVE_STAGE_NEGOCIACAO_NOME,
)

_stages_por_pipeline: dict[str, dict[str, int]] = {}
_contrato_stage_ids_cache: list[int] | None = None

PIPEDRIVE_V2_BASE = "https://api.pipedrive.com/api/v2"


def _normalizar_nome_etapa(nome: str) -> str:
    s = (nome or "").strip().casefold()
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _headers() -> dict[str, str]:
    from core import config

    return {"x-api-token": config.PIPEDRIVE_API_TOKEN}


def limpar_cache_stages() -> None:
    """Limpa cache de etapas (útil em testes)."""
    global _contrato_stage_ids_cache
    _stages_por_pipeline.clear()
    _contrato_stage_ids_cache = None


def list_stage_ids_etapa_contrato() -> list[int]:
    """
    stage_id da etapa Contrato em cada pipeline do Pipedrive.
    Uma única chamada GET /stages (evita N+1 por pipeline).
    """
    global _contrato_stage_ids_cache
    if _contrato_stage_ids_cache is not None:
        return list(_contrato_stage_ids_cache)

    chave = _normalizar_nome_etapa(PIPEDRIVE_STAGE_CONTRATO_NOME)
    response = requests.get(
        f"{PIPEDRIVE_V2_BASE}/stages",
        headers=_headers(),
        params={"limit": 500},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive stages -> {response.status_code}: {response.text[:500]}"
        )

    stage_ids: list[int] = []
    for stage in response.json().get("data") or []:
        sid = stage.get("id")
        if sid is None:
            continue
        if _normalizar_nome_etapa(stage.get("name") or "") == chave:
            stage_ids.append(int(sid))

    _contrato_stage_ids_cache = stage_ids
    return list(stage_ids)


def _carregar_stages_pipeline(pipeline_id: str) -> None:
    response = requests.get(
        "https://api.pipedrive.com/api/v2/stages",
        headers=_headers(),
        params={"pipeline_id": pipeline_id, "limit": 500},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive stages -> {response.status_code}: {response.text[:500]}"
        )
    mapping: dict[str, int] = {}
    for stage in response.json().get("data") or []:
        name = stage.get("name") or ""
        sid = stage.get("id")
        if sid is not None:
            mapping[_normalizar_nome_etapa(name)] = int(sid)
    _stages_por_pipeline[pipeline_id] = mapping


def stage_id_por_nome(pipeline_id: str | int, nome_etapa: str) -> int:
    """Retorna o stage_id da etapa informada no pipeline."""
    pid = str(pipeline_id)
    if pid not in _stages_por_pipeline:
        _carregar_stages_pipeline(pid)
    chave = _normalizar_nome_etapa(nome_etapa)
    stage_id = _stages_por_pipeline.get(pid, {}).get(chave)
    if stage_id is None:
        raise RuntimeError(
            f"Pipedrive: etapa {nome_etapa!r} não encontrada no pipeline {pipeline_id}."
        )
    return stage_id


def stage_id_negociacao(pipeline_id: str | int) -> int:
    return stage_id_por_nome(pipeline_id, PIPEDRIVE_STAGE_NEGOCIACAO_NOME)


def stage_id_contrato(pipeline_id: str | int) -> int:
    return stage_id_por_nome(pipeline_id, PIPEDRIVE_STAGE_CONTRATO_NOME)


def deal_esta_em_negociacao(deal: dict[str, Any]) -> bool:
    pipeline_id = deal.get("pipeline_id")
    stage_id_atual = deal.get("stage_id")
    if pipeline_id is None or stage_id_atual is None:
        return False
    return int(stage_id_atual) == stage_id_negociacao(pipeline_id)


def deal_esta_em_etapa_contrato(deal: dict[str, Any]) -> bool:
    pipeline_id = deal.get("pipeline_id")
    stage_id_atual = deal.get("stage_id")
    if pipeline_id is None or stage_id_atual is None:
        return False
    try:
        return int(stage_id_atual) == stage_id_contrato(pipeline_id)
    except RuntimeError:
        return False


def deal_elegivel_formulario_contrato(deal: dict[str, Any]) -> bool:
    """Card aberto na etapa Contrato (listagem portal + submit + worker)."""
    return deal.get("status") == "open" and deal_esta_em_etapa_contrato(deal)


def _buscar_deal_v2(deal_id: str) -> dict[str, Any]:
    response = requests.get(
        f"https://api.pipedrive.com/api/v2/deals/{deal_id}",
        headers=_headers(),
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive GET deal -> {response.status_code}: {response.text[:500]}"
        )
    data = response.json().get("data")
    if not data:
        raise RuntimeError(f"Pipedrive GET deal {deal_id}: resposta sem data.")
    return data


def _mover_deal_para_stage(deal_id: str, stage_id: int) -> None:
    response = requests.patch(
        f"https://api.pipedrive.com/api/v2/deals/{deal_id}",
        headers=_headers(),
        json={"stage_id": stage_id},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive PATCH deal stage -> {response.status_code}: {response.text[:500]}"
        )


def _garantir_deal_em_etapa(deal: dict[str, Any], nome_etapa: str) -> bool:
    """
    Garante que o deal está na etapa informada do seu pipeline.

    Retorna True se o deal foi movido; False se já estava na etapa correta.
    Atualiza deal['stage_id'] em memória após mover.
    """
    deal_id = str(deal.get("id") or "")
    if not deal_id:
        raise RuntimeError(f"Deal sem id para verificar etapa {nome_etapa!r}.")

    pipeline_id = deal.get("pipeline_id")
    stage_id_atual = deal.get("stage_id")
    if pipeline_id is None or stage_id_atual is None:
        deal_v2 = _buscar_deal_v2(deal_id)
        pipeline_id = deal_v2.get("pipeline_id")
        stage_id_atual = deal_v2.get("stage_id")
        if pipeline_id is not None:
            deal["pipeline_id"] = pipeline_id
        if stage_id_atual is not None:
            deal["stage_id"] = stage_id_atual

    if pipeline_id is None:
        raise RuntimeError(
            f"Pipedrive deal {deal_id}: pipeline_id ausente; não é possível "
            f"resolver etapa {nome_etapa!r}."
        )

    destino = stage_id_por_nome(pipeline_id, nome_etapa)
    if int(stage_id_atual or 0) == destino:
        return False

    _mover_deal_para_stage(deal_id, destino)
    deal["stage_id"] = destino
    return True


def garantir_deal_em_etapa_negociacao(deal: dict[str, Any]) -> bool:
    """Garante etapa Negociação (ex.: reverter após falha de validação)."""
    return _garantir_deal_em_etapa(deal, PIPEDRIVE_STAGE_NEGOCIACAO_NOME)


def garantir_deal_em_etapa_contrato(deal: dict[str, Any]) -> bool:
    """Garante etapa Contrato (ex.: card visível no portal antes do envio do formulário)."""
    return _garantir_deal_em_etapa(deal, PIPEDRIVE_STAGE_CONTRATO_NOME)


def buscar_deals_etapa_contrato() -> list[dict[str, Any]]:
    """Lista deals abertos na etapa Contrato (portal/scripts; worker não usa mais este gatilho)."""
    deals: list[dict[str, Any]] = []
    cursor: str | None = None
    try:
        while True:
            params: dict[str, str | int] = {"status": "open", "limit": 500}
            if cursor:
                params["cursor"] = cursor
            response = requests.get(
                "https://api.pipedrive.com/api/v2/deals",
                headers=_headers(),
                params=params,
                timeout=60,
            )
            if response.status_code != 200:
                print(
                    f"[!] Erro ao buscar deals: {response.status_code} - {response.text}"
                )
                return deals
            body = response.json()
            page = body.get("data") or []
            if isinstance(page, dict):
                page = [page]
            for deal in page:
                if deal_esta_em_etapa_contrato(deal):
                    deals.append(deal)
            cursor = (body.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break
        return deals
    except Exception as e:
        print(f"[!] Falha na conexão com Pipedrive: {e}")
        return deals


def reverter_deal_para_negociacao(deal_id: str) -> bool:
    """Move o deal para Negociação (evita reprocessar enquanto corrige o card)."""
    deal = _buscar_deal_v2(deal_id)
    return garantir_deal_em_etapa_negociacao(deal)


def marcar_deal_como_ganho(deal_id: str) -> None:
    """Marca o deal como ganho após todas as assinaturas Clicksign."""
    response = requests.patch(
        f"https://api.pipedrive.com/api/v2/deals/{deal_id}",
        headers=_headers(),
        json={"status": "won"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Pipedrive PATCH deal won -> {response.status_code}: {response.text[:500]}"
        )
    data = response.json().get("data") or {}
    if data.get("status") != "won":
        raise RuntimeError(
            f"Pipedrive não confirmou status=won para deal {deal_id}; "
            f"status retornado={data.get('status')!r}"
        )
