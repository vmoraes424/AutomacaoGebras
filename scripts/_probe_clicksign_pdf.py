import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.automacao_contrato import ClicksignClient
from core.config import CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN
from core.envelope_state import buscar_por_deal_id

deal_id = sys.argv[1] if len(sys.argv) > 1 else "565"
rec = buscar_por_deal_id(deal_id)
print("envelope record", rec)
if not rec:
    sys.exit(0)
cs = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)
eid = rec["envelope_id"]
r = cs._request("GET", f"/envelopes/{eid}/documents", "list_documents")
print("docs status", r.status_code)
data = r.json().get("data") or []
if isinstance(data, dict):
    data = [data]
for d in data:
    did = d.get("id")
    r2 = cs._request("GET", f"/envelopes/{eid}/documents/{did}", "get_document")
    attrs = r2.json().get("data", {}).get("attributes", {})
    downloads = attrs.get("downloads") or {}
    print("doc", did, attrs.get("filename"), downloads.keys() if downloads else "no downloads")
