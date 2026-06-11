"""Benchmark CRM endpoints — Pipe direto vs portal (deal 746)."""

from __future__ import annotations

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("PIPEDRIVE_API_TOKEN", "").strip()
if not TOKEN:
    sys.exit("PIPEDRIVE_API_TOKEN missing")

H = {"x-api-token": TOKEN}
V2 = "https://api.pipedrive.com/api/v2"
PORTAL = os.environ.get("PORTAL_BASE", "http://localhost:8000")
DEAL_ID = int(os.environ.get("BENCH_DEAL_ID", "746"))
BUDGET_MS = float(os.environ.get("BENCH_BUDGET_MS", "2000"))


def ms_since(t0: float) -> float:
    return (time.perf_counter() - t0) * 1000


def flag(ms: float) -> str:
    return "OK" if ms <= BUDGET_MS else "SLOW"


def bench_pipe(label: str, fn) -> dict:
    t0 = time.perf_counter()
    result = fn()
    elapsed = ms_since(t0)
    print(f"  [pipe] {label}: {elapsed:.0f}ms [{flag(elapsed)}]")
    return {"label": label, "ms": elapsed, "result": result}


def bench_portal(path: str, headers: dict | None = None) -> dict:
    t0 = time.perf_counter()
    r = requests.get(f"{PORTAL}{path}", headers=headers or {}, timeout=120)
    elapsed = ms_since(t0)
    n = len(r.json()) if r.ok and r.headers.get("content-type", "").startswith("application/json") else 0
    print(f"  [portal] GET {path}: {elapsed:.0f}ms status={r.status_code} count={n} [{flag(elapsed)}]")
    return {"path": path, "ms": elapsed, "status": r.status_code, "count": n}


def fetch_all_open_deals() -> list[dict]:
    deals: list[dict] = []
    cursor: str | None = None
    while True:
        params: dict = {"status": "open", "limit": 500}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(f"{V2}/deals", headers=H, params=params, timeout=60)
        r.raise_for_status()
        body = r.json()
        page = body.get("data") or []
        if isinstance(page, dict):
            page = [page]
        deals.extend(page)
        cursor = (body.get("additional_data") or {}).get("next_cursor")
        if not cursor:
            break
    return deals


def main() -> None:
    print(f"=== CRM benchmark (deal {DEAL_ID}, budget {BUDGET_MS:.0f}ms) ===\n")

    r = requests.get(f"{V2}/deals/{DEAL_ID}", headers=H, timeout=60)
    r.raise_for_status()
    deal = r.json().get("data") or {}
    owner_id = deal.get("owner_id")
    stage_id = deal.get("stage_id")
    pipe_id = deal.get("pipeline_id")
    org_id = deal.get("org_id")
    print(
        f"Deal {DEAL_ID}: title={deal.get('title')!r} owner_id={owner_id} "
        f"stage_id={stage_id} pipeline_id={pipe_id} org_id={org_id}\n"
    )

    print("--- Pipedrive API ---")
    bench_pipe("GET deal", lambda: deal)
    all_deals = bench_pipe("all open deals (paginated)", fetch_all_open_deals)["result"]
    print(f"         total open deals in account: {len(all_deals)}")

    if stage_id:
        bench_pipe(
            f"open deals stage_id={stage_id}",
            lambda: requests.get(
                f"{V2}/deals",
                headers=H,
                params={"status": "open", "stage_id": stage_id, "limit": 500},
                timeout=60,
            ).json(),
        )

    if stage_id and owner_id:
        bench_pipe(
            f"open deals stage_id+owner_id={owner_id}",
            lambda: requests.get(
                f"{V2}/deals",
                headers=H,
                params={
                    "status": "open",
                    "stage_id": stage_id,
                    "owner_id": owner_id,
                    "limit": 500,
                },
                timeout=60,
            ).json(),
        )

    bench_pipe(
        "GET users v1",
        lambda: requests.get(
            "https://api.pipedrive.com/api/v1/users",
            headers=H,
            params={"limit": 500},
            timeout=60,
        ).json(),
    )

    if org_id:
        bench_pipe(
            f"GET org {org_id}",
            lambda: requests.get(f"{V2}/organizations/{org_id}", headers=H, timeout=30).json(),
        )

    print("\n--- Portal (cold cache) ---")
    PipedriveCrmReader = __import__(
        "portal.infrastructure.pipedrive.pipedrive_crm_reader",
        fromlist=["PipedriveCrmReader"],
    ).PipedriveCrmReader
    PipedriveCrmReader.invalidate_crm_cache()

    if owner_id:
        bench_portal(f"/pipedrive/deals?owner_user_id={owner_id}")
    bench_portal("/pipedrive/users")

    print("\n--- Portal (warm cache, fresh=false) ---")
    if owner_id:
        bench_portal(f"/pipedrive/deals?owner_user_id={owner_id}")
    bench_portal("/pipedrive/users")

    print("\n--- Portal (fresh=true) ---")
    fresh_h = {"X-Portal-Fresh": "1"}
    if owner_id:
        bench_portal(f"/pipedrive/deals?owner_user_id={owner_id}", fresh_h)
    bench_portal("/pipedrive/users", fresh_h)


if __name__ == "__main__":
    main()
