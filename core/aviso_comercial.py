"""Aviso informativo ao comercial (etapa 1) — não é signatário Clicksign."""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)
from .gebras_defaults import EMAIL_COMERCIAL_AUTOMACAO
from .pipedrive_fields import (
    FIELD_DOCUMENTO,
    FIELD_QUANTIDADE_UCS,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
    formatar_data_ptbr,
    get_filial_label,
    get_nome_cliente,
    get_numero_contrato,
    get_val,
)
from .plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    formatar_linha_pedidos_plune_contrato,
)


def _formatar_moeda(valor) -> str:
    try:
        texto = str(valor or "").replace("R$", "").replace(" ", "")
        if "," in texto and "." in texto:
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        val = float(texto)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(valor or "—")


def _linha_pedido_plune(numeros: dict[str, str], tipo: str, rotulo: str) -> str:
    numero = (numeros.get(tipo) or "").strip()
    if numero:
        return f"{rotulo}: {numero}"
    return f"{rotulo}: (não gerado)"


def montar_aviso_comercial(
    deal: dict, numeros_pedidos: dict[str, str] | None = None
) -> tuple[str, str, str]:
    """Retorna (assunto, corpo_texto, corpo_html)."""
    deal_id = str(deal.get("id", "")).strip()
    titulo = str(deal.get("title") or "—").strip()
    nome = get_nome_cliente(deal) or titulo
    numeros = numeros_pedidos or {}
    resumo_plune = formatar_linha_pedidos_plune_contrato(numeros) or "—"
    linha_impl = _linha_pedido_plune(numeros, TIPO_PEDIDO_IMPLANTACAO, "Implantação")
    linha_rec = _linha_pedido_plune(numeros, TIPO_PEDIDO_RECORRENTE, "Recorrente")
    pipe_url = f"https://gebras.pipedrive.com/deal/{deal_id}" if deal_id else "—"

    assunto = f"[Automação Gebras] Deal #{deal_id} — {nome}"

    corpo_texto = f"""Olá, equipe Comercial,

A automação Gebras iniciou o fluxo pós-venda para o deal abaixo.

PEDIDOS PLUNE
{linha_impl}
{linha_rec}
Resumo: {resumo_plune}

DADOS DO NEGÓCIO
Deal: #{deal_id} — {titulo}
Cliente: {nome}
CNPJ/CPF: {get_val(deal, FIELD_DOCUMENTO) or "—"}
Filial: {get_filial_label(deal) or "—"}
Valor recorrência: {_formatar_moeda(get_val(deal, FIELD_VALOR_MENSAL))}
Valor implantação: {_formatar_moeda(get_val(deal, FIELD_VALOR_IMPLANTACAO))}
Quantidade de UC's: {get_val(deal, FIELD_QUANTIDADE_UCS) or "—"}
Nº contrato: {get_numero_contrato(deal)}
Data do ganho: {formatar_data_ptbr(deal.get("won_time") or deal.get("add_time"))}

Pipedrive: {pipe_url}

PRÓXIMOS PASSOS
1. Contrato enviado ao Clicksign (etapa 1: Consultor assina; este e-mail é apenas informativo).
2. Sequência de assinatura: Consultor → Coordenador → Cliente → Diretor.
3. Após assinatura: aprovação dos pedidos Plune e, se aplicável, pedido no HUB.

Automação Gebras
"""

    corpo_html = f"""<p>Olá, equipe Comercial,</p>
<p>A <strong>automação Gebras</strong> iniciou o fluxo pós-venda para o deal abaixo.</p>
<h3>Pedidos Plune</h3>
<ul>
<li>{linha_impl}</li>
<li>{linha_rec}</li>
</ul>
<p><strong>Resumo:</strong> {resumo_plune}</p>
<h3>Dados do negócio</h3>
<table border="1" cellpadding="6" cellspacing="0">
<tr><td><strong>Deal</strong></td><td>#{deal_id} — {titulo}</td></tr>
<tr><td><strong>Cliente</strong></td><td>{nome}</td></tr>
<tr><td><strong>CNPJ/CPF</strong></td><td>{get_val(deal, FIELD_DOCUMENTO) or "—"}</td></tr>
<tr><td><strong>Filial</strong></td><td>{get_filial_label(deal) or "—"}</td></tr>
<tr><td><strong>Valor recorrência</strong></td><td>{_formatar_moeda(get_val(deal, FIELD_VALOR_MENSAL))}</td></tr>
<tr><td><strong>Valor implantação</strong></td><td>{_formatar_moeda(get_val(deal, FIELD_VALOR_IMPLANTACAO))}</td></tr>
<tr><td><strong>Quantidade de UC's</strong></td><td>{get_val(deal, FIELD_QUANTIDADE_UCS) or "—"}</td></tr>
<tr><td><strong>Nº contrato</strong></td><td>{get_numero_contrato(deal)}</td></tr>
<tr><td><strong>Data do ganho</strong></td><td>{formatar_data_ptbr(deal.get("won_time") or deal.get("add_time"))}</td></tr>
</table>
<p><a href="{pipe_url}">Abrir deal no Pipedrive</a></p>
<h3>Próximos passos</h3>
<ol>
<li>Contrato no Clicksign — <strong>etapa 1: Consultor</strong> (este e-mail é só informativo; vocês não assinam).</li>
<li>Ordem: Consultor → Coordenador → Cliente → Diretor.</li>
<li>Após assinatura: aprovação Plune e HUB (se aplicável).</li>
</ol>
<p>Automação Gebras</p>"""

    return assunto, corpo_texto, corpo_html


def _smtp_configurado() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def enviar_aviso_comercial_etapa1(
    deal: dict, numeros_pedidos: dict[str, str] | None = None
) -> bool:
    """
    Envia e-mail informativo para comercial@gebras.com (etapa 1, sem assinatura).
    Retorna True se enviou; False se SMTP ausente ou falha (log no stdout).
    """
    destino = EMAIL_COMERCIAL_AUTOMACAO
    assunto, texto, html = montar_aviso_comercial(deal, numeros_pedidos)
    deal_id = str(deal.get("id", "")).strip()

    if not _smtp_configurado():
        print(
            f"[*] Deal {deal_id}: aviso comercial (informativo) — SMTP não configurado "
            f"no .env; e-mail não enviado para {destino!r}.",
            flush=True,
        )
        print(f"    Assunto: {assunto}", flush=True)
        print(f"    Plune: {formatar_linha_pedidos_plune_contrato(numeros_pedidos or {})}", flush=True)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = SMTP_FROM or SMTP_USER
    msg["To"] = destino
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(msg["From"], [destino], msg.as_string())
        print(
            f"[v] Deal {deal_id}: aviso informativo enviado para {destino} (etapa 1).",
            flush=True,
        )
        return True
    except Exception as exc:
        print(
            f"[!] Deal {deal_id}: falha ao enviar aviso comercial para {destino}: {exc}",
            flush=True,
        )
        return False
