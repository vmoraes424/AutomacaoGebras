"""Testes: exceções Plune."""

from __future__ import annotations

import pytest

from core.plune_errors import PluneApiError, PluneError


def test_plune_api_error_raw():
    err = PluneApiError("falha", "ERR_123")
    assert isinstance(err, PluneError)
    assert err.raw_error == "ERR_123"
    assert "falha" in str(err)


def test_plune_api_error_default_raw():
    err = PluneApiError("só mensagem")
    assert err.raw_error == "só mensagem"
