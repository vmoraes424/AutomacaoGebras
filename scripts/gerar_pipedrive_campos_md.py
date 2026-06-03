"""Gera docs/Pipedrive/Pipedrive-campos-hashes.md a partir da API v2 dealFields."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "Pipedrive" / "Pipedrive-campos-hashes.md"

AUTOMACAO = {
    "14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b": "FIELD_NUMERO_CONTRATO_P1",
    "41a3157128d51e2fc803eeec4b242efafcb55b4e": "FIELD_NUMERO_CONTRATO_P2",
    "28d491e0263008b437e28fc55bbad8302c4646c8": "FIELD_NOME_CLIENTE",
    "81566ac6e038bb0ba3adfa122c798b3e497b7538": "FIELD_ENDERECO",
    "6d3373f7ee86c7d2449824136baf3ee1938a8ef1": "FIELD_CEP -> CEPPrincipal / ClienteCep",
    "2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5": "FIELD_CIDADE",
    "176d2a0d5167d1edc9b949c75f8b9a7597eabe91": "FIELD_DOCUMENTO",
    "f9923cdce1274da8c10cec1b9ab561e024504620": "FIELD_QTD_SOLE",
    "2a331c4b62c9d46aae9451af25eca2d08a3fdf0a": "FIELD_VALOR_MENSAL",
    "015407d5106c321a227f1ca881f920fe2e1042ec": "FIELD_VALOR_IMPLANTACAO",
    "f40caca58878f19aefba960b87127753b7b932ca": "FIELD_INSCRICAO_MUNICIPAL",
    "2b8f62a107891e26390459cfa4048b3eedade11b": "FIELD_DATA_PAGAMENTO_IMPLANTACAO / FIELD_DATA_IMPLANTACAO",
    "f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2": "FIELD_DATA_PRIMEIRA_COBRANCA",
    "ffb2d5aec9acdee5a242ca19683bbf4caa24cd53": "FIELD_INDICADORES_QUALIDADE (Gestão da Qualidade de Energia)",
    "8f998d4877d478b3905c126d8b23f205d0686b77": "FIELD_GESTAO_ACL",
    "1ba1794470354856aaca3e784349cd5f9f4d074e": "FIELD_GESTAO_USINA_FOTOVOLTAICA",
    "c0a23912d889e00f51ed5bd08a55856a7e5dc930": "FIELD_QUALIDADE_ENERGIA (Sole Consultoria)",
    "c6d1c300a1d070c1a54494a246f6330beabe36aa": "FIELD_QUANTIDADE_UCS",
    "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b": "FIELD_CONTATO_GESTOR / SIGNER: Gestor Gebras",
    "722da69afe31c1f8fa4f5457a223e2a952ae0978": "FIELD_CONTATO_FINANCEIRO",
    "3002b2df87f0577585ebaec394fd09a38ca8778f": "FIELD_CONTATO_CONTRATANTE",
    "14855b5973f28e97dafd4e2abccc539d7461dc24": "FIELD_REGIONAL (Sub Centro Nível 2)",
    "60ffe8e9c2aa51f717865559e86e6044bfb335e6": "FIELD_SUBCENTRO_NIVEL_3 -> SubCentroCusto3Id",
    "c3e623cfa197040b778400a8977ae2c8a8386024": "FIELD_INSCRICAO_ESTADUAL -> inscricao_estadual (contrato)",
    "225005fe8384d97183e5480781ea8ea82982301e": "FIELD_PERCENTUAL_EXITO -> percentual_exito (contrato)",
    "4fba2f9323c64acdcac770e38f2c0cdb840796bc": "FIELD_OBSERVACOES_DETALHES (opcional)",
    "be20f11317ac66845bf97695f43e57795e26d01d": "FIELD_FILIAL -> BranchId Plune",
    "92359b129485b08fd024b8c28ef022e7635419a3": "SIGNER: Coordenador Principal",
    "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6": "SIGNER: Contato Principal",
    "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2": "SIGNER: Diretor Principal",
}


def load_token() -> str:
    sys.path.insert(0, str(ROOT))
    from core.config import PIPEDRIVE_API_TOKEN

    if not PIPEDRIVE_API_TOKEN:
        raise RuntimeError("PIPEDRIVE_API_TOKEN não configurado no .env")
    return PIPEDRIVE_API_TOKEN


def fetch_deal_fields(token: str) -> list[dict]:
    headers = {"x-api-token": token}
    all_fields: list[dict] = []
    cursor = None
    while True:
        params: dict = {"limit": 500}
        if cursor:
            params["cursor"] = cursor
        response = requests.get(
            "https://api.pipedrive.com/api/v2/dealFields",
            headers=headers,
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        body = response.json()
        all_fields.extend(body.get("data") or [])
        cursor = (body.get("additional_data") or {}).get("next_cursor")
        if not cursor:
            break
    return all_fields


def esc_md(text: str) -> str:
    return (text or "").replace("|", "\\|")


def build_markdown(fields: list[dict]) -> str:
    fields.sort(
        key=lambda f: (not f.get("is_custom_field", False), (f.get("field_name") or "").lower())
    )
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    custom_only = [f for f in fields if f.get("is_custom_field")]

    lines = [
        "# Campos Pipedrive (Deals) — hashes e nomes",
        "",
        f"Gerado em **{now}** via `GET /api/v2/dealFields`. Total: **{len(fields)}** campos.",
        "",
        "Fonte: API Pipedrive v2. Campos usados pela automação estão marcados na coluna *Uso no código*.",
        "",
        "## Índice",
        "",
        "- [Todos os campos](#todos-os-campos)",
        "- [Somente custom fields](#somente-custom-fields)",
        "- [Usados pela automação](#usados-pela-automação)",
        "",
        "## Todos os campos",
        "",
        "| Nome do campo | Hash (`field_code`) | Tipo | Custom | Uso no código |",
        "|---|---|---|---|---|",
    ]

    for field in fields:
        name = esc_md(field.get("field_name") or "")
        code = str(field.get("field_code") or "")
        ftype = str(field.get("field_type") or "")
        custom = "Sim" if field.get("is_custom_field") else "Não"
        uso = AUTOMACAO.get(code, "")
        lines.append(f"| {name} | `{code}` | {ftype} | {custom} | {uso} |")

    lines.extend(
        [
            "",
            "## Somente custom fields",
            "",
            f"Total: **{len(custom_only)}** campos customizados.",
            "",
            "| Nome do campo | Hash (`field_code`) | Tipo | Uso no código |",
            "|---|---|---|---|",
        ]
    )

    for field in custom_only:
        name = esc_md(field.get("field_name") or "")
        code = str(field.get("field_code") or "")
        ftype = str(field.get("field_type") or "")
        uso = AUTOMACAO.get(code, "")
        lines.append(f"| {name} | `{code}` | {ftype} | {uso} |")

    lines.extend(
        [
            "",
            "## Usados pela automação",
            "",
            "Definidos em `core/pipedrive_fields.py`.",
            "",
            "| Nome no Pipedrive | Hash | Constante / papel |",
            "|---|---|---|",
        ]
    )

    for field in fields:
        code = str(field.get("field_code") or "")
        if code in AUTOMACAO:
            name = esc_md(field.get("field_name") or "")
            lines.append(f"| {name} | `{code}` | {AUTOMACAO[code]} |")

    return "\n".join(lines) + "\n"


def main() -> None:
    token = load_token()
    fields = fetch_deal_fields(token)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(build_markdown(fields), encoding="utf-8")
    print(f"Escrito: {OUT_PATH} ({len(fields)} campos)")


if __name__ == "__main__":
    main()
