"""Testes: persistência deal_forms (memória + MySQL mockado)."""

from __future__ import annotations

import json
from contextlib import contextmanager
from unittest.mock import patch
from datetime import datetime, timezone
from typing import Any

import pytest

from portal.application.formulario.submit import SubmitDealForm
from portal.domain.formulario.exceptions import DealFormNotEditableError
from portal.domain.formulario.value_objects import FormStatus
from portal.infrastructure.persistence.memory_deal_form_repository import (
    MemoryDealFormRepository,
)
from portal.infrastructure.persistence.mysql_deal_form_repository import (
    MysqlDealFormRepository,
)


class _FakeExecuteResult:
    def __init__(self, row: dict | None = None, rows: list | None = None):
        self._row = row
        self._rows = rows or []

    def fetchone(self):
        return self._row

    def fetchall(self):
        return self._rows


class FakeDbConnection:
    def __init__(self) -> None:
        self.rows: dict[tuple[int, str], dict[str, Any]] = {}
        self.executed: list[tuple[str, tuple | None]] = []

    def execute(self, sql: str, params: tuple | list | None = None) -> _FakeExecuteResult:
        self.executed.append((sql, params))
        normalized = " ".join(sql.split())
        if normalized.startswith("SELECT") and params:
            deal_id, schema_version = params
            row = self.rows.get((deal_id, schema_version))
            return _FakeExecuteResult(row=row)
        if normalized.startswith("INSERT") and params:
            (
                deal_id,
                schema_version,
                owner_user_id,
                owner_name,
                deal_title,
                status,
                payload_json,
                validation_errors_json,
                created_at,
                updated_at,
                submitted_at,
            ) = params
            self.rows[(deal_id, schema_version)] = {
                "deal_id": deal_id,
                "schema_version": schema_version,
                "owner_user_id": owner_user_id,
                "owner_name": owner_name,
                "deal_title": deal_title,
                "status": status,
                "payload_json": payload_json,
                "validation_errors_json": validation_errors_json,
                "created_at": created_at,
                "updated_at": updated_at,
                "submitted_at": submitted_at,
            }
        return _FakeExecuteResult()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass


@pytest.fixture
def memory_repo():
    repo = MemoryDealFormRepository()
    yield repo
    repo.clear()


@pytest.fixture
def mysql_repo():
    fake = FakeDbConnection()

    @contextmanager
    def conn_factory():
        yield fake  # type: ignore[misc]

    repo = MysqlDealFormRepository(conn_factory=conn_factory)
    return repo, fake


def test_memory_insert_update_draft(memory_repo, form_payload_v1_minimo):
    memory_repo.save_draft(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=1,
        owner_name="A",
        deal_title="Deal",
    )
    updated = {**form_payload_v1_minimo, "cliente": {"contratante": "Novo"}}
    form = memory_repo.save_draft(
        746,
        payload=updated,
        schema_version="v1",
        owner_user_id=1,
        owner_name="A",
        deal_title="Deal",
    )
    assert form.status == FormStatus.DRAFT
    assert form.payload["cliente"]["contratante"] == "Novo"
    assert form.created_at is not None
    assert form.updated_at is not None


def test_memory_submit_draft_to_validated(memory_repo, form_payload_v1_minimo):
    memory_repo.save_draft(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
    )
    submitted = memory_repo.submit(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
        validation_errors=None,
    )
    assert submitted.status == FormStatus.VALIDATED
    assert submitted.submitted_at is not None


def test_memory_block_edit_after_submit(memory_repo, form_payload_v1_minimo):
    memory_repo.submit(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
    )
    with pytest.raises(DealFormNotEditableError):
        memory_repo.save_draft(
            746,
            payload={"x": 1},
            schema_version="v1",
            owner_user_id=None,
            owner_name="",
            deal_title="",
        )


def test_memory_error_status_allows_new_draft(memory_repo, form_payload_v1_minimo):
    memory_repo.submit(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
        validation_errors={"campo": "erro"},
    )
    fixed = memory_repo.save_draft(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
    )
    assert fixed.status == FormStatus.DRAFT


def test_memory_validation_errors_persisted(memory_repo, form_payload_v1_minimo):
    errors = {"signatarios.email_diretor_gebras": "obrigatório"}
    form = memory_repo.submit(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
        validation_errors=errors,
    )
    assert form.status == FormStatus.ERROR
    assert form.validation_errors == errors
    assert form.submitted_at is None
    loaded = memory_repo.get_by_deal_id(746)
    assert loaded is not None
    assert loaded.validation_errors == errors


def test_memory_uniqueness_deal_id_schema_version(memory_repo, form_payload_v1_minimo):
    memory_repo.save_draft(
        746,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=None,
        owner_name="",
        deal_title="",
    )
    memory_repo.save_draft(
        746,
        payload={"v2": True},
        schema_version="v2",
        owner_user_id=None,
        owner_name="",
        deal_title="",
    )
    assert memory_repo.get_by_deal_id(746, schema_version="v1") is not None
    assert memory_repo.get_by_deal_id(746, schema_version="v2") is not None


@patch("core.form_pipe_sync.push_form_to_pipedrive")
def test_submit_use_case_with_validator(
    _sync, memory_repo, form_payload_v1_minimo, eligible_pipe_deal
):
    def validator(deal_id, payload):
        if not payload.get("cliente", {}).get("documento"):
            return {"cliente.documento": "obrigatório"}
        return {}

    use_case = SubmitDealForm(memory_repo, validator=validator)
    bad = use_case.execute(746, payload={"cliente": {}})
    assert bad.status == FormStatus.ERROR

    good = use_case.execute(746, payload=form_payload_v1_minimo)
    assert good.status == FormStatus.VALIDATED


def test_mysql_repo_upsert_and_load(mysql_repo, form_payload_v1_minimo):
    repo, fake = mysql_repo
    repo.save_draft(
        100,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=5,
        owner_name="Nome",
        deal_title="Título",
    )
    assert (100, "v1") in fake.rows
    loaded = repo.get_by_deal_id(100)
    assert loaded is not None
    assert loaded.deal_id == 100
    assert loaded.payload["cliente"]["contratante"] == "Cliente Teste Ltda"

    repo.submit(
        100,
        payload=form_payload_v1_minimo,
        schema_version="v1",
        owner_user_id=5,
        owner_name="Nome",
        deal_title="Título",
        validation_errors={"campo": "erro"},
    )
    row = fake.rows[(100, "v1")]
    assert row["status"] == "error"
    errors = row["validation_errors_json"]
    if isinstance(errors, str):
        errors = json.loads(errors)
    assert errors == {"campo": "erro"}
