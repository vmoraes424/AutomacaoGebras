"""Testes: formatação de data/hora em Brasília."""

from datetime import datetime, timezone

from core.pipedrive_fields import formatar_data_hora_brasilia


def test_utc_para_brasilia():
    # 25/05/2026 13:22:46 UTC = 25/05/2026 10:22:46 em Brasília (UTC-3)
    dt = datetime(2026, 5, 25, 13, 22, 46, tzinfo=timezone.utc)
    assert formatar_data_hora_brasilia(dt) == "25/05/2026 10:22:46"
