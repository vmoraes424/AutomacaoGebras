"""
Catálogo dinâmico Plune: sincroniza subcentros via Browse e persiste no MySQL.

Novos valores (ex.: Regional 4) entram no banco na sincronização ou no primeiro uso.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests

from .config import PLUNE_AUTH_TOKEN, PLUNE_BASE_URL, PLUNE_COMPANY_ID
from .database import db_conn, upsert_subcentro

_SYNC_COOLDOWN_SEC = 300
_last_sync_at: datetime | None = None


def aliases_para_label(label: str, *, level: int = 2) -> list[str]:
    """Gera chaves de busca equivalentes (Regional 4 / Regional4 / etc.)."""
    texto = " ".join((label or "").split()).strip()
    if not texto:
        return []

    chaves: list[str] = []
    seen: set[str] = set()

    def add(valor: str) -> None:
        v = valor.strip()
        if v and v not in seen:
            seen.add(v)
            chaves.append(v)

    add(texto)
    compacto = texto.replace(" ", "")
    add(compacto)

    if level == 2:
        m = re.match(r"(?i)regional\s*(\d+)$", compacto)
        if m:
            num = m.group(1)
            add(f"Regional {num}")
            add(f"Regional{num}")
            add(f"Regional {num}".title())
        if texto.lower() == "sede":
            add("Sede")

    return chaves


def lookup_subcentro(branch_id: str, level: int, pipe_label: str) -> str | None:
    branch_id = str(branch_id)
    with db_conn() as conn:
        for chave in aliases_para_label(pipe_label, level=level):
            row = conn.execute(
                """
                SELECT plune_id FROM plune_subcentro
                WHERE branch_id = %s AND `level` = %s AND pipe_label = %s
                """,
                (branch_id, level, chave),
            ).fetchone()
            if row:
                return str(row["plune_id"])
    return None


def resolver_subcentro(
    branch_id: str, level: int, pipe_label: str, *, sync_if_missing: bool = True
) -> str | None:
    plune_id = lookup_subcentro(branch_id, level, pipe_label)
    if plune_id:
        return plune_id
    if sync_if_missing and PLUNE_AUTH_TOKEN:
        sincronizar_subcentros_de_pedidos()
        return lookup_subcentro(branch_id, level, pipe_label)
    return None


def _plune_get(class_id: str, method: str, params: list[tuple[str, str]]) -> dict:
    if not PLUNE_BASE_URL or not PLUNE_AUTH_TOKEN:
        raise RuntimeError("Plune não configurado (URL/token)")
    q = list(params) + [("_AuthToken", PLUNE_AUTH_TOKEN)]
    url = f"{PLUNE_BASE_URL.rstrip('/')}/JSON/{class_id}/{method}?" + urlencode(
        q, encoding="iso-8859-1"
    )
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    text = response.text.lstrip()
    if not text.startswith("{"):
        text = text[text.find("{") :]
    payload = json.loads(text)
    err = payload.get("ErrorStatus") or payload.get("ErrorStatus2")
    if err:
        raise RuntimeError(f"Plune ErrorStatus: {err}")
    return payload


def _cell(row: dict, name: str) -> tuple[str, str]:
    item = row.get(name) or {}
    if isinstance(item, dict):
        raw = str(item.get("value", "") or "").strip()
        rid = raw.split(".")[0] if raw else ""
        label = str(item.get("resolved", "") or "").strip()
        return rid, label
    return "", ""


def sincronizar_subcentros_de_pedidos(*, limit: int = 1000, force: bool = False) -> int:
    """
    Atualiza plune_subcentro a partir de pedidos recentes (campo resolved).
    Retorna quantidade de entradas gravadas/atualizadas.
    """
    global _last_sync_at
    agora = datetime.now(timezone.utc)
    if (
        not force
        and _last_sync_at
        and (agora - _last_sync_at).total_seconds() < _SYNC_COOLDOWN_SEC
    ):
        return 0

    browse_sequences = (
        "SubCentroCustoId,SubCentroCusto2Id,SubCentroCusto3Id,BranchId",
        "SubCentroCusto2Id,SubCentroCusto3Id,BranchId",
        "SubCentroCusto3Id,BranchId",
    )
    rows: list[dict] = []
    for seq in browse_sequences:
        params = [
            ("Venda.Pedido.Status", "5"),
            ("Venda.Pedido.Status.xBrowse", "1"),
            ("_Venda.Pedido.BrowseSequence", seq),
            ("_Venda.Pedido.BrowseLimit", str(limit)),
            ("_Venda.Pedido.Order", "Data"),
            ("_Venda.Pedido.OrderDesc", "1"),
        ]
        payload = _plune_get("Venda.Pedido", "Browse", params)
        batch = payload.get("data", {}).get("row", []) or []
        if isinstance(batch, dict):
            batch = [batch]
        rows.extend(batch)

    gravados = 0
    with db_conn() as conn:
        for row in rows:
            br_id, _ = _cell(row, "BranchId")
            if not br_id:
                continue
            s1_id, s1_name = _cell(row, "SubCentroCustoId")
            s2_id, s2_name = _cell(row, "SubCentroCusto2Id")
            s3_id, s3_name = _cell(row, "SubCentroCusto3Id")

            if s1_id and s1_name:
                for chave in aliases_para_label(s1_name, level=1):
                    upsert_subcentro(br_id, 1, chave, s1_id, s1_name, conn=conn)
                    gravados += 1

            if s2_id and s2_name:
                for chave in aliases_para_label(s2_name, level=2):
                    upsert_subcentro(br_id, 2, chave, s2_id, s2_name, conn=conn)
                    gravados += 1

            if s3_id and s3_name:
                for chave in aliases_para_label(s3_name, level=3):
                    upsert_subcentro(br_id, 3, chave, s3_id, s3_name, conn=conn)
                    gravados += 1

        conn.execute(
            """
            INSERT INTO app_meta (`key`, value) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value)
            """,
            ("plune_subcentro_last_sync", agora.isoformat()),
        )

    _last_sync_at = agora
    return gravados


def garantir_catalogo_inicializado() -> None:
    """Primeira execução: sincroniza subcentros se a tabela estiver vazia."""
    with db_conn() as conn:
        n = conn.execute("SELECT COUNT(*) AS c FROM plune_subcentro").fetchone()["c"]
    if n == 0 and PLUNE_AUTH_TOKEN:
        sincronizar_subcentros_de_pedidos(force=True)
