"""Testes: domínio formulário (sem infraestrutura)."""

from __future__ import annotations

from datetime import datetime, timezone

from portal.domain.formulario.entities import DealForm
from portal.domain.formulario.value_objects import FormStatus


def test_deal_form_to_record():
    form = DealForm(
        deal_id=746,
        status=FormStatus.DRAFT,
        schema_version="v1",
        payload={"cliente": {"contratante": "Teste"}},
        owner_user_id=1,
        created_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
    )
    record = form.to_record()
    assert record["deal_id"] == 746
    assert record["status"] == "draft"
    assert record["payload"]["cliente"]["contratante"] == "Teste"


def test_status_snapshot():
    form = DealForm(
        deal_id=100,
        status=FormStatus.DRAFT,
        schema_version="v1",
        payload={},
    )
    snap = form.status_snapshot()
    assert snap["deal_id"] == 100
    assert snap["status"] == "draft"
    assert "payload" not in snap
