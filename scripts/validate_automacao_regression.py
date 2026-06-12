#!/usr/bin/env python3
"""Valida regressão da automação pós-formulário web (sem integration/MySQL live)."""

from __future__ import annotations

import subprocess
import sys


AUTOMACAO_REGRESSION_TESTS = [
    "tests/test_automacao_regression_form.py",
    "tests/test_form_regression_legacy.py",
    "tests/test_form_worker_integration.py",
    "tests/test_form_deal_adapter.py",
    "tests/test_form_uc_hub.py",
    "tests/test_form_hub_pedido_integration.py",
    "tests/test_fill_contract.py",
    "tests/test_extrair_signatarios.py",
    "tests/test_plune_pedido_unit.py",
    "tests/test_hub_pedido_unit.py",
    "tests/test_automacao_contrato_unit.py",
    "tests/test_form_rollback.py",
]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *AUTOMACAO_REGRESSION_TESTS,
        "-m",
        "not integration",
        "-q",
    ]
    print("Validando automacao (form -> worker -> Plune/Clicksign/HUB)...")
    print(" ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
