"""Testes: casos de uso formulário com repositório em memória."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from portal.application.formulario.get_deal_form import GetDealForm
from portal.application.formulario.save_draft import SaveDealFormDraft
from portal.application.formulario.submit import SubmitDealForm
from portal.domain.formulario.exceptions import (
    DealFormNotEditableError,
    DealFormNotFoundError,
)
from portal.domain.formulario.value_objects import FormStatus
from portal.infrastructure.persistence.memory_deal_form_repository import (
    MemoryDealFormRepository,
)


@pytest.fixture
def repo():
    r = MemoryDealFormRepository()
    yield r
    r.clear()


def test_save_and_get_draft_use_case(repo):
    save = SaveDealFormDraft(repo)
    get = GetDealForm(repo)

    save.execute(746, payload={"a": 1}, schema_version="v1")
    form = get.execute(746)
    assert form.payload == {"a": 1}
    assert form.status.value == "draft"


def test_get_raises_when_missing(repo):
    with pytest.raises(DealFormNotFoundError):
        GetDealForm(repo).execute(999)


@patch("core.form_pipe_sync.push_form_to_pipedrive")
def test_submit_after_draft(_sync, repo):
    save = SaveDealFormDraft(repo)
    submit = SubmitDealForm(repo)
    save.execute(746, payload={"a": 1})
    form = submit.execute(746, payload={"a": 1})
    assert form.status == FormStatus.VALIDATED


@patch("core.form_pipe_sync.push_form_to_pipedrive")
def test_draft_blocked_after_submit(_sync, repo):
    SubmitDealForm(repo).execute(746, payload={"a": 1})
    with pytest.raises(DealFormNotEditableError):
        SaveDealFormDraft(repo).execute(746, payload={"b": 2})
