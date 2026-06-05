"""Campos set/enum na API v2 do Pipedrive vêm como lista de ids ([91])."""

from __future__ import annotations

from unittest.mock import patch

from core.pipedrive_fields import (
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_GEBRAS,
    FIELD_EMAIL_DIRETOR_GEBRAS,
    get_val,
)
from core.pipedrive_validations import _validar_campo_contrato


def _deal_v2(**custom_fields) -> dict:
    return {"id": 746, "custom_fields": custom_fields}


@patch("core.pipedrive_fields._enum_option_labels_for_field")
def test_get_val_resolve_lista_ids_api_v2(mock_enum_labels):
    mock_enum_labels.side_effect = lambda code: {
        FIELD_EMAIL_COORDENADOR_GEBRAS: {"91": "vinicius.bederode@gebras.com"},
        FIELD_EMAIL_DIRETOR_GEBRAS: {"92": "pedro.terra@gebras.com"},
    }.get(code, {})

    deal = _deal_v2(
        **{
            FIELD_EMAIL_COORDENADOR_GEBRAS: [91],
            FIELD_EMAIL_DIRETOR_GEBRAS: [92],
        }
    )

    assert get_val(deal, FIELD_EMAIL_COORDENADOR_GEBRAS) == "vinicius.bederode@gebras.com"
    assert get_val(deal, FIELD_EMAIL_DIRETOR_GEBRAS) == "pedro.terra@gebras.com"


@patch("core.pipedrive_fields._enum_option_labels_for_field")
def test_validacao_email_aceita_lista_ids_api_v2(mock_enum_labels):
    mock_enum_labels.side_effect = lambda code: {
        FIELD_EMAIL_COORDENADOR_GEBRAS: {"91": "vinicius.bederode@gebras.com"},
        FIELD_EMAIL_DIRETOR_GEBRAS: {"92": "pedro.terra@gebras.com"},
        FIELD_EMAIL_CONSULTOR_GEBRAS: {"89": "pedro.terra@gebras.com"},
    }.get(code, {})

    deal = _deal_v2(
        **{
            FIELD_EMAIL_CONSULTOR_GEBRAS: [89],
            FIELD_EMAIL_COORDENADOR_GEBRAS: [91],
            FIELD_EMAIL_DIRETOR_GEBRAS: [92],
        }
    )

    assert (
        _validar_campo_contrato(
            deal, "E-mail Coordenador GEBRAS", FIELD_EMAIL_COORDENADOR_GEBRAS, "email"
        )
        is None
    )
    assert (
        _validar_campo_contrato(
            deal, "E-mail Diretor GEBRAS", FIELD_EMAIL_DIRETOR_GEBRAS, "email"
        )
        is None
    )
