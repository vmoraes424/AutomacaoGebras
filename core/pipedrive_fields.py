import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from .config import PIPEDRIVE_API_TOKEN
from .database import default_branch_id, resolve_filial_branch

# --- Hashes dos custom fields (Pipedrive) ---
FIELD_NUMERO_CONTRATO_P1 = "14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b"
FIELD_NUMERO_CONTRATO_P2 = "41a3157128d51e2fc803eeec4b242efafcb55b4e"
FIELD_NOME_CLIENTE = "28d491e0263008b437e28fc55bbad8302c4646c8"
FIELD_ENDERECO = "81566ac6e038bb0ba3adfa122c798b3e497b7538"
FIELD_CEP = "6d3373f7ee86c7d2449824136baf3ee1938a8ef1"
FIELD_CIDADE = "2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5"
FIELD_DOCUMENTO = "176d2a0d5167d1edc9b949c75f8b9a7597eabe91"
FIELD_QTD_SOLE = "f9923cdce1274da8c10cec1b9ab561e024504620"
FIELD_VALOR_MENSAL = "2a331c4b62c9d46aae9451af25eca2d08a3fdf0a"  # Valor Recorrência
FIELD_VALOR_IMPLANTACAO = "015407d5106c321a227f1ca881f920fe2e1042ec"
FIELD_DATA_IMPLANTACAO = "2b8f62a107891e26390459cfa4048b3eedade11b"
FIELD_DATA_PRIMEIRA_COBRANCA = "f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2"
FIELD_INDICADORES_QUALIDADE = "ffb2d5aec9acdee5a242ca19683bbf4caa24cd53"
FIELD_QUALIDADE_ENERGIA = "c0a23912d889e00f51ed5bd08a55856a7e5dc930"
FIELD_GESTAO_ACL = "8f998d4877d478b3905c126d8b23f205d0686b77"
FIELD_GESTAO_USINA_FOTOVOLTAICA = "1ba1794470354856aaca3e784349cd5f9f4d074e"

# Campos numéricos de serviço (UCs) usados em contrato, comissão e observações Plune
CAMPOS_SERVICO_UC = (
    FIELD_QTD_SOLE,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
)
FIELD_CONTATO_GESTOR = "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"
FIELD_CONTATO_FINANCEIRO = "722da69afe31c1f8fa4f5457a223e2a952ae0978"
FIELD_CONTATO_CONTRATANTE = "3002b2df87f0577585ebaec394fd09a38ca8778f"
FIELD_REGIONAL = "14855b5973f28e97dafd4e2abccc539d7461dc24"
FIELD_SUBCENTRO_NIVEL_3 = "60ffe8e9c2aa51f717865559e86e6044bfb335e6"
FIELD_FILIAL = "be20f11317ac66845bf97695f43e57795e26d01d"
FIELD_INSCRICAO_ESTADUAL = "c3e623cfa197040b778400a8977ae2c8a8386024"
FIELD_PERCENTUAL_EXITO = "225005fe8384d97183e5480781ea8ea82982301e"
FIELD_OBSERVACOES_DETALHES = "4fba2f9323c64acdcac770e38f2c0cdb840796bc"

SIGNER_FIELDS = [
    ("Coordenador Principal", "92359b129485b08fd024b8c28ef022e7635419a3"),
    ("Contato Principal", "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6"),
    ("Gestor Gebras", "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"),
    ("Diretor Principal", "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2"),
]

# Seção Contrato no Pipedrive: obrigatórios para automação, exceto CAMPOS_CONTRATO_OPCIONAIS
CAMPOS_CONTRATO_OPCIONAIS = frozenset(
    {
        FIELD_DATA_IMPLANTACAO,
        FIELD_VALOR_IMPLANTACAO,
        FIELD_OBSERVACOES_DETALHES,
        # Cliente novo pode ainda não existir no HUB (sem códigos).
        FIELD_NUMERO_CONTRATO_P1,
        FIELD_NUMERO_CONTRATO_P2,
    }
)

# (rótulo no Pipedrive, hash, tipo) — text | enum | email | cep | uc | money_mensal | date | documento
CAMPOS_CONTRATO_OBRIGATORIOS: tuple[tuple[str, str, str], ...] = (
    ("Filial", FIELD_FILIAL, "enum"),
    ("Dados da Contratante", FIELD_NOME_CLIENTE, "text"),
    ("Endereço", FIELD_ENDERECO, "text"),
    ("CEP", FIELD_CEP, "cep"),
    ("Município/Estado", FIELD_CIDADE, "text"),
    ("CPF/CNPJ", FIELD_DOCUMENTO, "documento"),
    ("Inscrição Estadual", FIELD_INSCRICAO_ESTADUAL, "text"),
    ("SOLE Web", FIELD_QTD_SOLE, "uc"),
    ("Sole Consultoria", FIELD_QUALIDADE_ENERGIA, "uc"),
    ("Gestão ACL - Mercado Livre de Energia", FIELD_GESTAO_ACL, "uc"),
    ("Gestão Usina Fotovoltaica", FIELD_GESTAO_USINA_FOTOVOLTAICA, "uc"),
    ("Gestão da Qualidade de Energia", FIELD_INDICADORES_QUALIDADE, "uc"),
    ("Valor Recorrência", FIELD_VALOR_MENSAL, "money_mensal"),
    (
        "Data de Pagamento da Primeira Cobrança Mensal",
        FIELD_DATA_PRIMEIRA_COBRANCA,
        "date",
    ),
    ("Porcentagem de Exito", FIELD_PERCENTUAL_EXITO, "enum"),
    ("Sub Centro Nível 2", FIELD_REGIONAL, "enum"),
    ("Sub Centro Nível 3", FIELD_SUBCENTRO_NIVEL_3, "enum"),
    ("E-mail Coordenador", "92359b129485b08fd024b8c28ef022e7635419a3", "email"),
    ("E-mail Assinante do Contrato", "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6", "email"),
    ("E-mail Gestor GEBRAS", FIELD_CONTATO_GESTOR, "email"),
    ("E-mail Diretor", "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2", "email"),
    ("Email Financeiro Contratante", FIELD_CONTATO_FINANCEIRO, "email"),
    ("E-mail Gestor Contratante", FIELD_CONTATO_CONTRATANTE, "email"),
)


def get_custom_fields(deal_data: dict) -> dict:
    return deal_data.get("custom_fields") or {}


def get_val(deal_data: dict, code: str) -> str:
    cf = get_custom_fields(deal_data)
    v = cf.get(code)
    if isinstance(v, dict):
        return str(v.get("value", ""))
    return str(v) if v is not None else ""


_enum_option_labels: dict[str, dict[str, str]] | None = None


def _enum_option_labels_for_field(field_code: str) -> dict[str, str]:
    """Mapeia id da opção (str) -> label (dealFields v2)."""
    global _enum_option_labels
    if _enum_option_labels is None:
        _enum_option_labels = {}
        if not PIPEDRIVE_API_TOKEN:
            return {}
        cursor = None
        while True:
            params: dict = {"limit": 500}
            if cursor:
                params["cursor"] = cursor
            response = requests.get(
                "https://api.pipedrive.com/api/v2/dealFields",
                headers={"x-api-token": PIPEDRIVE_API_TOKEN},
                params=params,
                timeout=60,
            )
            try:
                response.raise_for_status()
            except requests.HTTPError:
                break
            body = response.json()
            for field in body.get("data") or []:
                code = str(field.get("field_code") or "")
                if not code or not field.get("options"):
                    continue
                _enum_option_labels[code] = {
                    str(opt.get("id")): str(opt.get("label") or "").strip()
                    for opt in field.get("options") or []
                    if opt.get("id") is not None
                }
            cursor = (body.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break
    return _enum_option_labels.get(field_code, {})


def get_enum_label(deal_data: dict, field_code: str) -> str:
    """Rótulo de campo enum (Sub Centro etc.) — catálogo Plune usa o label."""
    raw = get_custom_fields(deal_data).get(field_code)
    if isinstance(raw, dict):
        return str(raw.get("label") or raw.get("name") or "").strip()
    if raw is None or raw == "":
        return ""
    opt_id = str(raw).strip()
    return _enum_option_labels_for_field(field_code).get(opt_id, opt_id)


def get_filial_chaves(deal_data: dict) -> tuple[str, str]:
    """Retorna (rótulo, id da opção) do enum Filial para mapeamento no Plune."""
    raw = get_custom_fields(deal_data).get(FIELD_FILIAL)
    if isinstance(raw, dict):
        label = str(raw.get("label") or raw.get("name") or "").strip()
        opt_id = str(raw.get("id") or raw.get("value") or "").strip()
        return label, opt_id
    texto = str(raw or "").strip()
    return texto, texto


def get_filial_label(deal_data: dict) -> str:
    label, _ = get_filial_chaves(deal_data)
    return label


def resolver_branch_id(deal_data: dict) -> str:
    """Filial (Pipedrive) -> Venda.Pedido.BranchId (tabela pipedrive_filial no MySQL)."""
    label, opt_id = get_filial_chaves(deal_data)
    branch_id = resolve_filial_branch(label, opt_id)
    if branch_id:
        return branch_id
    raise ValueError(
        "Filial do deal não mapeada para BranchId no Plune. "
        f"Valor no Pipedrive: {get_filial_label(deal_data) or opt_id!r}. "
        "Cadastre em pipedrive_filial (MySQL)."
    )


def settings_por_branch(branch_id: str) -> dict:
    from .database import branch_config
    from .plune_catalog import garantir_catalogo_inicializado

    garantir_catalogo_inicializado()
    cfg = branch_config(str(branch_id))
    if cfg:
        return cfg
    from .config import PLUNE_PEDIDO_MODELO_ID, PLUNE_PEDIDO_SERIE

    return {
        "subcentro_custo_id": "",
        "parametro_recorrente": "",
        "parametro_implantacao": "",
        "pedido_serie": PLUNE_PEDIDO_SERIE,
        "pedido_modelo_id": PLUNE_PEDIDO_MODELO_ID,
        "regional_map": {},
        "subcentro3_map": {},
    }


def get_nome_cliente(deal_data: dict) -> str:
    return get_val(deal_data, FIELD_NOME_CLIENTE).strip()


def get_documento(deal_data: dict) -> str:
    return get_val(deal_data, FIELD_DOCUMENTO).strip()


def get_numero_contrato(deal_data: dict) -> str:
    """Monta o identificador do contrato; sem códigos HUB usa o deal_id."""
    p1 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P1).strip()
    p2 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P2).strip()
    if p1 and p2:
        return f"CGRc{p1}i{p2}n1r0a26"
    deal_id = str(deal_data.get("id", "")).strip() or "0"
    p1 = p1 or deal_id
    p2 = p2 or deal_id
    return f"CGRc{p1}i{p2}n1r0a26"


def normalizar_documento(documento: str) -> str:
    return re.sub(r"\D", "", documento or "")


def normalizar_cep(cep: str) -> str:
    """Somente dígitos, até 8 (Ultra::CEP no Plune)."""
    return re.sub(r"\D", "", cep or "")[:8]


def normalizar_nome(nome: str) -> str:
    texto = (nome or "").upper()
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    return re.sub(r"\s+", " ", texto).strip()


TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")


def formatar_data_hora_brasilia(dt: datetime | None) -> str:
    """Data/hora em Brasília (America/Sao_Paulo) para logs e mensagens ao usuário."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_BRASILIA).strftime("%d/%m/%Y %H:%M:%S")


def formatar_data_ptbr(data_iso) -> str:
    if not data_iso:
        return datetime.now().strftime("%d/%m/%Y")
    try:
        data_str = str(data_iso).split("T")[0]
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)


def formatar_quantidade_uc(valor) -> str:
    """Quantidade de UCs no contrato Word: apenas número, sem por extenso."""
    texto = str(valor or "").strip()
    if not texto:
        return ""
    try:
        normalizado = texto.replace("R$", "").replace(" ", "")
        num = float(normalizado.replace(".", "").replace(",", "."))
        if num == int(num):
            return str(int(num))
        return str(num).replace(".", ",")
    except (ValueError, TypeError):
        return texto


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
