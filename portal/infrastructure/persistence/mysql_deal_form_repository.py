from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from copy import deepcopy
from typing import Any

from core.database import DbConnection, db_conn
from portal.domain.formulario.entities import DealForm
from portal.infrastructure.persistence.deal_form_mapper import row_to_deal_form, utc_now_iso
from portal.infrastructure.persistence.deal_form_rules import build_draft, build_submit


class MysqlDealFormRepository:
    """Persistência MySQL em `deal_forms` (gebras_automacao)."""

    def __init__(
        self,
        conn_factory: Callable[[], AbstractContextManager[DbConnection]] | None = None,
    ) -> None:
        self._conn_factory = conn_factory or db_conn

    def list_form_status_by_deal_ids(
        self, deal_ids: list[int], *, schema_version: str = "v1"
    ) -> dict[int, str]:
        if not deal_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(deal_ids))
        params: list = [*deal_ids, schema_version]
        with self._conn_factory() as conn:
            rows = conn.execute(
                f"""
                SELECT deal_id, status FROM deal_forms
                WHERE deal_id IN ({placeholders}) AND schema_version = %s
                """,
                tuple(params),
            ).fetchall()
        return {int(row["deal_id"]): str(row["status"]) for row in rows}

    def get_by_deal_id(
        self, deal_id: int, *, schema_version: str = "v1"
    ) -> DealForm | None:
        with self._conn_factory() as conn:
            row = conn.execute(
                """
                SELECT deal_id, schema_version, owner_user_id, owner_name, deal_title,
                       status, payload_json, validation_errors_json,
                       created_at, updated_at, submitted_at
                FROM deal_forms
                WHERE deal_id = %s AND schema_version = %s
                """,
                (deal_id, schema_version),
            ).fetchone()
        return row_to_deal_form(row) if row else None

    def save_draft(
        self,
        deal_id: int,
        *,
        payload: dict[str, Any],
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
    ) -> DealForm:
        existing = self.get_by_deal_id(deal_id, schema_version=schema_version)
        form = build_draft(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            existing=existing,
        )
        self._upsert(form)
        return deepcopy(form)

    def submit(
        self,
        deal_id: int,
        *,
        payload: dict[str, Any],
        schema_version: str,
        owner_user_id: int | None,
        owner_name: str,
        deal_title: str,
        validation_errors: dict | None = None,
    ) -> DealForm:
        existing = self.get_by_deal_id(deal_id, schema_version=schema_version)
        form = build_submit(
            deal_id,
            payload=payload,
            schema_version=schema_version,
            owner_user_id=owner_user_id,
            owner_name=owner_name,
            deal_title=deal_title,
            existing=existing,
            validation_errors=validation_errors,
        )
        self._upsert(form)
        return deepcopy(form)

    def _upsert(self, form: DealForm) -> None:
        created = form.created_at.isoformat() if form.created_at else utc_now_iso()
        updated = form.updated_at.isoformat() if form.updated_at else utc_now_iso()
        submitted = form.submitted_at.isoformat() if form.submitted_at else None
        errors_json = json.dumps(form.validation_errors) if form.validation_errors else None

        with self._conn_factory() as conn:
            conn.execute(
                """
                INSERT INTO deal_forms (
                    deal_id, schema_version, owner_user_id, owner_name, deal_title,
                    status, payload_json, validation_errors_json,
                    created_at, updated_at, submitted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    owner_user_id = VALUES(owner_user_id),
                    owner_name = VALUES(owner_name),
                    deal_title = VALUES(deal_title),
                    status = VALUES(status),
                    payload_json = VALUES(payload_json),
                    validation_errors_json = VALUES(validation_errors_json),
                    updated_at = VALUES(updated_at),
                    submitted_at = VALUES(submitted_at)
                """,
                (
                    form.deal_id,
                    form.schema_version,
                    form.owner_user_id,
                    form.owner_name,
                    form.deal_title,
                    str(form.status),
                    json.dumps(form.payload, ensure_ascii=False),
                    errors_json,
                    created,
                    updated,
                    submitted,
                ),
            )
