"""
CLI MySQL gebras_automacao (estado + catálogo da automação).

Comandos: docs/automacao-db-cli.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PORT
from core.database import (
    db_conn,
    detalhe_estado_deal,
    limpar_estado_deal,
    limpar_todo_estado,
    resumo_estado_banco,
    sincronizar_banco_completo,
)


def _mysql_label() -> str:
    return f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"


def _confirmar(prompt: str, *, yes: bool, token: str) -> bool:
    if yes:
        return True
    digitado = input(f"{prompt} [{token}]: ").strip()
    return digitado == token


def cmd_status(_: argparse.Namespace) -> int:
    print(f"MySQL: {_mysql_label()}\n")
    for chave, valor in resumo_estado_banco().items():
        print(f"  {chave}: {valor}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    detalhe = detalhe_estado_deal(args.deal_id)
    print(json.dumps(detalhe, indent=2, ensure_ascii=False, default=str))
    total = sum(len(detalhe[k]) for k in detalhe if k != "deal_id")
    if total == 0:
        print(f"\n(nenhum registro de estado para deal {args.deal_id})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    limit = args.limit
    with db_conn() as conn:
        if args.tipo == "deals":
            rows = conn.execute(
                """
                SELECT deal_id, won_time, processed_at
                FROM deals_processed
                ORDER BY processed_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
            for r in rows:
                print(f"{r['deal_id']}|{r['won_time']}  ({r['processed_at']})")
        elif args.tipo == "legado":
            rows = conn.execute(
                """
                SELECT deal_id, blocked_at
                FROM deals_legacy_block
                ORDER BY blocked_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
            for r in rows:
                print(f"{r['deal_id']}  bloqueado em {r['blocked_at']}")
        elif args.tipo == "envelopes":
            rows = conn.execute(
                """
                SELECT deal_id, envelope_id, envelope_name,
                       pedidos_plune_criados, pedidos_plune_aprovados, pedido_plune_id
                FROM envelopes_pending
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
            for r in rows:
                print(
                    f"deal={r['deal_id']} envelope={r['envelope_id']} "
                    f"plune_criado={r['pedidos_plune_criados']} "
                    f"aprovado={r['pedidos_plune_aprovados']} "
                    f"pedido_id={r['pedido_plune_id'] or '-'}"
                )
        elif args.tipo == "pedidos":
            if args.deal_id:
                rows = conn.execute(
                    """
                    SELECT pedido_key, created_at
                    FROM pedidos_plune_keys
                    WHERE pedido_key = %s OR pedido_key LIKE %s
                    ORDER BY pedido_key
                    LIMIT %s
                    """,
                    (args.deal_id, f"{args.deal_id}-%", limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT pedido_key, created_at
                    FROM pedidos_plune_keys
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                ).fetchall()
            for r in rows:
                print(f"{r['pedido_key']}  ({r['created_at']})")
    return 0


def cmd_rm(args: argparse.Namespace) -> int:
    if args.alvo == "deal":
        if not _confirmar(
            f"Apagar estado do deal {args.deal_id}?",
            yes=args.yes,
            token=str(args.deal_id),
        ):
            print("Cancelado.")
            return 1
        stats = limpar_estado_deal(args.deal_id)
        print(f"Removido estado do deal {args.deal_id}:")
        for tabela, n in stats.items():
            if n:
                print(f"  {tabela}: {n}")
        if not any(stats.values()):
            print("  (nada encontrado)")
        return 0

    if args.alvo == "estado":
        if not _confirmar(
            "Apagar TODO o estado (deals, envelopes, pedidos)? Catálogo não é alterado.",
            yes=args.yes,
            token="LIMPAR",
        ):
            print("Cancelado.")
            return 1
        stats = limpar_todo_estado()
        print("Estado da automação zerado:")
        for tabela, n in stats.items():
            print(f"  {tabela}: {n}")
        return 0

    print(f"Alvo desconhecido: {args.alvo}", file=sys.stderr)
    return 2


def cmd_catalogo(_: argparse.Namespace) -> int:
    import importlib.util

    path = Path(__file__).resolve().parent / "ver_catalogo_db.py"
    spec = importlib.util.spec_from_file_location("ver_catalogo_db", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.main()


def cmd_sync(args: argparse.Namespace) -> int:
    print(f"MySQL: {_mysql_label()}\n")
    resultado = sincronizar_banco_completo(
        sync_subcentros=not args.sem_plune,
        force_subcentros=True,
    )
    if not args.sem_plune:
        print(f"Subcentros Plune: {resultado.get('subcentros', 0)} upserts")
    print("\nResumo:")
    for chave, valor in (resultado.get("resumo") or resumo_estado_banco()).items():
        print(f"  {chave}: {valor}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CLI MySQL gebras_automacao (estado + catálogo)",
        prog="automacao_db",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Não pedir confirmação (rm)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Contagens das tabelas").set_defaults(
        func=cmd_status
    )

    p_show = sub.add_parser("show", help="Estado de um deal (JSON)")
    p_show.add_argument("deal_id", help="ID do deal no Pipedrive")
    p_show.set_defaults(func=cmd_show)

    p_list = sub.add_parser("list", help="Listar registros")
    p_list.add_argument(
        "tipo",
        choices=("deals", "legado", "envelopes", "pedidos"),
        help="Tabela de estado",
    )
    p_list.add_argument("--deal-id", help="Filtrar pedidos por deal")
    p_list.add_argument("--limit", type=int, default=100, help="Máx. linhas")
    p_list.set_defaults(func=cmd_list)

    p_rm = sub.add_parser("rm", help="Remover estado (não apaga catálogo)")
    p_rm.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Não pedir confirmação",
    )
    p_rm_sub = p_rm.add_subparsers(dest="alvo", required=True)

    p_rm_deal = p_rm_sub.add_parser("deal", help="Limpar um deal")
    p_rm_deal.add_argument("deal_id")
    p_rm_deal.set_defaults(func=cmd_rm)

    p_rm_estado = p_rm_sub.add_parser("estado", help="Zerar todo estado da automação")
    p_rm_estado.set_defaults(func=cmd_rm, deal_id=None)

    sub.add_parser("catalogo", help="Filiais, branches e subcentros").set_defaults(
        func=cmd_catalogo
    )

    p_sync = sub.add_parser("sync", help="Seed catálogo + sync subcentros Plune")
    p_sync.add_argument("--sem-plune", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
