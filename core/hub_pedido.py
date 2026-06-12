"""
Pedido no SOLE HUB (MySQL gebras) — criação pós-assinatura e remoção via rm deal.

Espelha PedidoServices.Salvar no Gebras-Faturas (insert cabeçalho + filhos).
"""

from __future__ import annotations

import re
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from typing import Any, Iterator

import pymysql

from .automacao_config import get_automacao_config
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
    CAMPOS_CONTRATO_OPCIONAIS,
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_PERCENTUAL_EXITO,
    buscar_deal_por_id,
    get_enum_label,
    get_numero_contrato,
    get_val,
    parse_codigo_cliente_instalacao,
)
from .plune_pedido import TIPO_PEDIDO_RECORRENTE, obter_numeros_pedidos_plune_deal

HUB_SITUACAO_NOVO = 0

# Formato obrigatório em Observações (Detalhes) para criar pedido no HUB.
FORMATO_OBSERVACOES_HUB = (
    "UC = <IDENTIFICACAO> - <serviço> + <serviço> = <valor BR>; UC = ..."
)
EXEMPLO_OBSERVACOES_HUB = (
    "UC = 00665 - SOLE WEB + Gestão ACL - Mercado Livre de Energia = 1.500,92; "
    "UC = 01942 - ACL + Sole Consultoria = 454.564,00"
)

# Valor: ponto milhar + vírgula decimal, sempre 2 casas (ex.: 1.500,92 ou 500,00).
_RE_VALOR_MONETARIO_BR = re.compile(
    r"^(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}$"
)
_RE_BLOCO_UC_OBS = re.compile(
    r"^UC\s*=\s*(?P<identificacao>\S+)\s*-\s*(?P<servicos>.+?)\s*=\s*(?P<valor>"
    r"(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})\s*$",
    re.IGNORECASE,
)
_RE_MARCADOR_UC_OBS = re.compile(r"UC\s*=", re.IGNORECASE)
_RE_UC_SEPARADOR_VIRGULA = re.compile(r",\s*UC\s*=", re.IGNORECASE)

# Aliases do Pipedrive → codigoServico (pedido_nome_servico); chave já normalizada.
_ALIASES_SERVICO_PIPE: dict[str, int] = {
    "sole web": 2,
    "sole web com telemetria": 2,
    "sw": 2,
    "sole consultoria": 1,
    "sc": 1,
    "gestao mercado livre": 4,
    "gestão mercado livre": 4,
    "gestao acl": 4,
    "gestão acl": 4,
    "gestao acl - mercado livre de energia": 4,
    "gestão acl - mercado livre de energia": 4,
    "mercado livre de energia": 4,
    "acl": 4,
    "gml": 4,
    "gestao de usina fotovoltaica": 3,
    "gestão de usina fotovoltaica": 3,
    "guf": 3,
    "gestao de qualidade de energia": 6,
    "gestão de qualidade de energia": 6,
    "gqe": 6,
    "direito de energia com comissao de sucesso": 5,
    "direito de energia com comissão de sucesso": 5,
    "decs": 5,
}

# Tokens curtos/ambíguos que não podem ser resolvidos sozinhos (ex.: "SOLE" → SW e SC).
_TOKENS_SERVICO_PROIBIDOS: frozenset[str] = frozenset({"sole", "gestao", "gestão"})


@dataclass(frozen=True)
class InstalacaoObsHub:
    identificacao: str
    codigo_instalacao: int
    servicos: tuple[int, ...]
    valor: Decimal


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


def _normalizar_texto_hub(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto or "")
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", sem_acento.strip().lower())


@dataclass(frozen=True)
class _ServicoCatalogoHub:
    codigo: int
    nome: str
    nome_norm: str
    descricao_norm: str
    sigla_norm: str


@lru_cache(maxsize=1)
def _catalogo_servicos_hub() -> tuple[_ServicoCatalogoHub, ...]:
    """Nomes oficiais em pedido_nome_servico (MYSQL_DATABASE_HUB)."""
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT codigo, nome, descricao, sigla
                FROM pedido_nome_servico
                WHERE codigo > 0
                ORDER BY codigo
                """
            )
            rows = cur.fetchall()
    catalogo: list[_ServicoCatalogoHub] = []
    for row in rows:
        if isinstance(row, dict):
            codigo = int(row["codigo"])
            nome = str(row["nome"] or "")
            descricao = str(row.get("descricao") or nome)
            sigla = str(row.get("sigla") or "")
        else:
            codigo, nome, descricao, sigla = row
            codigo = int(codigo)
            nome = str(nome or "")
            descricao = str(descricao or nome)
            sigla = str(sigla or "")
        catalogo.append(
            _ServicoCatalogoHub(
                codigo=codigo,
                nome=nome,
                nome_norm=_normalizar_texto_hub(nome),
                descricao_norm=_normalizar_texto_hub(descricao),
                sigla_norm=_normalizar_texto_hub(sigla),
            )
        )
    return tuple(catalogo)


def _resolver_token_servico_hub(token: str) -> int:
    """Resolve rótulo do Pipe para codigoServico com alta confiança (sem match parcial fraco)."""
    bruto = token.strip()
    if not bruto:
        raise HubPedidoError("Trecho de serviço vazio em Observações (Detalhes).")
    norm = _normalizar_texto_hub(bruto)
    if norm in _TOKENS_SERVICO_PROIBIDOS:
        raise HubPedidoError(
            f"Serviço ambíguo em Observações: {bruto!r}. "
            "Use o nome completo (ex.: «SOLE Web (com telemetria)» ou «SOLE Consultoria»), "
            "não apenas «SOLE»."
        )
    if norm in _ALIASES_SERVICO_PIPE:
        return _ALIASES_SERVICO_PIPE[norm]

    catalogo = _catalogo_servicos_hub()
    for item in catalogo:
        if norm == item.nome_norm or norm == item.descricao_norm:
            return item.codigo
        if item.sigla_norm and norm == item.sigla_norm:
            return item.codigo

    candidatos: list[tuple[int, int, int]] = []
    for item in catalogo:
        if len(norm) >= 4 and norm in item.nome_norm:
            candidatos.append((len(item.nome_norm), len(norm), item.codigo))
        elif len(item.nome_norm) >= 4 and item.nome_norm in norm:
            candidatos.append((len(norm), len(item.nome_norm), item.codigo))
    if candidatos:
        candidatos.sort(reverse=True)
        melhor = candidatos[0]
        if len(candidatos) == 1 or candidatos[1][0] < melhor[0]:
            return melhor[2]
        raise HubPedidoError(
            f"Serviço ambíguo em Observações: {bruto!r} "
            f"(candidatos HUB: {candidatos[0][2]}, {candidatos[1][2]}). "
            "Use o nome completo como no cadastro do HUB."
        )

    raise HubPedidoError(
        f"Serviço não reconhecido em Observações: {bruto!r}. "
        "Confira o texto em «Observações (Detalhes)» e os nomes em pedido_nome_servico."
    )


def _mensagem_formato_observacoes_hub(deal_id: str, motivo: str) -> str:
    return (
        f"Deal {deal_id}: Observações (Detalhes) é obrigatório no formato "
        f"«{FORMATO_OBSERVACOES_HUB}» ({motivo}). "
        f"Valor em real brasileiro (ex.: 1.500,92). Separe UCs com «;». "
        f"Exemplo: {EXEMPLO_OBSERVACOES_HUB}"
    )


def _segmentos_observacoes_hub(texto: str) -> list[str]:
    return [p.strip() for p in texto.split(";") if p.strip()]


def _parse_valor_monetario_hub(valor_bruto: str, *, identificacao_uc: str) -> Decimal:
    valor_bruto = valor_bruto.strip()
    if not _RE_VALOR_MONETARIO_BR.fullmatch(valor_bruto):
        raise HubPedidoError(
            f"Valor inválido para UC {identificacao_uc!r} em Observações: {valor_bruto!r}. "
            "Use formato brasileiro com vírgula decimal e ponto de milhar "
            "(ex.: 1.500,92 ou 500,00)."
        )
    normalizado = valor_bruto.replace(".", "").replace(",", ".")
    return Decimal(normalizado).quantize(Decimal("0.01"))


def validar_observacoes_hub_obrigatorias(
    deal_id: str,
    obs_pipe: str,
    codigos_instalacao: list[int],
    codigo_cliente: int,
) -> list[InstalacaoObsHub]:
    """
    Valida e interpreta Observações (Detalhes). Sem formato correto → HubPedidoError.

    Instalações (CODIGO) vêm só de Código Cliente/Código da Instalação (ex.: 352/1234,3456).
    Observações definem serviços e valor por bloco «UC =»; a quantidade de blocos deve
    coincidir com a quantidade de instalações no campo combinado.
    """
    deal_id = str(deal_id).strip()
    texto = (obs_pipe or "").strip()
    if not texto:
        raise HubPedidoError(_mensagem_formato_observacoes_hub(deal_id, "campo vazio"))
    if not _RE_MARCADOR_UC_OBS.search(texto):
        raise HubPedidoError(_mensagem_formato_observacoes_hub(deal_id, "falta «UC =»"))
    if _RE_UC_SEPARADOR_VIRGULA.search(texto):
        raise HubPedidoError(
            _mensagem_formato_observacoes_hub(
                deal_id,
                "separe cada UC com «;», não com vírgula entre blocos",
            )
        )

    segmentos = _segmentos_observacoes_hub(texto)
    blocos = _parse_blocos_observacoes_hub(texto)
    if not blocos:
        raise HubPedidoError(
            _mensagem_formato_observacoes_hub(
                deal_id,
                "nenhum bloco válido (use «-», «+», «=» e valor tipo 1.500,92)",
            )
        )
    if len(blocos) != len(segmentos):
        raise HubPedidoError(
            f"Deal {deal_id}: há {len(segmentos)} bloco(s) separados por «;», mas apenas "
            f"{len(blocos)} no formato completo «{FORMATO_OBSERVACOES_HUB}». "
            "Revise «+», o valor (ex.: 1.500,92) e o separador «;» entre UCs."
        )
    if len(blocos) != len(codigos_instalacao):
        raise HubPedidoError(
            f"Deal {deal_id}: Código Cliente/Código da Instalação tem "
            f"{len(codigos_instalacao)} instalação(ões) {codigos_instalacao}, "
            f"mas Observações (Detalhes) tem {len(blocos)} bloco(s) «UC =». "
            "Informe um bloco por instalação, na mesma ordem."
        )

    linhas = _resolver_linhas_observacoes_hub(texto, codigos_instalacao)
    return linhas


def erros_validacao_observacoes_hub(deal: dict) -> list[str]:
    """Mensagens para DealValidationError (validação no ganho do deal)."""
    deal_id = str(deal.get("id", ""))
    codigo_cliente_raw = get_val(deal, FIELD_CODIGO_CLIENTE_INSTALACAO).strip()
    if not codigo_cliente_raw:
        return []
    try:
        codigos_p1, codigo_cliente = _p1_p2_do_deal(deal)
    except HubPedidoError as exc:
        return [str(exc)]
    obs_pipe = get_val(deal, FIELD_OBSERVACOES_DETALHES).strip()
    if not obs_pipe and FIELD_OBSERVACOES_DETALHES in CAMPOS_CONTRATO_OPCIONAIS:
        return []
    try:
        validar_observacoes_hub_obrigatorias(
            deal_id, obs_pipe, codigos_p1, codigo_cliente
        )
    except HubPedidoError as exc:
        return [str(exc)]
    return []


def _parse_blocos_observacoes_hub(texto: str) -> list[tuple[str, tuple[int, ...], Decimal]]:
    """
    Extrai IDENTIFICACAO (UC), serviços e valor do texto de Observações.

    Formato: ``UC = <IDENTIFICACAO> - SOLE WEB + ... = 1.500,92; ...``
    """
    texto = (texto or "").strip()
    if not texto:
        return []
    blocos: list[tuple[str, tuple[int, ...], Decimal]] = []
    for bloco in _segmentos_observacoes_hub(texto):
        match = _RE_BLOCO_UC_OBS.match(bloco)
        if not match:
            raise HubPedidoError(
                f"Bloco de Observações inválido: {bloco!r}. "
                f"Use «{FORMATO_OBSERVACOES_HUB}» e valor tipo 1.500,92."
            )
        identificacao = match.group("identificacao").strip()
        servicos_brutos = match.group("servicos")
        valor = _parse_valor_monetario_hub(
            match.group("valor"), identificacao_uc=identificacao
        )
        codigos_servico: list[int] = []
        for parte in re.split(r"\s*\+\s*", servicos_brutos):
            codigos_servico.append(_resolver_token_servico_hub(parte))
        if not codigos_servico:
            raise HubPedidoError(
                f"UC {identificacao!r}: nenhum serviço após «-» em Observações (Detalhes)."
            )
        unicos = tuple(dict.fromkeys(codigos_servico))
        blocos.append((identificacao, unicos, valor))
    return blocos


def _resolver_codigo_instalacao_hub(identificacao: str, codigo_cliente: int) -> int:
    """Resolve instalacao.CODIGO a partir de IDENTIFICACAO + COD_CLIENTE (Código Cliente/Instalação)."""
    identificacao = identificacao.strip()
    if not identificacao:
        raise HubPedidoError("IDENTIFICACAO da UC vazia em Observações (Detalhes).")
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT CODIGO
                FROM instalacao
                WHERE IDENTIFICACAO = %s AND COD_CLIENTE = %s
                LIMIT 1
                """,
                (identificacao, codigo_cliente),
            )
            row = cur.fetchone()
    if not row:
        raise HubPedidoError(
            f"UC {identificacao!r} não encontrada em instalacao.IDENTIFICACAO "
            f"para cliente {codigo_cliente} (confira Observações e "
            "Código Cliente/Código da Instalação)."
        )
    return int(row[0])


def _resolver_linhas_observacoes_hub(
    texto: str, codigos_instalacao: list[int]
) -> list[InstalacaoObsHub]:
    """Associa cada bloco UC (serviços/valor) ao CODIGO do campo cliente/instalação."""
    linhas: list[InstalacaoObsHub] = []
    blocos = _parse_blocos_observacoes_hub(texto)
    for (identificacao, servicos, valor), codigo in zip(blocos, codigos_instalacao):
        linhas.append(
            InstalacaoObsHub(
                identificacao=identificacao,
                codigo_instalacao=codigo,
                servicos=servicos,
                valor=valor,
            )
        )
    return linhas


def _parse_observacoes_uc_hub(texto: str) -> list[InstalacaoObsHub]:
    """Compatível com testes: parse estrutural sem MySQL (sem CODIGO resolvido)."""
    return [
        InstalacaoObsHub(
            identificacao=ident,
            codigo_instalacao=0,
            servicos=servicos,
            valor=valor,
        )
        for ident, servicos, valor in _parse_blocos_observacoes_hub(texto)
    ]


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


def _p1_p2_do_deal(deal: dict) -> tuple[list[int], int]:
    """P2 e instalações (P1) somente do campo «codigo_cliente/inst1,inst2»."""
    codigo_cliente_raw = get_val(deal, FIELD_CODIGO_CLIENTE_INSTALACAO).strip()
    if not codigo_cliente_raw:
        raise HubPedidoError(
            "Código Cliente/Código da Instalação obrigatório no Pipedrive."
        )
    try:
        codigo_cliente, instalacoes_campo = parse_codigo_cliente_instalacao(
            codigo_cliente_raw
        )
    except ValueError as exc:
        raise HubPedidoError(str(exc)) from exc

    if not instalacoes_campo:
        raise HubPedidoError(
            "Informe as instalações após «/» em Código Cliente/Código da Instalação "
            "(ex.: 352/1234,3456). O campo Notas é independente e não define instalações HUB."
        )
    return instalacoes_campo, codigo_cliente


def _parse_codigos_notas(notas_raw: str) -> list[int]:
    """
    Campo Notas: um ou vários códigos de instalação separados por vírgula, ; ou espaço.
    Ex.: ``00665,01942`` → [665, 1942].
    """
    codigos: list[int] = []
    for parte in re.split(r"[,;\s]+", notas_raw.strip()):
        texto = parte.strip()
        if not texto:
            continue
        try:
            codigos.append(int(texto))
        except ValueError as exc:
            raise HubPedidoError(
                f"Notas: código de instalação inválido no Pipedrive: {texto!r}"
            ) from exc
    if not codigos:
        raise HubPedidoError("Notas vazio no Pipedrive.")
    vistos: set[int] = set()
    unicos: list[int] = []
    for codigo in codigos:
        if codigo not in vistos:
            vistos.add(codigo)
            unicos.append(codigo)
    return unicos


def _validar_instalacao_hub(codigo_instalacao: int, codigo_cliente: int) -> None:
    """Confere se cada CODIGO do campo cliente/instalação existe no HUB para o cliente."""
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM instalacao
                WHERE CODIGO = %s AND COD_CLIENTE = %s
                LIMIT 1
                """,
                (codigo_instalacao, codigo_cliente),
            )
            ok = cur.fetchone()
    if not ok:
        raise HubPedidoError(
            f"Instalação HUB {codigo_instalacao} não encontrada para cliente {codigo_cliente} "
            "(confira Código Cliente/Código da Instalação no Pipedrive)."
        )


def _validar_instalacoes_hub(
    codigos_instalacao: list[int], codigo_cliente: int
) -> None:
    for codigo in codigos_instalacao:
        _validar_instalacao_hub(codigo, codigo_cliente)


def _ativar_instalacoes_hub_inativas(
    cur,
    codigos_instalacao: list[int],
    codigo_cliente: int,
) -> list[int]:
    """
    Marca Ativo='S' nas instalações do pedido que estiverem inativas no HUB.

    Espelha o comportamento do desktop ao incluir UCs no pedido.
    """
    codigos = sorted({int(c) for c in codigos_instalacao if c})
    if not codigos:
        return []

    placeholders = ",".join(["%s"] * len(codigos))
    cur.execute(
        f"""
        SELECT CODIGO
        FROM instalacao
        WHERE COD_CLIENTE = %s
          AND CODIGO IN ({placeholders})
          AND COALESCE(Ativo, 'S') <> 'S'
        """,
        (codigo_cliente, *codigos),
    )
    inativas = [int(row[0]) for row in cur.fetchall()]
    if not inativas:
        return []

    ph2 = ",".join(["%s"] * len(inativas))
    cur.execute(
        f"""
        UPDATE instalacao
        SET Ativo = 'S'
        WHERE COD_CLIENTE = %s AND CODIGO IN ({ph2})
        """,
        (codigo_cliente, *inativas),
    )
    return inativas


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


def _pedido_hub_existe(codigo_pedido: int) -> bool:
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pedido WHERE codigo = %s LIMIT 1",
                (int(codigo_pedido),),
            )
            return bool(cur.fetchone())


def _skip_parceiro_novo_hub(
    deal_id: str, *, parceiro_plune_criado: bool | None
) -> tuple[dict[str, Any] | None, dict | None]:
    if parceiro_plune_criado is None:
        registro = buscar_por_deal_id(deal_id)
        parceiro_novo = bool(registro and registro.get("parceiro_plune_criado"))
    else:
        registro = buscar_por_deal_id(deal_id)
        parceiro_novo = bool(parceiro_plune_criado)
    if parceiro_novo:
        return (
            {
                "status": "skipped",
                "deal_id": deal_id,
                "reason": "parceiro_novo_plune",
            },
            registro,
        )
    return None, registro


def _montar_dados_pedido_hub_deal(deal_id: str, deal: dict) -> dict[str, Any]:
    try:
        codigos_instalacao, codigo_cliente = _p1_p2_do_deal(deal)
    except HubPedidoError as exc:
        raise HubPedidoError(f"Deal {deal_id}: {exc}") from exc

    obs_pipe = get_val(deal, FIELD_OBSERVACOES_DETALHES).strip()
    linhas_obs = validar_observacoes_hub_obrigatorias(
        deal_id, obs_pipe, codigos_instalacao, codigo_cliente
    )
    _validar_instalacoes_hub(codigos_instalacao, codigo_cliente)
    valor_decimal = sum((linha.valor for linha in linhas_obs), Decimal("0")).quantize(
        Decimal("0.01")
    )

    hoje = date.today()
    data_comercial = _parse_data_pipe(get_val(deal, FIELD_DATA_PRIMEIRA_COBRANCA)) or hoje
    titulo = get_numero_contrato(deal)[:255]
    link = f"https://gebras.pipedrive.com/deal/{deal_id}"
    observacoes = (
        f"{obs_pipe}\n\nPIPEDRIVE:\n{link}" if obs_pipe else f"PIPEDRIVE:\n{link}"
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

    tem_perc_economia, perc_economia = _perc_economia_do_deal(deal)
    return {
        "codigos_instalacao": codigos_instalacao,
        "codigo_cliente": codigo_cliente,
        "linhas_obs": linhas_obs,
        "valor_decimal": valor_decimal,
        "data_comercial": data_comercial,
        "primeira_cobranca": data_comercial,
        "titulo": titulo,
        "observacoes": observacoes,
        "codigo_usuario": codigo_usuario,
        "codigo_plune_recorrente": codigo_plune_recorrente,
        "tem_perc_economia": tem_perc_economia,
        "perc_economia": perc_economia,
    }


def _inserir_filhos_pedido_hub(
    cur,
    codigo_pedido: int,
    linhas_obs: list[InstalacaoObsHub],
    *,
    tem_perc_economia: bool,
    perc_economia: Decimal,
    codigo_plune_recorrente: int,
) -> None:
    for linha_obs in linhas_obs:
        codigo_instalacao = linha_obs.codigo_instalacao
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
                linha_obs.valor,
                _bool_char(tem_perc_economia),
                perc_economia,
            ),
        )
        for codigo_servico in linha_obs.servicos:
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


def _resultado_pedido_hub(
    deal_id: str,
    status: str,
    codigo_pedido: int,
    dados: dict[str, Any],
    *,
    instalacoes_ativadas: list[int] | None = None,
) -> dict[str, Any]:
    linhas_obs = dados["linhas_obs"]
    return {
        "status": status,
        "deal_id": deal_id,
        "pedido_hub_id": codigo_pedido,
        "codigo_cliente": dados["codigo_cliente"],
        "codigos_instalacao": dados["codigos_instalacao"],
        "instalacoes_ativadas": list(instalacoes_ativadas or []),
        "instalacoes_obs": [
            {
                "identificacao": linha.identificacao,
                "codigo": linha.codigo_instalacao,
                "servicos": list(linha.servicos),
                "valor": str(linha.valor),
            }
            for linha in linhas_obs
        ],
        "pedido_plune_recorrente": dados["codigo_plune_recorrente"],
    }


def criar_pedido_hub(
    deal_id: str,
    *,
    parceiro_plune_criado: bool | None = None,
    ignorar_ja_criado: bool = False,
) -> dict[str, Any]:
    """
    Cria pedido no HUB se parceiro Plune já existia no ganho.

    parceiro_plune_criado: se informado, usa em vez de ler envelopes_pending
    (útil quando ainda não há envelope Clicksign, ex. DEV_PULAR_CLICKSIGN).
    ignorar_ja_criado: recria quando o estado local indica pedido mas a linha sumiu no HUB.
    """
    deal_id = str(deal_id).strip()
    if get_automacao_config().pular_hub:
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "hub_criacao_desabilitada",
        }
    skip, registro = _skip_parceiro_novo_hub(
        deal_id, parceiro_plune_criado=parceiro_plune_criado
    )
    if skip:
        return skip
    if (
        not ignorar_ja_criado
        and registro
        and registro.get("hub_pedido_criado")
    ):
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "hub_pedido_ja_criado",
            "pedido_hub_id": registro.get("pedido_hub_id"),
        }

    deal = buscar_deal_por_id(deal_id)
    if not deal:
        raise HubPedidoError(f"Deal {deal_id} não encontrado no Pipedrive")

    dados = _montar_dados_pedido_hub_deal(deal_id, deal)
    agora = datetime.now()
    vigencia = 12
    renovar = _bool_char(True)

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
                    dados["codigo_usuario"],
                    dados["titulo"],
                    dados["observacoes"],
                    HUB_SITUACAO_NOVO,
                    dados["data_comercial"],
                    dados["data_comercial"],
                    vigencia,
                    renovar,
                    dados["primeira_cobranca"],
                    dados["valor_decimal"],
                ),
            )
            codigo_pedido = int(cur.lastrowid)
            codigos_uc_pedido = [linha.codigo_instalacao for linha in dados["linhas_obs"]]
            instalacoes_ativadas = _ativar_instalacoes_hub_inativas(
                cur, codigos_uc_pedido, dados["codigo_cliente"]
            )
            _inserir_filhos_pedido_hub(
                cur,
                codigo_pedido,
                dados["linhas_obs"],
                tem_perc_economia=dados["tem_perc_economia"],
                perc_economia=dados["perc_economia"],
                codigo_plune_recorrente=dados["codigo_plune_recorrente"],
            )

    marcar_hub_pedido_criado(deal_id, codigo_pedido)
    return _resultado_pedido_hub(
        deal_id,
        "created",
        codigo_pedido,
        dados,
        instalacoes_ativadas=instalacoes_ativadas,
    )


def atualizar_pedido_hub(
    deal_id: str, *, parceiro_plune_criado: bool | None = None
) -> dict[str, Any]:
    """Atualiza pedido HUB existente com dados atuais do Pipedrive (correção/regeneração)."""
    deal_id = str(deal_id).strip()
    skip, registro = _skip_parceiro_novo_hub(
        deal_id, parceiro_plune_criado=parceiro_plune_criado
    )
    if skip:
        return skip
    if not registro or not registro.get("hub_pedido_criado"):
        return {
            "status": "missing",
            "deal_id": deal_id,
            "reason": "hub_pedido_nao_criado",
        }

    pedido_hub_id = registro.get("pedido_hub_id")
    if not pedido_hub_id:
        return {
            "status": "missing",
            "deal_id": deal_id,
            "reason": "pedido_hub_id_ausente",
        }

    codigo_pedido = int(pedido_hub_id)
    if not _pedido_hub_existe(codigo_pedido):
        return {
            "status": "missing",
            "deal_id": deal_id,
            "reason": "pedido_hub_inexistente",
            "pedido_hub_id": codigo_pedido,
        }

    deal = buscar_deal_por_id(deal_id)
    if not deal:
        raise HubPedidoError(f"Deal {deal_id} não encontrado no Pipedrive")

    dados = _montar_dados_pedido_hub_deal(deal_id, deal)
    agora = datetime.now()

    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pedido SET
                    descricao=%s, observacoes=%s, valorTotal=%s,
                    dataComercial=%s, inicioContrato=%s, primeiraCobranca=%s,
                    dataAlteracao=%s, codigoUsuarioAlteracao=%s
                WHERE codigo=%s
                """,
                (
                    dados["titulo"],
                    dados["observacoes"],
                    dados["valor_decimal"],
                    dados["data_comercial"],
                    dados["data_comercial"],
                    dados["primeira_cobranca"],
                    agora,
                    dados["codigo_usuario"],
                    codigo_pedido,
                ),
            )
            cur.execute(
                "DELETE FROM pedido_instalacao_extra WHERE codigoPedido=%s",
                (codigo_pedido,),
            )
            cur.execute(
                "DELETE FROM pedido_instalacao_servico WHERE codigoPedido=%s",
                (codigo_pedido,),
            )
            cur.execute(
                "DELETE FROM pedido_plune WHERE codigoPedido=%s",
                (codigo_pedido,),
            )
            codigos_uc_pedido = [linha.codigo_instalacao for linha in dados["linhas_obs"]]
            instalacoes_ativadas = _ativar_instalacoes_hub_inativas(
                cur, codigos_uc_pedido, dados["codigo_cliente"]
            )
            _inserir_filhos_pedido_hub(
                cur,
                codigo_pedido,
                dados["linhas_obs"],
                tem_perc_economia=dados["tem_perc_economia"],
                perc_economia=dados["perc_economia"],
                codigo_plune_recorrente=dados["codigo_plune_recorrente"],
            )

    return _resultado_pedido_hub(
        deal_id,
        "updated",
        codigo_pedido,
        dados,
        instalacoes_ativadas=instalacoes_ativadas,
    )


def sincronizar_pedido_hub_deal(
    deal_id: str,
    *,
    parceiro_plune_criado: bool | None = None,
    permitir_criacao: bool = True,
) -> dict[str, Any]:
    """
    Cria ou atualiza pedido HUB conforme estado local e banco gebras.

    permitir_criacao=False (pré-aprovação Plune em produção): só atualiza pedido
    já existente; criação fica para após aprovar_pedidos_plune.
    """
    deal_id = str(deal_id).strip()
    skip, registro = _skip_parceiro_novo_hub(
        deal_id, parceiro_plune_criado=parceiro_plune_criado
    )
    if skip:
        return skip

    if registro and registro.get("hub_pedido_criado"):
        pedido_hub_id = registro.get("pedido_hub_id")
        if pedido_hub_id and _pedido_hub_existe(int(pedido_hub_id)):
            return atualizar_pedido_hub(
                deal_id, parceiro_plune_criado=parceiro_plune_criado
            )
        if not permitir_criacao:
            return {
                "status": "skipped",
                "deal_id": deal_id,
                "reason": "hub_aguardando_aprovacao_plune",
            }
        return criar_pedido_hub(
            deal_id,
            parceiro_plune_criado=parceiro_plune_criado,
            ignorar_ja_criado=True,
        )

    if not permitir_criacao:
        return {
            "status": "skipped",
            "deal_id": deal_id,
            "reason": "hub_aguardando_aprovacao_plune",
        }

    return criar_pedido_hub(deal_id, parceiro_plune_criado=parceiro_plune_criado)


def tentar_sincronizar_pedido_hub_deal(
    deal_id: str,
    *,
    parceiro_plune_criado: bool | None = None,
    permitir_criacao: bool = True,
) -> dict[str, Any] | None:
    """Wrapper com log; cria ou atualiza; não propaga exceção (fluxo principal continua)."""
    deal_id = str(deal_id).strip()
    try:
        result = sincronizar_pedido_hub_deal(
            deal_id,
            parceiro_plune_criado=parceiro_plune_criado,
            permitir_criacao=permitir_criacao,
        )
        log_resultado_hub(deal_id, result)
        return result
    except HubPedidoError as exc:
        print(
            f"[!] HUB: falha ao sincronizar pedido (deal {deal_id}): {exc}",
            flush=True,
        )
        return None
    except Exception as exc:
        print(f"[!] HUB: erro inesperado (deal {deal_id}): {exc}", flush=True)
        return None


def tentar_criar_pedido_hub_deal(
    deal_id: str, *, parceiro_plune_criado: bool | None = None
) -> dict[str, Any] | None:
    """Alias pós-aprovação Plune: sempre permite criação."""
    return tentar_sincronizar_pedido_hub_deal(
        deal_id,
        parceiro_plune_criado=parceiro_plune_criado,
        permitir_criacao=True,
    )


def log_resultado_hub(deal_id: str, result: dict) -> None:
    status = result.get("status")
    if status == "created":
        print(
            f"[v] HUB: pedido criado — id={result.get('pedido_hub_id')} (deal {deal_id}).",
            flush=True,
        )
    elif status == "updated":
        print(
            f"[v] HUB: pedido atualizado — id={result.get('pedido_hub_id')} (deal {deal_id}).",
            flush=True,
        )
    elif status == "skipped":
        reason = result.get("reason")
        if reason == "hub_aguardando_aprovacao_plune":
            print(
                f"[*] HUB: aguardando aprovação Plune para criar pedido (deal {deal_id}).",
                flush=True,
            )
        elif reason == "hub_criacao_desabilitada":
            print(
                f"[*] HUB: criação desabilitada (PULAR_HUB) — deal {deal_id}.",
                flush=True,
            )
        else:
            print(
                f"[*] HUB: ignorado para deal {deal_id} — {reason}",
                flush=True,
            )
    else:
        print(f"[v] HUB: resultado {result}", flush=True)
