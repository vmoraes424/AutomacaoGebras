"""POC: Insert Venda.AnexoPedido com multipart (não rodar em prod sem pedido de teste)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests
from core.config import PLUNE_AUTH_TOKEN, PLUNE_BASE_URL, PLUNE_COMPANY_ID

# pedido exemplo do browse (ajuste se necessário)
BRANCH_ID = "751"
PEDIDO_ID = sys.argv[1] if len(sys.argv) > 1 else "2027"
CLIENTE_ID = sys.argv[2] if len(sys.argv) > 2 else ""

base = PLUNE_BASE_URL.rstrip("/")
pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"

for path in [
    f"/Class/Venda.AnexoPedido/Insert",
    f"/JSON/Venda.AnexoPedido/Insert",
]:
    data = {
        "Venda.AnexoPedido.CompanyId": PLUNE_COMPANY_ID,
        "Venda.AnexoPedido.BranchId": BRANCH_ID,
        "Venda.AnexoPedido.PedidoId": PEDIDO_ID,
        "_AuthToken": PLUNE_AUTH_TOKEN,
        "_Venda.AnexoPedido.OK": "1",
    }
    if CLIENTE_ID:
        data["Venda.AnexoPedido.ClienteId"] = CLIENTE_ID
    files = {
        "Venda.AnexoPedido.Anexo": ("teste_automacao.pdf", pdf, "application/pdf"),
    }
    url = base + path
    r = requests.post(url, data=data, files=files, timeout=120)
    print(path, r.status_code, r.text[:400].replace("\n", " "))
