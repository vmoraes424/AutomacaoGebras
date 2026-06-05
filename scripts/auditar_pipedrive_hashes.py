"""Auditoria: hashes em pipedrive_fields.py vs API e docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import pipedrive_fields as pf
from scripts.gerar_pipedrive_campos_md import AUTOMACAO, fetch_deal_fields, load_token

MD_PATH = ROOT / "docs" / "Pipedrive" / "Pipedrive-campos-hashes.md"
OLD_SUBCENTRO = (
    "3b5fc4072a4bff3e5e24dce974d20e15c6ebaed6",
    "4f6e152a7d4f89dbd6664ef97980531394721599",
)
# Removidos do Pipedrive (jun/2026); mantidos no código para deals antigos
LEGACY_REMOVED = frozenset({
    "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b",
    "92359b129485b08fd024b8c28ef022e7635419a3",
    "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2",
})


def main() -> int:
    consts: dict[str, str] = {}
    for name, val in vars(pf).items():
        if name.startswith("FIELD_") and isinstance(val, str) and len(val) == 40:
            consts[name] = val
    for papel, _nome_cs, chave, *_ in pf.SIGNER_FIELDS:
        consts[f"SIGNER:{papel}"] = chave

    fields = fetch_deal_fields(load_token())
    by_code = {str(f.get("field_code")): f for f in fields}
    hash_to_const = {v: k for k, v in consts.items()}

    print("=== 1. Constantes vs API Pipedrive ===\n")
    missing = 0
    for nome, hashv in sorted(consts.items()):
        f = by_code.get(hashv)
        if not f:
            if hashv in LEGACY_REMOVED:
                print(f"AVISO {nome:36} hash removido da API (legado)")
            else:
                missing += 1
                print(f"ERRO  {nome:36} hash ausente na API")
        else:
            print(
                f"OK    {nome:36} -> {f.get('field_name')!r} "
                f"({f.get('field_type')})"
            )

    print("\n=== 2. Hashes duplicados (mesmo hash, varias constantes) ===\n")
    rev: dict[str, list[str]] = {}
    for n, h in consts.items():
        rev.setdefault(h, []).append(n)
    dup = False
    for h, names in rev.items():
        if len(names) > 1:
            dup = True
            print(f"  {h}: {names}")
    if not dup:
        print("  (nenhum)")

    print("\n=== 3. AUTOMACAO dict vs pipedrive_fields.py ===\n")
    code_hashes = set(consts.values())
    for h, uso in sorted(AUTOMACAO.items()):
        if h not in by_code:
            print(f"  hash morto em AUTOMACAO: {h[:20]}... -> {uso}")
        elif h not in code_hashes:
            print(f"  AUTOMACAO sem FIELD_ correspondente: {uso}")

    for h, nome in sorted(consts.items(), key=lambda x: x[1]):
        if h not in AUTOMACAO and not h.startswith("SIGNER:"):
            # signers partially in AUTOMACAO
            pass
    for h in code_hashes:
        if h not in AUTOMACAO:
            print(f"  constante sem entrada AUTOMACAO: {hash_to_const.get(h)}")

    print("\n=== 4. Nomenclatura / semantica ===\n")
    f2 = by_code.get(pf.FIELD_REGIONAL, {})
    f3 = by_code.get(pf.FIELD_SUBCENTRO_NIVEL_3, {})
    print(f"  FIELD_REGIONAL -> API: {f2.get('field_name')!r} ({f2.get('field_type')})")
    print(
        f"  FIELD_SUBCENTRO_NIVEL_3 -> API: {f3.get('field_name')!r} "
        f"({f3.get('field_type')})"
    )
    if f2.get("field_name") and str(f2.get("field_name")) != "Regional":
        print(
            f"  AVISO: FIELD_REGIONAL -> API: {f2.get('field_name')!r} "
            "(esperado 'Regional')"
        )
    if f3.get("field_name") and str(f3.get("field_name")) != "Consultor":
        print(
            f"  AVISO: FIELD_SUBCENTRO_NIVEL_3 -> API: {f3.get('field_name')!r} "
            "(esperado 'Consultor')"
        )

    iq = by_code.get(pf.FIELD_INDICADORES_QUALIDADE, {})
    qe = by_code.get(pf.FIELD_QUALIDADE_ENERGIA, {})
    print(f"  FIELD_INDICADORES_QUALIDADE -> {iq.get('field_name')!r}")
    print(f"  FIELD_QUALIDADE_ENERGIA -> {qe.get('field_name')!r}")

    print("\n=== 5. Contrato automacao_contrato (mapeamento suspeito) ===\n")
    print(
        "  automacao_contrato usa qualidade_energia com "
        "FIELD_INDICADORES_QUALIDADE (verificar se deveria ser "
        "FIELD_QUALIDADE_ENERGIA / Sole Consultoria)"
    )

    print("\n=== 6. Campos custom API (centro/filial) nao usados no codigo ===\n")
    for f in sorted(fields, key=lambda x: x.get("field_name") or ""):
        name = (f.get("field_name") or "").lower()
        if any(k in name for k in ("sub centro", "filial", "regional", "centro")):
            code = str(f.get("field_code"))
            mapped = hash_to_const.get(code, "")
            tag = mapped or "NAO USADO"
            print(f"  {f.get('field_name')} | {code} | {tag}")

    print("\n=== 7. Documentacao Pipedrive-campos-hashes.md ===\n")
    if MD_PATH.exists():
        md = MD_PATH.read_text(encoding="utf-8")
        for nome, h in [
            ("FIELD_REGIONAL", pf.FIELD_REGIONAL),
            ("FIELD_SUBCENTRO_NIVEL_3", pf.FIELD_SUBCENTRO_NIVEL_3),
        ]:
            print(f"  {nome} no .md: {'sim' if h in md else 'NAO'}")
        for oh in OLD_SUBCENTRO:
            if oh in md:
                print(f"  AVISO: hash antigo ainda no .md: {oh}")
    else:
        print("  arquivo .md nao encontrado")

    print("\n=== 8. Enum: leitura get_val vs get_enum_label ===\n")
    enum_fields = [
        ("FIELD_REGIONAL", pf.FIELD_REGIONAL),
        ("FIELD_SUBCENTRO_NIVEL_3", pf.FIELD_SUBCENTRO_NIVEL_3),
        ("FIELD_FILIAL", pf.FIELD_FILIAL),
    ]
    for label, code in enum_fields:
        f = by_code.get(code, {})
        if f.get("field_type") == "enum":
            usado = "get_enum_label" if code != pf.FIELD_FILIAL else "get_filial_chaves"
            print(f"  {label}: enum -> {usado}")
        elif f.get("field_type") == "double" or f.get("field_type") == "int":
            print(f"  {label}: numerico ({f.get('field_type')}) -> get_val")

    print(f"\nResumo: {len(consts)} constantes, {missing} hash(es) invalido(s) na API")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
