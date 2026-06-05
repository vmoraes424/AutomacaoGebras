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

        assert [s["papel"] for s in seq] == [
            "Consultor",
            "Coordenador",
            "Cliente",
            "Diretor",
        ]
        assert [s["name"] for s in seq] == [
            "Gestor Gebras",
            "Coordenador Principal",
            "Contato Principal",
            "Diretor Principal",
        ]
        assert [s["group"] for s in seq] == [1, 2, 3, 4]
        assert seq[0]["email"] == "consultor@gebras.com"
        assert not any(s["papel"] == "Comercial" for s in seq)

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

        emails = {s["papel"]: s["email"] for s in seq}
        assert emails["Consultor"] == "gestor@gebras.com"
        assert emails["Coordenador"] == "coord@gebras.com"
        assert "Diretor" not in emails
        assert "Comercial" not in emails

    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_multiplos_emails_em_todos_os_grupos(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {
                "84": "consultor1@gebras.com",
                "85": "consultor2@gebras.com",
            },
            FIELD_EMAIL_COORDENADOR_GEBRAS: {
                "81": "coord1@gebras.com",
                "82": "coord2@gebras.com",
            },
            FIELD_EMAIL_DIRETOR_GEBRAS: {
                "80": "diretor1@gebras.com",
                "83": "diretor2@gebras.com",
            },
        }.get(code, {})

        seq = extrair_signatarios(
            _deal(
                **{
                    FIELD_EMAIL_CONSULTOR_GEBRAS: ["84", "85"],
                    FIELD_EMAIL_COORDENADOR_GEBRAS: ["81", "82"],
                    FIELD_CONTATO_PRINCIPAL: "cliente1@example.com,cliente2@example.com",
                    FIELD_EMAIL_DIRETOR_GEBRAS: ["80", "83"],
                }
            )
        )

        assert [s["name"] for s in seq] == [
            "Gestor Gebras",
            "Gestor Gebras 2",
            "Coordenador Principal",
            "Coordenador Principal 2",
            "Contato Principal",
            "Contato Principal 2",
            "Diretor Principal",
            "Diretor Principal 2",
        ]
        assert [s["group"] for s in seq] == [1, 1, 2, 2, 3, 3, 4, 4]

    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_dois_consultores_no_grupo_1(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {
                "84": "vkbederode@gmail.com",
                "85": "pedro.terra@gebras.com",
            },
        }.get(code, {})

        seq = extrair_signatarios(
            _deal(**{FIELD_EMAIL_CONSULTOR_GEBRAS: ["84", "85"]})
        )

        consultores = [s for s in seq if s["group"] == 1]
        assert len(consultores) == 2
        assert [s["email"] for s in consultores] == [
            "vkbederode@gmail.com",
            "pedro.terra@gebras.com",
        ]
        assert [s["papel"] for s in consultores] == ["Consultor", "Consultor 2"]
        assert [s["name"] for s in consultores] == ["Gestor Gebras", "Gestor Gebras 2"]

    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_deduplica_email_repetido(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {"84": "mesmo@gebras.com"},
        }.get(code, {})

        seq = extrair_signatarios(
            _deal(**{FIELD_EMAIL_CONSULTOR_GEBRAS: "84"})
        )

        assert len(seq) == 1
        assert seq[0]["papel"] == "Consultor"
        assert seq[0]["name"] == "Gestor Gebras"


class TestSignatariosOmitidos:
    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_diretor_omitido_mesmo_email_consultor(self, mock_enum_labels):
        from core.pipedrive_fields import (
            FIELD_EMAIL_CONSULTOR_GEBRAS,
            signatarios_omitidos_por_email_duplicado,
        )

        mock_enum_labels.return_value = {}
        deal = _deal(
            **{
                FIELD_EMAIL_CONSULTOR_GEBRAS: "pedro.terra@gebras.com",
                FIELD_EMAIL_COORDENADOR_GEBRAS: "coord@gebras.com",
                FIELD_CONTATO_PRINCIPAL: "cliente@example.com",
                FIELD_EMAIL_DIRETOR_GEBRAS: "pedro.terra@gebras.com",
            }
        )
        seq = extrair_signatarios(deal)
        omitidos = signatarios_omitidos_por_email_duplicado(deal, seq)

        assert [s["papel"] for s in seq] == ["Consultor", "Coordenador", "Cliente"]
        assert len(omitidos) == 1
        assert omitidos[0]["papel"] == "Diretor"
        assert omitidos[0]["email"] == "pedro.terra@gebras.com"
