"""
Anexos de pedido Plune: proposta (Pipedrive) e contrato (Clicksign ou .docx local em dev).
"""

from __future__ import annotations

import glob
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from .config import (
    CLICKSIGN_ACCESS_TOKEN,
    CLICKSIGN_BASE_URL,
    DEV_PULAR_CLICKSIGN,
    PASTA_SAIDA,
    TESTE_PLUNE_SEM_ASSINATURA,
)
from .envelope_state import buscar_por_deal_id
from .pipedrive_files import baixar_pdf_proposta_deal
from .plune_anexo import inserir_anexo_pedido


def _mime_por_extensao(nome: str) -> str:
    ext = Path(nome).suffix.lower()
    if ext == ".pdf":
        return "application/pdf"
    if ext == ".docx":
        return (
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        )
    return "application/octet-stream"


def _contrato_docx_local(deal_id: str) -> tuple[bytes, str] | None:
    padrao = str(Path(PASTA_SAIDA) / f"Contrato_{deal_id}_*.docx")
    caminhos = sorted(glob.glob(padrao), key=lambda p: Path(p).stat().st_mtime, reverse=True)
    if not caminhos:
        return None
    caminho = Path(caminhos[0])
    return caminho.read_bytes(), caminho.name


def _contrato_clicksign_assinado(deal_id: str) -> tuple[bytes, str] | None:
    if not CLICKSIGN_BASE_URL or not CLICKSIGN_ACCESS_TOKEN:
        return None
    registro = buscar_por_deal_id(deal_id)
    if not registro:
        return None
    envelope_id = registro.get("envelope_id")
    if not envelope_id:
        return None
    from .automacao_contrato import ClicksignClient

    cliente = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)
    if cliente.get_envelope_status(envelope_id) != "closed":
        return None
    return cliente.baixar_pdf_assinado(envelope_id)


def obter_bytes_contrato(
    deal_id: str, *, permitir_docx_local: bool = False
) -> tuple[bytes, str, str] | None:
    """
    Retorna (bytes, nome_arquivo, content_type).
    Prioriza PDF assinado Clicksign; em dev pode usar .docx local.
    """
    assinado = _contrato_clicksign_assinado(deal_id)
    if assinado:
        conteudo, nome = assinado
        return conteudo, nome, _mime_por_extensao(nome)

    if permitir_docx_local:
        local = _contrato_docx_local(deal_id)
        if local:
            conteudo, nome = local
            return conteudo, nome, _mime_por_extensao(nome)
    return None


@dataclass
class CacheAnexosDeal:
    """Cache thread-safe dos bytes de proposta/contrato por deal (um download por arquivo)."""

    deal_id: str
    permitir_docx_local: bool = False
    _proposta: tuple[bytes, str] | None = field(default=None, init=False)
    _contrato: tuple[bytes, str, str] | None = field(default=None, init=False)
    _contrato_carregado: bool = field(default=False, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _prefetch_threads: list[threading.Thread] = field(default_factory=list, init=False)

    def prefetch(self, *, proposta: bool = True, contrato: bool = False) -> None:
        """Carrega proposta e/ou contrato em paralelo (bloqueante)."""
        self.iniciar_prefetch_assincrono(proposta=proposta, contrato=contrato)
        for thread in self._prefetch_threads:
            thread.join()

    def iniciar_prefetch_assincrono(
        self, *, proposta: bool = True, contrato: bool = False
    ) -> None:
        """
        Inicia download/leitura em background (não bloqueia).
        Os uploads chamam proposta()/contrato(), que aguardam se ainda estiver carregando.
        """
        threads: list[threading.Thread] = []
        if proposta:
            threads.append(
                threading.Thread(
                    target=self.proposta,
                    name=f"prefetch-proposta-{self.deal_id}",
                    daemon=True,
                )
            )
        if contrato:
            threads.append(
                threading.Thread(
                    target=self.contrato,
                    name=f"prefetch-contrato-{self.deal_id}",
                    daemon=True,
                )
            )
        for thread in threads:
            thread.start()
        self._prefetch_threads = threads

    def proposta(self) -> tuple[bytes, str] | None:
        if self._proposta is not None:
            return self._proposta
        dados = baixar_pdf_proposta_deal(self.deal_id)
        with self._lock:
            if self._proposta is None:
                self._proposta = dados
            return self._proposta

    def contrato(self, *, permitir_docx_local: bool | None = None) -> tuple[bytes, str, str] | None:
        if permitir_docx_local is None:
            permitir_docx_local = self.permitir_docx_local
        if self._contrato_carregado:
            return self._contrato
        dados = obter_bytes_contrato(
            self.deal_id, permitir_docx_local=permitir_docx_local
        )
        with self._lock:
            if not self._contrato_carregado:
                self._contrato = dados
                self._contrato_carregado = True
            return self._contrato


def anexar_proposta_pedido(
    deal_id: str,
    pedido_id: str,
    branch_id: str,
    *,
    cache: CacheAnexosDeal | None = None,
) -> dict | None:
    deal_id = str(deal_id).strip()
    try:
        pdf = cache.proposta() if cache else baixar_pdf_proposta_deal(deal_id)
        if not pdf:
            print(
                f"[*] Deal {deal_id}: sem PDF de proposta no Pipedrive "
                f"(pedido Plune {pedido_id}).",
                flush=True,
            )
            return None
        conteudo, nome = pdf
        resultado = inserir_anexo_pedido(
            pedido_id=pedido_id,
            branch_id=branch_id,
            nome_arquivo=nome,
            conteudo=conteudo,
            content_type="application/pdf",
        )
        print(
            f"[v] Deal {deal_id}: proposta «{nome}» anexada ao pedido Plune {pedido_id} "
            f"(anexo id {resultado.get('anexo_id') or '-'}).",
            flush=True,
        )
        return resultado
    except Exception as exc:
        print(
            f"[!] Deal {deal_id}: falha ao anexar proposta no pedido {pedido_id}: {exc}",
            flush=True,
        )
        return {"erro": str(exc)}


def anexar_contrato_pedido(
    deal_id: str,
    pedido_id: str,
    branch_id: str,
    *,
    permitir_docx_local: bool | None = None,
    cache: CacheAnexosDeal | None = None,
) -> dict | None:
    if permitir_docx_local is None:
        permitir_docx_local = bool(
            TESTE_PLUNE_SEM_ASSINATURA or DEV_PULAR_CLICKSIGN
        )
    deal_id = str(deal_id).strip()
    try:
        if cache:
            arquivo = cache.contrato(permitir_docx_local=permitir_docx_local)
        else:
            arquivo = obter_bytes_contrato(
                deal_id, permitir_docx_local=permitir_docx_local
            )
        if not arquivo:
            print(
                f"[*] Deal {deal_id}: contrato assinado indisponível "
                f"(pedido Plune {pedido_id}).",
                flush=True,
            )
            return None
        conteudo, nome, mime = arquivo
        resultado = inserir_anexo_pedido(
            pedido_id=pedido_id,
            branch_id=branch_id,
            nome_arquivo=nome,
            conteudo=conteudo,
            content_type=mime,
        )
        print(
            f"[v] Deal {deal_id}: contrato «{nome}» anexado ao pedido Plune {pedido_id} "
            f"(anexo id {resultado.get('anexo_id') or '-'}).",
            flush=True,
        )
        return resultado
    except Exception as exc:
        print(
            f"[!] Deal {deal_id}: falha ao anexar contrato no pedido {pedido_id}: {exc}",
            flush=True,
        )
        return {"erro": str(exc)}
