"""
Cursor project hooks — contexto alinhado a ENTENDIMENTO_SISTEMA.md.
Entrada: JSON em stdin. Saída: JSON em stdout (fail-open em erro).
"""
from __future__ import annotations

import json
import os
import sys

TRACKED_BASENAMES = frozenset(
    {
        "automacao_contrato.py",
        "criar_webhook.py",
        "ENTENDIMENTO_SISTEMA.md",
        "contrato_padrao.docx",
        "hooks.json",
    }
)


def _session_context() -> str:
    return (
        "**Automacao Gebras (contratos)** - Leitura recomendada na raiz do repo: "
        "`ENTENDIMENTO_SISTEMA.md`. "
        "Resumo: deal **ganho** no Pipedrive (apos o arranque do script, em UTC) -> "
        "`automacao_contrato.py` faz polling -> preenche `contrato_padrao.docx` com **docxtpl** "
        "-> grava em `contratos/` -> **Clicksign API v3** (grupos sequenciais). "
        "Estado: `deals_processados.txt`. "
        "`criar_webhook.py` so **regista** webhook; nao processa callbacks aqui. "
        "Mapeamentos CRM usam **hashes** de custom fields no codigo."
    )


def _normalize(p: str) -> str:
    return p.replace("\\", "/")


def _paths_from_tool_input(raw: object) -> list[str]:
    out: list[str] = []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return out
    if not isinstance(raw, dict):
        return out
    for key in ("path", "file_path", "target_file", "file"):
        val = raw.get(key)
        if isinstance(val, str) and val.strip():
            out.append(val.strip())
    return out


def _is_tracked_file(path: str) -> bool:
    if not path:
        return False
    norm = _normalize(path)
    base = os.path.basename(norm)
    if base in TRACKED_BASENAMES:
        return True
    markers = ("/.cursor/skills/", "/.cursor/agents/", "/.cursor/hooks/")
    return any(m in norm for m in markers)


def _post_write_context(paths: list[str]) -> str | None:
    if not any(_is_tracked_file(p) for p in paths):
        return None
    return (
        "Editaste um ficheiro central do fluxo (automacao, modelo, doc de sistema ou `.cursor/`). "
        "Se o **comportamento** mudou, atualiza `ENTENDIMENTO_SISTEMA.md` e, se aplicavel, "
        "placeholders em `contrato_padrao.docx` / hashes Pipedrive em `fill_contract()` ou "
        "signatarios em `extrair_signatarios()`. Nao commits de tokens - preferir variaveis de ambiente."
    )


def session_start(data: object) -> dict:
    _ = data
    return {"additional_context": _session_context()}


def post_tool_use(data: object) -> dict:
    if not isinstance(data, dict):
        return {}
    paths = _paths_from_tool_input(data.get("tool_input"))
    ctx = _post_write_context(paths)
    if not ctx:
        return {}
    return {"additional_context": ctx}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return

    try:
        if mode == "session_start":
            out = session_start(data)
        elif mode == "post_tool_use":
            out = post_tool_use(data)
        else:
            out = {}
        # UTF-8 for Cursor; avoid Windows console cp1252 issues when testing locally
        sys.stdout.buffer.write(
            json.dumps(out, ensure_ascii=False).encode("utf-8") + b"\n"
        )
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
