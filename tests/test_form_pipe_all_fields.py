"""Garante que todos os campos mapeados do formulário v1 geram PATCH v2 válido no Pipedrive."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from core.form_pipe_sync import (
    PipeSyncError,
    form_field_to_pipe_value,
    form_payload_to_pipe_custom_fields,
    sync_form_field_to_pipedrive,
    sync_form_payload_to_pipedrive,
)
from core.form_schema_v1 import FORM_PATH_TO_PIPE, PIPE_TO_FORM_PATH
from core.pipe_v2_schema import PipeV2SchemaError, validate_pipe_custom_field
from core.pipedrive_fields import (
    DEFAULT_PIPE_CURRENCY,
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_EMAIL_COORDENADOR_GEBRAS,
    FIELD_EMAIL_DIRETOR_GEBRAS,
    FIELD_FILIAL,
    FIELD_PERCENTUAL_EXITO,
    FIELD_REGIONAL,
    FIELD_SUBCENTRO_NIVEL_3,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"

BIVIEW_PIPE_FIELD_OPTIONS = {
    FIELD_FILIAL: {"101": "Iribarrem San Martin"},
    FIELD_REGIONAL: {"102": "Regional1"},
    FIELD_SUBCENTRO_NIVEL_3: {"103": "Alinne de Matos Alves"},
    FIELD_PERCENTUAL_EXITO: {"104": "20%"},
    FIELD_EMAIL_CONSULTOR_GEBRAS: {"201": "vkbederode@gmail.com"},
    FIELD_EMAIL_COORDENADOR_GEBRAS: {"202": "vinicius.bederode@gebras.com"},
    FIELD_EMAIL_DIRETOR_GEBRAS: {"203": "pedro.terra@gebras.com"},
}


def _mock_biview_options(field_code: str) -> dict[str, str]:
    return BIVIEW_PIPE_FIELD_OPTIONS.get(field_code, {})


def _load_payload(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _form_value(payload: dict[str, Any], field_path: str) -> Any:
    section, _, field = field_path.partition(".")
    return payload[section][field]


@pytest.fixture
def biview_payload() -> dict[str, Any]:
    return _load_payload("form_payload_v1_biview_746.json")


@pytest.fixture
def g1_payload() -> dict[str, Any]:
    return _load_payload("form_payload_v1_g1.json")


@pytest.fixture
def mock_pipe_options():
    with patch(
        "core.pipedrive_fields._enum_option_labels_for_field",
        side_effect=_mock_biview_options,
    ):
        yield


ALL_MAPPED_PATHS = list(FORM_PATH_TO_PIPE.keys())


@pytest.mark.parametrize("field_path", ALL_MAPPED_PATHS, ids=ALL_MAPPED_PATHS)
def test_campo_individual_formato_v2_biview(
    field_path: str,
    biview_payload: dict[str, Any],
    mock_pipe_options,
):
    """Cada campo do deal 746 (Biview) → tipo aceito pelo Pipedrive v2."""
    pipe_hash = FORM_PATH_TO_PIPE[field_path]
    raw = _form_value(biview_payload, field_path)
    converted = form_field_to_pipe_value(pipe_hash, field_path, raw)
    validate_pipe_custom_field(pipe_hash, converted, field_path=field_path)


@pytest.mark.parametrize("field_path", ALL_MAPPED_PATHS, ids=ALL_MAPPED_PATHS)
def test_sync_campo_individual_patch_biview(
    field_path: str,
    biview_payload: dict[str, Any],
    mock_pipe_options,
):
    """Blur/sync de cada campo envia PATCH com valor v2 válido."""
    raw = _form_value(biview_payload, field_path)
    with patch("core.form_pipe_sync.requests.patch") as mock_patch:
        mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
        sync_form_field_to_pipedrive(746, field_path, raw)

    body = mock_patch.call_args.kwargs["json"]
    assert "custom_fields" in body
    pipe_hash = FORM_PATH_TO_PIPE[field_path]
    assert pipe_hash in body["custom_fields"]
    validate_pipe_custom_field(
        pipe_hash,
        body["custom_fields"][pipe_hash],
        field_path=field_path,
    )


def test_payload_completo_todos_campos_v2_biview(biview_payload, mock_pipe_options):
    """Sync completo do formulário Biview — todos os custom_fields válidos."""
    cf = form_payload_to_pipe_custom_fields(746, biview_payload)
    assert len(cf) == len(FORM_PATH_TO_PIPE)

    for field_path, pipe_hash in FORM_PATH_TO_PIPE.items():
        assert pipe_hash in cf, f"ausente no PATCH: {field_path}"
        validate_pipe_custom_field(pipe_hash, cf[pipe_hash], field_path=field_path)


@patch("core.form_pipe_sync.requests.patch")
def test_sync_completo_nao_dispara_400_schema(mock_patch, biview_payload, mock_pipe_options):
    mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
    sync_form_payload_to_pipedrive(746, biview_payload)
    mock_patch.assert_called_once()
    body = mock_patch.call_args.kwargs["json"]
    for pipe_hash, value in body["custom_fields"].items():
        validate_pipe_custom_field(
            pipe_hash,
            value,
            field_path=PIPE_TO_FORM_PATH.get(pipe_hash, ""),
        )


def test_payload_g1_golden_tambem_valido(g1_payload):
    g1_options = {
        FIELD_FILIAL: {"1": "Matriz"},
        FIELD_REGIONAL: {"2": "Sul"},
        FIELD_SUBCENTRO_NIVEL_3: {"3": "Consultor Teste"},
        FIELD_PERCENTUAL_EXITO: {"4": "15%"},
        FIELD_EMAIL_CONSULTOR_GEBRAS: {"10": "consultor@gebras.com.br"},
        FIELD_EMAIL_COORDENADOR_GEBRAS: {"11": "coordenador@gebras.com.br"},
        FIELD_EMAIL_DIRETOR_GEBRAS: {"12": "diretor@gebras.com.br"},
    }

    def _g1(field_code: str) -> dict[str, str]:
        return g1_options.get(field_code, {})

    with patch(
        "core.pipedrive_fields._enum_option_labels_for_field",
        side_effect=_g1,
    ):
        cf = form_payload_to_pipe_custom_fields(999001, g1_payload)

    for field_path, pipe_hash in FORM_PATH_TO_PIPE.items():
        validate_pipe_custom_field(pipe_hash, cf[pipe_hash], field_path=field_path)


@pytest.mark.parametrize(
    "field_path,bad_value,match",
    [
        ("servicos.gestao_qualidade_energia", "9", "deve ser int"),
        ("valores.valor_recorrencia", "1805", "deve ser objeto"),
        ("cliente.municipio_estado", "Pelotas", "deve ser objeto"),
    ],
)
def test_validador_rejeita_formato_v1_legado(field_path, bad_value, match):
    """Documenta erros que a API v2 retornava antes das conversões."""
    pipe_hash = FORM_PATH_TO_PIPE[field_path]
    with pytest.raises(PipeV2SchemaError, match=match):
        validate_pipe_custom_field(pipe_hash, bad_value, field_path=field_path)


def test_servico_string_do_input_converte_para_int_no_patch(mock_pipe_options):
    """Frontend pode enviar '9' como string; PATCH deve levar int."""
    from core.pipedrive_fields import FIELD_QTD_SOLE

    with patch("core.form_pipe_sync.requests.patch") as mock_patch:
        mock_patch.return_value = MagicMock(ok=True, status_code=200, text="{}")
        sync_form_field_to_pipedrive(746, "servicos.sole_web", "4")

    valor = mock_patch.call_args.kwargs["json"]["custom_fields"][FIELD_QTD_SOLE]
    assert valor == 4
    assert type(valor) is int


def test_amostras_esperadas_biview(biview_payload, mock_pipe_options):
    """Sanity check de valores convertidos (regressão rápida)."""
    cf = form_payload_to_pipe_custom_fields(746, biview_payload)

    from core.pipedrive_fields import (
        FIELD_CIDADE,
        FIELD_INDICADORES_QUALIDADE,
        FIELD_VALOR_MENSAL,
    )

    assert cf[FIELD_INDICADORES_QUALIDADE] == 9
    assert cf[FIELD_VALOR_MENSAL] == {
        "value": 7878.78,
        "currency": DEFAULT_PIPE_CURRENCY,
    }
    assert cf[FIELD_CIDADE] == {"value": "Pelotas - RS, Brasil"}
