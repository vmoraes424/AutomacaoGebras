import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests
from core.config import PLUNE_AUTH_TOKEN, PLUNE_BASE_URL, PLUNE_COMPANY_ID

base = PLUNE_BASE_URL.rstrip("/")
for cls in [
    "Venda.PedidoAnexo",
    "Venda.Pedido.Anexo",
    "Venda.AnexoPedido",
    "Venda.PedidoArquivo",
    "Venda.PedidoDocumento",
]:
    prefix = cls + "."
    params = {
        "_AuthToken": PLUNE_AUTH_TOKEN,
        prefix + "CompanyId": PLUNE_COMPANY_ID,
        "_" + cls + ".BrowseLimit": "1",
    }
    url = f"{base}/JSON/{cls}/Browse"
    r = requests.get(url, params=params, timeout=30)
    if cls != "Venda.AnexoPedido":
        continue
    params["_" + cls + ".BrowseSequence"] = "Id,BranchId,PedidoId,Descricao,Arquivo,Nome,Anexo"
    r = requests.get(url, params=params, timeout=30)
    import json
    data = json.loads(r.text.lstrip()[r.text.find("{"):])
    rows = (data.get("data") or {}).get("row") or []
    if isinstance(rows, dict):
        rows = [rows]
    print("rows", len(rows))
    if rows:
        print(json.dumps(rows[0], indent=2, ensure_ascii=False)[:1500])
    # try Insert schema - empty browse on fake pedido
    print("keys sample", list(rows[0].keys()) if rows else "none")
