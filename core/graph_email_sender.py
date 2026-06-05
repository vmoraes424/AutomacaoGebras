"""Envio de e-mail via Microsoft Graph (mesmo padrão do projeto Automação CCEE)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import msal
import requests

from .config import GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID


@dataclass(frozen=True)
class EmailEnvelope:
    sender: str
    recipients: list[str]
    subject: str
    html_body: str


class GraphEmailSender:
    GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]

    def __init__(self) -> None:
        self._token_cache: dict[str, str] = {}

    @staticmethod
    def configurado() -> bool:
        return bool(GRAPH_TENANT_ID and GRAPH_CLIENT_ID and GRAPH_CLIENT_SECRET)

    def _acquire_token(self) -> str:
        if not self.configurado():
            raise RuntimeError(
                "Configuração do Microsoft Graph incompleta. "
                "Defina tenant_id, client_id, client_secret e email no .env."
            )

        authority = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"
        app = msal.ConfidentialClientApplication(
            client_id=GRAPH_CLIENT_ID,
            client_credential=GRAPH_CLIENT_SECRET,
            authority=authority,
        )
        result = app.acquire_token_for_client(scopes=self.GRAPH_SCOPE)
        token = str(result.get("access_token", "") or "")
        if not token:
            error_desc = (
                result.get("error_description")
                or result.get("error")
                or "Falha desconhecida"
            )
            raise RuntimeError(f"Falha ao obter token Microsoft Graph: {error_desc}")
        return token

    @staticmethod
    def _build_payload(envelope: EmailEnvelope) -> dict[str, Any]:
        return {
            "message": {
                "subject": envelope.subject,
                "body": {"contentType": "HTML", "content": envelope.html_body},
                "toRecipients": [
                    {"emailAddress": {"address": recipient}}
                    for recipient in envelope.recipients
                ],
            },
            "saveToSentItems": True,
        }

    def _send_with_token(
        self, sender: str, token: str, payload: dict[str, Any]
    ) -> requests.Response:
        url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        return requests.post(url, headers=headers, json=payload, timeout=30)

    @staticmethod
    def _extract_graph_error(response: requests.Response) -> str:
        try:
            data = response.json()
        except Exception:
            return response.text[:500]
        err = data.get("error") if isinstance(data, dict) else None
        if isinstance(err, dict):
            code = err.get("code", "")
            message = err.get("message", "")
            return f"{code} - {message}".strip(" -")
        return str(data)

    def send(self, envelope: EmailEnvelope) -> None:
        sender = (envelope.sender or "").strip()
        if not sender:
            raise RuntimeError(
                "Remetente não informado para envio via Microsoft Graph."
            )
        if not envelope.recipients:
            raise RuntimeError(
                "Lista de destinatários vazia para envio via Microsoft Graph."
            )

        payload = self._build_payload(envelope)
        token = self._token_cache.get("access_token") or self._acquire_token()
        response = self._send_with_token(sender, token, payload)

        if response.status_code in (401, 403):
            token = self._acquire_token()
            self._token_cache["access_token"] = token
            response = self._send_with_token(sender, token, payload)

        if response.status_code >= 300:
            msg = self._extract_graph_error(response)
            raise RuntimeError(
                f"Falha no envio via Microsoft Graph ({response.status_code}): {msg}"
            )
