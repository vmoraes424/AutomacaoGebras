"""Compara hashes em core/pipedrive_fields.py com GET /api/v2/dealFields."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import pipedrive_fields as pf
from scripts.gerar_pipedrive_campos_md import fetch_deal_fields, load_token

CONSTANTES = {
    "FIELD_NUMERO_CONTRATO_P1": pf.FIELD_NUMERO_CONTRATO_P1,
    "FIELD_NUMERO_CONTRATO_P2": pf.FIELD_NUMERO_CONTRATO_P2,
    "FIELD_NOME_CLIENTE": pf.FIELD_NOME_CLIENTE,
    "FIELD_ENDERECO": pf.FIELD_ENDERECO,
    "FIELD_CEP": pf.FIELD_CEP,
    "FIELD_CIDADE": pf.FIELD_CIDADE,
    "FIELD_DOCUMENTO": pf.FIELD_DOCUMENTO,
    "FIELD_QTD_SOLE": pf.FIELD_QTD_SOLE,
    "FIELD_VALOR_MENSAL": pf.FIELD_VALOR_MENSAL,
    "FIELD_VALOR_IMPLANTACAO": pf.FIELD_VALOR_IMPLANTACAO,
    "FIELD_DATA_IMPLANTACAO": pf.FIELD_DATA_IMPLANTACAO,
    "FIELD_DATA_PRIMEIRA_COBRANCA": pf.FIELD_DATA_PRIMEIRA_COBRANCA,
    "FIELD_INDICADORES_QUALIDADE": pf.FIELD_INDICADORES_QUALIDADE,
    "FIELD_QUALIDADE_ENERGIA": pf.FIELD_QUALIDADE_ENERGIA,
    "FIELD_GESTAO_ACL": pf.FIELD_GESTAO_ACL,
    "FIELD_GESTAO_USINA_FOTOVOLTAICA": pf.FIELD_GESTAO_USINA_FOTOVOLTAICA,
    "FIELD_CONTATO_GESTOR": pf.FIELD_CONTATO_GESTOR,
    "FIELD_CONTATO_FINANCEIRO": pf.FIELD_CONTATO_FINANCEIRO,
    "FIELD_CONTATO_CONTRATANTE": pf.FIELD_CONTATO_CONTRATANTE,
    "FIELD_REGIONAL": pf.FIELD_REGIONAL,
    "FIELD_SUBCENTRO_NIVEL_3": pf.FIELD_SUBCENTRO_NIVEL_3,
    "FIELD_FILIAL": pf.FIELD_FILIAL,
}

SIGNERS = {
    "SIGNER_COORDENADOR": pf.SIGNER_FIELDS[0][1],
    "SIGNER_CONTATO": pf.SIGNER_FIELDS[1][1],
    "SIGNER_GESTOR_GEBRAS": pf.SIGNER_FIELDS[2][1],
    "SIGNER_DIRETOR": pf.SIGNER_FIELDS[3][1],
}


def main() -> None:
    by_code = {
        str(f.get("field_code")): f.get("field_name")
        for f in fetch_deal_fields(load_token())
    }

    ok = 0
    fail = 0
    print("=== Hashes da automação vs API Pipedrive ===\n")
    for nome, hashv in {**CONSTANTES, **SIGNERS}.items():
        api_nome = by_code.get(hashv)
        if api_nome:
            print(f"OK  {nome:30} -> {api_nome}")
            ok += 1
        else:
            print(f"ERRO {nome:30} -> hash {hashv} NÃO existe na API")
            fail += 1

    print(f"\n{ok} OK, {fail} com problema.")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
