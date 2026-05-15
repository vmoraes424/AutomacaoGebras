import re
from datetime import datetime

import requests

from .config import PIPEDRIVE_API_TOKEN

# --- Hashes dos custom fields (Pipedrive) ---
FIELD_NUMERO_CONTRATO_P1 = "14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b"
FIELD_NUMERO_CONTRATO_P2 = "41a3157128d51e2fc803eeec4b242efafcb55b4e"
FIELD_NOME_CLIENTE = "28d491e0263008b437e28fc55bbad8302c4646c8"
FIELD_ENDERECO = "81566ac6e038bb0ba3adfa122c798b3e497b7538"
FIELD_CIDADE = "2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5"
FIELD_DOCUMENTO = "176d2a0d5167d1edc9b949c75f8b9a7597eabe91"
FIELD_QTD_SOLE = "f9923cdce1274da8c10cec1b9ab561e024504620"
FIELD_VALOR_MENSAL = "c5dfc907c53bb12ca916f9d0d20df23e3847e54d"
FIELD_VALOR_IMPLANTACAO = "015407d5106c321a227f1ca881f920fe2e1042ec"
FIELD_DATA_IMPLANTACAO = "2b8f62a107891e26390459cfa4048b3eedade11b"
FIELD_DATA_PRIMEIRA_COBRANCA = "f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2"
FIELD_INDICADORES_QUALIDADE = "ffb2d5aec9acdee5a242ca19683bbf4caa24cd53"
FIELD_QUALIDADE_ENERGIA = "c0a23912d889e00f51ed5bd08a55856a7e5dc930"
FIELD_CONTATO_GESTOR = "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"
FIELD_CONTATO_FINANCEIRO = "722da69afe31c1f8fa4f5457a223e2a952ae0978"
FIELD_CONTATO_CONTRATANTE = "3002b2df87f0577585ebaec394fd09a38ca8778f"
FIELD_REGIONAL = "3b5fc4072a4bff3e5e24dce974d20e15c6ebaed6"

SIGNER_FIELDS = [
    ("Coordenador Principal", "92359b129485b08fd024b8c28ef022e7635419a3"),
    ("Contato Principal", "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6"),
    ("Gestor Gebras", "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"),
    ("Diretor Principal", "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2"),
]


def get_custom_fields(deal_data: dict) -> dict:
    return deal_data.get("custom_fields") or {}


def get_val(deal_data: dict, code: str) -> str:
    cf = get_custom_fields(deal_data)
    v = cf.get(code)
    if isinstance(v, dict):
        return str(v.get("value", ""))
    return str(v) if v is not None else ""


def get_nome_cliente(deal_data: dict) -> str:
    return get_val(deal_data, FIELD_NOME_CLIENTE).strip()


def get_documento(deal_data: dict) -> str:
    return get_val(deal_data, FIELD_DOCUMENTO).strip()


def get_numero_contrato(deal_data: dict) -> str:
    p1 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P1)
    p2 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P2)
    return f"CGRc{p1}i{p2}n1r0a26"


def normalizar_documento(documento: str) -> str:
    return re.sub(r"\D", "", documento or "")


def normalizar_nome(nome: str) -> str:
    texto = (nome or "").upper()
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    return re.sub(r"\s+", " ", texto).strip()


def formatar_data_ptbr(data_iso) -> str:
    if not data_iso:
        return datetime.now().strftime("%d/%m/%Y")
    try:
        data_str = str(data_iso).split("T")[0]
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)


def formatar_decimal_plune(valor) -> str:
    try:
        num = float(str(valor).replace(".", "").replace(",", "."))
        formatted = f"{num:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return ""


def buscar_deal_por_id(deal_id: str) -> dict | None:
    url = f"https://api.pipedrive.com/api/v1/deals/{deal_id}"
    headers = {"x-api-token": PIPEDRIVE_API_TOKEN}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        return None
    data = response.json().get("data")
    if not data:
        return None
    # API v1 retorna custom fields no nível raiz; normalizar para custom_fields
    if "custom_fields" not in data:
        custom = {}
        for key, value in data.items():
            if isinstance(key, str) and len(key) == 40 and key.isalnum():
                custom[key] = value
        if custom:
            data = {**data, "custom_fields": custom}
    return data


def extrair_signatarios(deal_data: dict) -> list:
    cf = get_custom_fields(deal_data)
    sign_sequence = []
    for nome_cargo, chave in SIGNER_FIELDS:
        email = cf.get(chave)
        if email and str(email).strip():
            sign_sequence.append({"name": nome_cargo, "email": str(email).strip()})
    return sign_sequence
