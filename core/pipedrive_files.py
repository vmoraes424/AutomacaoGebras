"""
Arquivos anexados a deals no Pipedrive (API v1 Files).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import requests

from .config import PIPEDRIVE_API_TOKEN


def _headers() -> dict[str, str]:
    return {"x-api-token": PIPEDRIVE_API_TOKEN}


def listar_arquivos_deal(deal_id: str) -> list[dict]:
    """Lista metadados de todos os arquivos do deal (com paginação)."""
    deal_id = str(deal_id).strip()
    if not deal_id:
        return []
    arquivos: list[dict] = []
    start = 0
    limit = 100
    while True:
        response = requests.get(
            f"https://api.pipedrive.com/v1/deals/{deal_id}/files",
            params={
                "api_token": PIPEDRIVE_API_TOKEN,
                "start": start,
                "limit": limit,
            },
            headers=_headers(),
            timeout=60,
        )
        if not response.ok:
            raise RuntimeError(
                f"Pipedrive files deal {deal_id} -> {response.status_code}: {response.text[:500]}"
            )
        body = response.json()
        data = body.get("data") or []
        if isinstance(data, dict):
            data = [data]
        arquivos.extend(data)
        pagination = (body.get("additional_data") or {}).get("pagination") or {}
        if not pagination.get("more_items_in_collection"):
            break
        next_start = pagination.get("next_start")
        if next_start is None:
            break
        start = int(next_start)
    return arquivos


def _eh_pdf(meta: dict) -> bool:
    tipo = str(meta.get("file_type") or "").lower()
    nome = str(meta.get("name") or "").lower()
    return tipo == "pdf" or nome.endswith(".pdf")


def _eh_docx(meta: dict) -> bool:
    tipo = str(meta.get("file_type") or "").lower()
    nome = str(meta.get("name") or "").lower()
    return tipo == "docx" or nome.endswith(".docx")


def _nome_base(meta: dict) -> str:
    nome = str(meta.get("name") or "").strip()
    if not nome:
        return ""
    return Path(nome).stem.strip().lower()


def _file_sort_key(meta: dict) -> tuple[str, str, int]:
    """
    Chave para «último enviado ao deal».
    add_time = anexo; update_time só desempata (não substitui upload mais recente).
    """
    add_t = str(meta.get("add_time") or "").strip()
    upd_t = str(meta.get("update_time") or "").strip()
    file_id = int(meta.get("id") or 0)
    return (add_t, upd_t, file_id)


def escolher_docx_contrato_padrao(arquivos: list[dict]) -> dict | None:
    """
    Seleciona template docx do deal pelo nome.
    Regra: basename (sem extensão) começa com 'contrato_padrao' (case-insensitive).
    Entre vários candidatos, usa o **último enviado** (add_time, depois id).
    """
    candidatos = [a for a in arquivos if _eh_docx(a)]
    if not candidatos:
        return None

    prefixo = "contrato_padrao"
    por_prefixo = [a for a in candidatos if _nome_base(a).startswith(prefixo)]
    if not por_prefixo:
        return None

    por_prefixo.sort(key=_file_sort_key, reverse=True)
    return por_prefixo[0]


def baixar_docx_contrato_padrao_deal(deal_id: str) -> tuple[bytes, str, int] | None:
    """
    Baixa o docx cujo nome começa com 'contrato_padrao' no deal.
    Retorna (bytes, nome, file_id).
    """
    arquivos = listar_arquivos_deal(deal_id)
    escolhido = escolher_docx_contrato_padrao(arquivos)
    if not escolhido:
        return None
    file_id = int(escolhido["id"])
    conteudo, nome, _ = baixar_arquivo_pipedrive(file_id)
    return conteudo, nome, file_id

def escolher_pdf_proposta(arquivos: list[dict]) -> dict | None:
    """Prioriza PDF com 'proposta' no nome; senão o primeiro PDF do deal."""
    pdfs = [a for a in arquivos if _eh_pdf(a)]
    if not pdfs:
        return None
    for arquivo in pdfs:
        nome = str(arquivo.get("name") or "").lower()
        if "proposta" in nome:
            return arquivo
    return pdfs[0]


def baixar_arquivo_pipedrive(file_id: str | int) -> tuple[bytes, str, str]:
    """
    Baixa o binário do arquivo.
    Retorna (conteúdo, nome_arquivo, content_type).
    """
    meta_resp = requests.get(
        f"https://api.pipedrive.com/v1/files/{file_id}",
        params={"api_token": PIPEDRIVE_API_TOKEN},
        headers=_headers(),
        timeout=60,
    )
    if not meta_resp.ok:
        raise RuntimeError(
            f"Pipedrive file meta {file_id} -> {meta_resp.status_code}: {meta_resp.text[:300]}"
        )
    meta = meta_resp.json().get("data") or {}
    nome = str(meta.get("name") or f"arquivo_{file_id}.pdf")
    url = meta.get("url")
    if not url:
        raise RuntimeError(f"Pipedrive file {file_id} sem URL de download")

    download_params = {}
    if "pipedrive.com" in url and "api_token=" not in url:
        download_params["api_token"] = PIPEDRIVE_API_TOKEN
    bin_resp = requests.get(
        url, params=download_params, headers=_headers(), timeout=120
    )
    if not bin_resp.ok:
        raise RuntimeError(
            f"Pipedrive download {file_id} -> {bin_resp.status_code}: {bin_resp.text[:200]}"
        )
    content_type = (
        bin_resp.headers.get("Content-Type")
        or meta.get("file_type")
        or "application/octet-stream"
    )
    return bin_resp.content, nome, content_type


def baixar_pdf_proposta_deal(deal_id: str) -> tuple[bytes, str] | None:
    """Baixa o PDF de proposta comercial do deal, se existir."""
    arquivos = listar_arquivos_deal(deal_id)
    escolhido = escolher_pdf_proposta(arquivos)
    if not escolhido:
        return None
    conteudo, nome, _ = baixar_arquivo_pipedrive(escolhido["id"])
    return conteudo, nome
