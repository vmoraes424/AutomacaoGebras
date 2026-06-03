"""Testes: ordem e grupos de signatários Clicksign."""

from __future__ import annotations

from unittest.mock import patch

from core.pipedrive_fields import (
    FIELD_CONTATO_GESTOR,
    FIELD_CONTATO_PRINCIPAL,
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_LEGADO,
    FIELD_EMAIL_DIRETOR_GEBRAS,
    extrair_signatarios,
)


def _deal(**custom_fields) -> dict:
    return {"id": 746, "custom_fields": custom_fields}


class TestExtrairSignatarios:
    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_ordem_e_grupos_completa(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {"84": "consultor@gebras.com"},
            FIELD_EMAIL_COORDENADOR_GEBRAS: {"81": "coordenador@gebras.com"},
            FIELD_EMAIL_DIRETOR_GEBRAS: {"80": "diretor@gebras.com"},
        }.get(code, {})

        seq = extrair_signatarios(
            _deal(
                **{
                    FIELD_EMAIL_CONSULTOR_GEBRAS: "84",
                    FIELD_EMAIL_COORDENADOR_GEBRAS: "81",
                    FIELD_CONTATO_PRINCIPAL: "cliente@example.com",
                    FIELD_EMAIL_DIRETOR_GEBRAS: "80",
                }
            )
        )

        assert [s["name"] for s in seq] == [
            "Consultor",
            "Coordenador",
            "Cliente",
            "Diretor",
        ]
        assert [s["group"] for s in seq] == [1, 2, 3, 4]
        assert seq[0]["email"] == "consultor@gebras.com"
        assert not any(s["name"] == "Comercial" for s in seq)

    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_fallback_hashes_legados(self, mock_enum_labels):
        mock_enum_labels.return_value = {}

        seq = extrair_signatarios(
            _deal(
                **{
                    FIELD_CONTATO_GESTOR: "gestor@gebras.com",
                    FIELD_EMAIL_COORDENADOR_LEGADO: "coord@gebras.com",
                    FIELD_CONTATO_PRINCIPAL: "cliente@example.com",
                }
            )
        )

        emails = {s["name"]: s["email"] for s in seq}
        assert emails["Consultor"] == "gestor@gebras.com"
        assert emails["Coordenador"] == "coord@gebras.com"
        assert "Diretor" not in emails
        assert "Comercial" not in emails

    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_deduplica_email_repetido(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {"84": "mesmo@gebras.com"},
        }.get(code, {})

        seq = extrair_signatarios(
            _deal(**{FIELD_EMAIL_CONSULTOR_GEBRAS: "84"})
        )

        assert len(seq) == 1
        assert seq[0]["name"] == "Consultor"
