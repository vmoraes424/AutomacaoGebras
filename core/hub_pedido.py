"""
Pedido no SOLE HUB (MySQL gebras) — criação pós-assinatura e remoção via rm deal.

Espelha PedidoServices.Salvar no Gebras-Faturas (insert cabeçalho + filhos).
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterator

import pymysql

from .config import (
    HUB_CODIGO_USUARIO_SISTEMA,
    MYSQL_DATABASE_HUB,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)
from .database import (
    buscar_por_deal_id,
    marcar_hub_pedido_criado,
    obter_estado_hub_deal,
)
from .pipedrive_fields import (
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_PERCENTUAL_EXITO,
    FIELD_QTD_SOLE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_VALOR_MENSAL,
    buscar_deal_por_id,
    get_enum_label,
    get_numero_contrato,
    get_val,
)
from .plune_pedido import TIPO_PEDIDO_RECORRENTE, obter_numeros_pedidos_plune_deal

HUB_SITUACAO_NOVO = 0

# codigoServico no HUB (uc_Instalacao.cs)
_SERVICO_POR_CAMPO_PIPE: tuple[tuple[int, str], ...] = (
    (1, FIELD_QUALIDADE_ENERGIA),
    (2, FIELD_QTD_SOLE),
    (3, FIELD_GESTAO_USINA_FOTOVOLTAICA),
    (4, FIELD_GESTAO_ACL),
    (6, FIELD_INDICADORES_QUALIDADE),
)


class HubPedidoError(RuntimeError):
    pass


@contextmanager
def hub_conn() -> Iterator[pymysql.connections.Connection]:
    if not MYSQL_HOST or not MYSQL_USER:
        raise HubPedidoError(
            "MySQL não configurado (MYSQL_HOST / MYSQL_USER no .env)"
        )
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE_HUB,
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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


def _parse_data_pipe(valor: str) -> date | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(texto[:10], fmt).date()
        except ValueError:
            continue
    return None


def _bool_char(valor: bool) -> str:
    return "S" if valor else "N"


def _servicos_do_deal(deal: dict) -> list[int]:
    codigos: list[int] = []
    for codigo_servico, campo in _SERVICO_POR_CAMPO_PIPE:
        qtd = _decimal_pipe(get_val(deal, campo))
        if qtd is not None and qtd > 0:
            codigos.append(codigo_servico)
    return codigos


def _perc_economia_do_deal(deal: dict) -> tuple[bool, Decimal]:
    """
    Porcentagem de Êxito (Pipedrive) → temServicoPercNaEconomia / servicoPercNaEconomia no HUB.

    Mesmo campo do contrato (`percentual_exito`); ex.: enum "15%" grava 15,00 em decimal(4,2).
    """
    label = get_enum_label(deal, FIELD_PERCENTUAL_EXITO).strip()
    if not label:
        return False, Decimal("0")
    lower = label.lower()
    if lower.startswith("a definir") or lower in ("n/a", "-", "na"):
        return False, Decimal("0")
    match = re.search(r"(\d+(?:[.,]\d+)?)", label.replace(",", "."))
    if not match:
        return False, Decimal("0")
    try:
        valor = Decimal(match.group(1))
    except InvalidOperation:
        return False, Decimal("0")
    if valor <= 0:
        return False, Decimal("0")
    if valor > Decimal("99.99"):
        valor = Decimal("99.99")
    return True, valor.quantize(Decimal("0.01"))


def _parse_codigos_instalacao_p1(p1_raw: str) -> list[int]:
    """
    Código(s) da Instalação (P1): um ou vários separados por vírgula, ; ou espaço.
    Ex.: ``00665,01942`` → [665, 1942].
    """
    codigos: list[int] = []
    for parte in re.split(r"[,;\s]+", p1_raw.strip()):
        texto = parte.strip()
        if not texto:
            continue
        try:
            codigos.append(int(texto))
        except ValueError as exc:
            raise HubPedidoError(
                f"Código da Instalação inválido no Pipedrive: {texto!r}"
            ) from exc
    if not codigos:
        raise HubPedidoError("Código da Instalação (P1) vazio no Pipedrive.")
    vistos: set[int] = set()
    unicos: list[int] = []
    for codigo in codigos:
        if codigo not in vistos:
            vistos.add(codigo)
            unicos.append(codigo)
    return unicos


def _resolver_instalacao_hub(codigo_instalacao: int, codigo_cliente: int) -> dict:
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT Codigo, cod_cliente, Ref_Cliente, IDENTIFICACAO, NUC
                FROM instalacao
                WHERE Codigo = %s AND cod_cliente = %s
                LIMIT 1
                """,
                (codigo_instalacao, codigo_cliente),
            )
            row = cur.fetchone()
    if not row:
        raise HubPedidoError(
            f"Instalação HUB {codigo_instalacao} não encontrada para cliente {codigo_cliente} "
            "(confira Código da Instalação e Código Cliente no Pipedrive)."
        )
    cols = ("Codigo", "cod_cliente", "Ref_Cliente", "IDENTIFICACAO", "NUC")
    if isinstance(row, dict):
        data = row
    else:
        data = dict(zip(cols, row))
    return data


def _resolver_instalacoes_hub(
    codigos_instalacao: list[int], codigo_cliente: int
) -> list[dict]:
    return [
        _resolver_instalacao_hub(codigo, codigo_cliente)
        for codigo in codigos_instalacao
    ]


def _valor_por_instalacao(
    valor_total: Decimal, indice: int, total_instalacoes: int
) -> Decimal:
    """Reparte valor recorrência entre instalações (última absorve centavos)."""
    if total_instalacoes <= 1:
        return valor_total
    base = (valor_total / total_instalacoes).quantize(Decimal("0.01"))
    if indice < total_instalacoes - 1:
        return base
    ja_alocado = base * (total_instalacoes - 1)
    return (valor_total - ja_alocado).quantize(Decimal("0.01"))


def _id_plune_recorrente_para_hub(deal_id: str) -> int | None:
    """Somente pedido Plune recorrente em pedido_plune (não implantação)."""
    numeros = obter_numeros_pedidos_plune_deal(deal_id)
    raw = numeros.get(TIPO_PEDIDO_RECORRENTE)
    if not raw:
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def remover_pedido_hub(codigo_pedido: int) -> bool:
    """Remove pedido HUB e filhos (somente se existir). Retorna True se apagou cabeçalho."""
    codigo_pedido = int(codigo_pedido)
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM pedido_instalacao_extra WHERE codigoPedido = %s",
                (codigo_pedido,),
            )
            cur.execute(
                "DELETE FROM pedido_instalacao_servico WHERE codigoPedido = %s",
                (codigo_pedido,),
            )
            cur.execute(
                "DELETE FROM pedido_plune WHERE codigoPedido = %s",
                (codigo_pedido,),
            )
            cur.execute("DELETE FROM pedido WHERE codigo = %s", (codigo_pedido,))
            return cur.rowcount > 0


def remover_pedido_hub_por_deal(deal_id: str) -> dict[str, int]:
    """
    Usado por automacao_db rm deal: remove pedido HUB criado pela automação.
    Lê pedido_hub_id antes de limpar envelopes_pending (chamador deve ler antes ou
    esta função lê estado ainda existente).
    """
    estado = obter_estado_hub_deal(deal_id)
    if not estado or not estado.get("hub_pedido_criado"):
        return {"hub_pedido": 0}
    pedido_id = estado.get("pedido_hub_id")
    if not pedido_id:
        return {"hub_pedido": 0}
    if remover_pedido_hub(int(pedido_id)):
        return {"hub_pedido": 1}
    return {"hub_pedido": 0}


def criar_pedido_hub(
    deal_id: str, *, parceiro_plune_criado: bool | None = None
) -> dict[str, Any]:
    """
    Cria pedido no HUB se parceiro Plune já existia no ganho.

    parceiro_plune_criado: se informado, usa em vez de ler envelopes_pending
    (útil quando ainda não há envelope Clicksign, ex. DEV_PULAR_CLICKSIGN).
    """
    deal_id = str(deal_id).strip()
    if parceiro_plune_criado is None:
        registro = buscar_por_deal_id(deal_id)
        parceiro_novo = bool(registro and registro.get("parceiro_plune_criado"))
    else:
        registro = buscar_por_deal_id(deal_id)
        parceiro_novo = bool(parceiro_plune_criado)
    if parceiro_novo:
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "parceiro_novo_plune",
        }
    if registro and registro.get("hub_pedido_criado"):
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "hub_pedido_ja_criado",
            "pedido_hub_id": registro.get("pedido_hub_id"),
        }

    deal = buscar_deal_por_id(deal_id)
    if not deal:
        raise HubPedidoError(f"Deal {deal_id} não encontrado no Pipedrive")

    p1_raw = get_val(deal, FIELD_NUMERO_CONTRATO_P1).strip()
    p2_raw = get_val(deal, FIELD_NUMERO_CONTRATO_P2).strip()
    if not p1_raw or not p2_raw:
        raise HubPedidoError(
            f"Deal {deal_id}: Código da Instalação (P1) e Código Cliente (P2) obrigatórios no Pipedrive."
        )
    codigos_instalacao = _parse_codigos_instalacao_p1(p1_raw)
    try:
        codigo_cliente = int(p2_raw.split(",")[0].strip())
    except ValueError as exc:
        raise HubPedidoError(
            f"Deal {deal_id}: Código Cliente (P2) deve ser numérico."
        ) from exc

    servicos = _servicos_do_deal(deal)
    if not servicos:
        raise HubPedidoError(
            f"Deal {deal_id}: nenhum serviço com UC > 0 no Pipedrive para o pedido HUB."
        )

    instalacoes = _resolver_instalacoes_hub(codigos_instalacao, codigo_cliente)
    n_inst = len(instalacoes)
    valor_mensal = _decimal_pipe(get_val(deal, FIELD_VALOR_MENSAL)) or 0.0
    valor_decimal = Decimal(str(round(valor_mensal, 2)))

    hoje = date.today()
    data_comercial = _parse_data_pipe(get_val(deal, FIELD_DATA_PRIMEIRA_COBRANCA)) or hoje
    primeira_cobranca = data_comercial
    titulo = get_numero_contrato(deal)[:255]
    obs_pipe = get_val(deal, FIELD_OBSERVACOES_DETALHES).strip()
    obs = obs_pipe or f"Pedido automação Pipedrive deal {deal_id}"
    link = f"https://gebras.pipedrive.com/deal/{deal_id}"
    observacoes = f"{obs}\n\nPIPEDRIVE:\n{link}"
    if n_inst > 1:
        lista_inst = ", ".join(str(c) for c in codigos_instalacao)
        observacoes += (
            f"\n\nPedido com {n_inst} instalações (códigos HUB): {lista_inst}."
        )

    codigo_usuario = HUB_CODIGO_USUARIO_SISTEMA
    if codigo_usuario == 0:
        raise HubPedidoError(
            "HUB_CODIGO_USUARIO_SISTEMA não configurado no .env (use -3 para AUTOMACAO)."
        )

    codigo_plune_recorrente = _id_plune_recorrente_para_hub(deal_id)
    if codigo_plune_recorrente is None:
        raise HubPedidoError(
            f"Deal {deal_id}: pedido Plune recorrente não encontrado para vínculo pedido_plune."
        )

    agora = datetime.now()
    vigencia = 12
    renovar = _bool_char(True)
    tem_perc_economia, perc_economia = _perc_economia_do_deal(deal)

    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pedido (
                    data, codigoUsuario, descricao, observacoes, codigoSituacao,
                    dataComercial, inicioContrato, vigencia, renovarAutomaticamente,
                    primeiraCobranca, valorTotal
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    agora,
                    codigo_usuario,
                    titulo,
                    observacoes,
                    HUB_SITUACAO_NOVO,
                    data_comercial,
                    data_comercial,
                    vigencia,
                    renovar,
                    primeira_cobranca,
                    valor_decimal,
                ),
            )
            codigo_pedido = int(cur.lastrowid)

            for idx, inst in enumerate(instalacoes):
                codigo_instalacao = int(inst["Codigo"])
                valor_inst = _valor_por_instalacao(valor_decimal, idx, n_inst)
                cur.execute(
                    """
                    INSERT INTO pedido_instalacao_extra (
                        codigoPedido, codigoInstalacao, observacoes, valor,
                        temServicoPercNaEconomia, servicoPercNaEconomia
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        codigo_pedido,
                        codigo_instalacao,
                        "",
                        valor_inst,
                        _bool_char(tem_perc_economia),
                        perc_economia,
                    ),
                )
                for codigo_servico in servicos:
                    cur.execute(
                        """
                        INSERT INTO pedido_instalacao_servico (
                            codigoPedido, codigoInstalacao, codigoServico
                        ) VALUES (%s, %s, %s)
                        """,
                        (codigo_pedido, codigo_instalacao, codigo_servico),
                    )
            cur.execute(
                """
                INSERT INTO pedido_plune (codigoPedido, codigoPedidoPlune)
                VALUES (%s, %s)
                """,
                (codigo_pedido, codigo_plune_recorrente),
            )

    marcar_hub_pedido_criado(deal_id, codigo_pedido)
    return {
        "status": "created",
        "deal_id": deal_id,
        "pedido_hub_id": codigo_pedido,
        "codigo_cliente": codigo_cliente,
        "codigos_instalacao": codigos_instalacao,
        "servicos": servicos,
        "pedido_plune_recorrente": codigo_plune_recorrente,
    }


def tentar_criar_pedido_hub_deal(
    deal_id: str, *, parceiro_plune_criado: bool | None = None
) -> dict[str, Any] | None:
    """Wrapper com log; não propaga exceção (fluxo principal continua)."""
    deal_id = str(deal_id).strip()
    try:
        result = criar_pedido_hub(
            deal_id, parceiro_plune_criado=parceiro_plune_criado
        )
        log_resultado_hub(deal_id, result)
        return result
    except HubPedidoError as exc:
        print(f"[!] HUB: falha ao criar pedido (deal {deal_id}): {exc}", flush=True)
        return None
    except Exception as exc:
        print(f"[!] HUB: erro inesperado (deal {deal_id}): {exc}", flush=True)
        return None


def log_resultado_hub(deal_id: str, result: dict) -> None:
    status = result.get("status")
    if status == "created":
        print(
            f"[v] HUB: pedido criado — id={result.get('pedido_hub_id')} (deal {deal_id}).",
            flush=True,
        )
    elif status == "skipped":
        print(
            f"[*] HUB: ignorado para deal {deal_id} — {result.get('reason')}",
            flush=True,
        )
    else:
        print(f"[v] HUB: resultado {result}", flush=True)
