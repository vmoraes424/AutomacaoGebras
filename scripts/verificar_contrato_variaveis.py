"""Compara placeholders em contrato_padrao.docx com chaves de fill_contract."""

from __future__ import annotations

import ast
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "contrato_padrao.docx"
FILL_CONTRACT = ROOT / "core" / "automacao_contrato.py"


def placeholders_docx(path: Path) -> set[str]:
    found: set[str] = set()
    pat = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not (
                name.endswith(".xml")
                and ("document" in name or "header" in name or "footer" in name)
            ):
                continue
            xml = z.read(name).decode("utf-8", errors="replace")
            plain = re.sub(r"<[^>]+>", "", xml)
            for m in pat.finditer(xml):
                found.add(m.group(1))
            for m in pat.finditer(plain):
                found.add(m.group(1))
    return found


def chaves_contexto_fill_contract() -> set[str]:
    src = FILL_CONTRACT.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "fill_contract":
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                val = child.value
                if isinstance(val, ast.Dict):
                    keys: set[str] = set()
                    for k in val.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            keys.add(k.value)
                    return keys
    raise RuntimeError("contexto = {...} nao encontrado em fill_contract")


def main() -> int:
    docx_vars = placeholders_docx(DOCX)
    ctx_vars = chaves_contexto_fill_contract()

    faltando = sorted(docx_vars - ctx_vars)
    extras = sorted(ctx_vars - docx_vars)

    print(f"Docx: {len(docx_vars)} placeholders | Contexto: {len(ctx_vars)} chaves\n")

    if faltando:
        print("FALTAM no fill_contract (quebram o Word):")
        for v in faltando:
            print(f"  - {v}")
    else:
        print("OK: todos os placeholders do docx estao no contexto.")

    if extras:
        print("\nExtras no contexto (nao usados no docx — ok):")
        for v in extras:
            print(f"  - {v}")

    return 1 if faltando else 0


if __name__ == "__main__":
    raise SystemExit(main())
