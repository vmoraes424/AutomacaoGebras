#!/usr/bin/env python3
"""Consulta um deal no Pipedrive (v1 + v2) e imprime resumo dos campos da automação."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.pipedrive_fields import (  # noqa: E402
    CAMPOS_CONTRATO_OBRIGATORIOS,
    FIELD_OBSERVACOES_DETALHES,
    buscar_deal_por_id,
    get_val,
)
from core.pipedrive_stages import _buscar_deal_v2, deal_esta_em_etapa_contrato  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="GET deal Pipedrive (validação)")
    parser.add_argument("deal_id", help="ID do deal, ex.: 746")
    args = parser.parse_args()

    deal_v1 = buscar_deal_por_id(args.deal_id)
    if not deal_v1:
        print(f"Deal {args.deal_id} não encontrado.", file=sys.stderr)
        return 1

    deal_v2 = _buscar_deal_v2(args.deal_id)

    summary = {
        "deal_id": deal_v1.get("id"),
        "title": deal_v1.get("title"),
        "status": deal_v1.get("status"),
        "stage_id": deal_v1.get("stage_id"),
        "owner_id_v1": deal_v1.get("owner_id"),
        "owner_id_v2": deal_v2.get("owner_id"),
        "em_etapa_contrato": deal_esta_em_etapa_contrato(deal_v2),
        "custom_fields_count": len(deal_v1.get("custom_fields") or {}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n--- Campos automação ---")
    for label, code, tipo in CAMPOS_CONTRATO_OBRIGATORIOS:
        val = get_val(deal_v1, code)
        print(f"{label}: {val}")

    obs = get_val(deal_v1, FIELD_OBSERVACOES_DETALHES)
    print(f"Observações (Detalhes): {obs or '(vazio)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
