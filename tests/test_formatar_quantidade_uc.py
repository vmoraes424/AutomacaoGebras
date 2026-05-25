"""Testes: quantidade UC no contrato (só número)."""

from core.pipedrive_fields import formatar_quantidade_uc


def test_inteiro():
    assert formatar_quantidade_uc("4") == "4"
    assert formatar_quantidade_uc(6) == "6"


def test_sem_extenso():
    assert formatar_quantidade_uc("4") == "4"
    assert "quatro" not in formatar_quantidade_uc("4").lower()
