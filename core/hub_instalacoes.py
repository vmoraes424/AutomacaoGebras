"""Consulta instalações do HUB (MySQL gebras) para o formulário web."""

from __future__ import annotations

from dataclasses import dataclass

from core.hub_pedido import HubPedidoError, hub_conn
from core.pipedrive_fields import (
    format_codigo_cliente_instalacao,
    parse_codigo_cliente_instalacao,
)


class HubInstalacoesError(ValueError):
    """Entrada inválida ou campo cliente/instalação malformado."""


class HubInstalacoesReadError(RuntimeError):
    """Falha ao consultar MySQL HUB."""


@dataclass(frozen=True)
class HubInstalacao:
    codigo: int
    codigo_cliente: int
    identificacao: str
    razao_social: str
    cidade: str
    uf: str
    ativo: bool
    selecionada: bool

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "codigo_cliente": self.codigo_cliente,
            "identificacao": self.identificacao,
            "razao_social": self.razao_social,
            "cidade": self.cidade,
            "uf": self.uf,
            "ativo": self.ativo,
            "selecionada": self.selecionada,
        }


@dataclass(frozen=True)
class HubInstalacoesResult:
    codigo_cliente: int
    codigos_instalacao_selecionados: tuple[int, ...]
    formato_pipedrive: str
    instalacoes: tuple[HubInstalacao, ...]
    codigos_nao_encontrados: tuple[int, ...]

    def to_dict(self) -> dict:
        return {
            "codigo_cliente": self.codigo_cliente,
            "codigos_instalacao_selecionados": list(self.codigos_instalacao_selecionados),
            "formato_pipedrive": self.formato_pipedrive,
            "instalacoes": [row.to_dict() for row in self.instalacoes],
            "codigos_nao_encontrados": list(self.codigos_nao_encontrados),
        }


def _listar_instalacoes_mysql(codigo_cliente: int) -> list[dict]:
    with hub_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    CODIGO,
                    COD_CLIENTE,
                    COALESCE(IDENTIFICACAO, ''),
                    COALESCE(RAZAOSOCIAL, ''),
                    COALESCE(CIDADE, ''),
                    COALESCE(UF, ''),
                    COALESCE(Ativo, 'S')
                FROM instalacao
                WHERE COD_CLIENTE = %s
                ORDER BY CODIGO
                """,
                (codigo_cliente,),
            )
            rows = cur.fetchall()
    return [
        {
            "codigo": int(row[0]),
            "codigo_cliente": int(row[1]),
            "identificacao": str(row[2] or "").strip(),
            "razao_social": str(row[3] or "").strip(),
            "cidade": str(row[4] or "").strip(),
            "uf": str(row[5] or "").strip(),
            "ativo": str(row[6] or "S").strip().upper() == "S",
        }
        for row in rows
    ]


def consultar_instalacoes_hub(codigo_cliente_instalacao: str) -> HubInstalacoesResult:
    """
    Resolve instalações HUB a partir do mesmo texto do campo Pipedrive.

    - «352» → todas as instalações do cliente 352 (nenhuma selecionada).
    - «352/1234,3456» → todas do cliente; marca selecionadas; avisa códigos inexistentes.
  """
    raw = (codigo_cliente_instalacao or "").strip()
    if not raw:
        raise HubInstalacoesError(
            "Informe o código do cliente ou «codigo_cliente/inst1,inst2»."
        )
    try:
        codigo_cliente, selecionados = parse_codigo_cliente_instalacao(raw)
    except ValueError as exc:
        raise HubInstalacoesError(str(exc)) from exc

    try:
        rows = _listar_instalacoes_mysql(codigo_cliente)
    except HubPedidoError as exc:
        raise HubInstalacoesReadError(str(exc)) from exc
    except Exception as exc:
        raise HubInstalacoesReadError(
            f"Falha ao consultar instalações HUB: {exc}"
        ) from exc

    selecionados_set = set(selecionados)
    codigos_hub = {row["codigo"] for row in rows}
    nao_encontrados = tuple(c for c in selecionados if c not in codigos_hub)

    instalacoes = tuple(
        HubInstalacao(
            codigo=row["codigo"],
            codigo_cliente=row["codigo_cliente"],
            identificacao=row["identificacao"],
            razao_social=row["razao_social"],
            cidade=row["cidade"],
            uf=row["uf"],
            ativo=row["ativo"],
            selecionada=row["codigo"] in selecionados_set,
        )
        for row in rows
    )

    return HubInstalacoesResult(
        codigo_cliente=codigo_cliente,
        codigos_instalacao_selecionados=tuple(selecionados),
        formato_pipedrive=format_codigo_cliente_instalacao(codigo_cliente, selecionados),
        instalacoes=instalacoes,
        codigos_nao_encontrados=nao_encontrados,
    )
