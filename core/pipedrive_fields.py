import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from .config import PIPEDRIVE_API_TOKEN
from .database import default_branch_id, resolve_filial_branch

# --- Hashes dos custom fields (Pipedrive) ---
FIELD_NOTAS = "14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b"
FIELD_CODIGO_CLIENTE_INSTALACAO = "41a3157128d51e2fc803eeec4b242efafcb55b4e"
FIELD_NOME_CLIENTE = "28d491e0263008b437e28fc55bbad8302c4646c8"
FIELD_ENDERECO = "81566ac6e038bb0ba3adfa122c798b3e497b7538"
FIELD_CEP = "6d3373f7ee86c7d2449824136baf3ee1938a8ef1"
FIELD_CIDADE = "2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5"
FIELD_DOCUMENTO = "176d2a0d5167d1edc9b949c75f8b9a7597eabe91"
FIELD_QTD_SOLE = "f9923cdce1274da8c10cec1b9ab561e024504620"
FIELD_VALOR_MENSAL = "2a331c4b62c9d46aae9451af25eca2d08a3fdf0a"  # Valor Recorrência
FIELD_VALOR_IMPLANTACAO = "015407d5106c321a227f1ca881f920fe2e1042ec"
# Inscrição Municipal (varchar, item 1.6 do quadro resumo) — antes «Data de Implantação» no Pipedrive
FIELD_INSCRICAO_MUNICIPAL = "f40caca58878f19aefba960b87127753b7b932ca"
FIELD_DATA_DE_IMPLANTACAO = FIELD_INSCRICAO_MUNICIPAL  # alias legado (campo renomeado no CRM)
# Data de Pagamento da Implantação (date) — x1_PrevisaoCobranca / contrato Word
FIELD_DATA_PAGAMENTO_IMPLANTACAO = "2b8f62a107891e26390459cfa4048b3eedade11b"
FIELD_DATA_IMPLANTACAO = FIELD_DATA_PAGAMENTO_IMPLANTACAO  # alias legado
FIELD_DATA_PRIMEIRA_COBRANCA = "f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2"
FIELD_INDICADORES_QUALIDADE = "ffb2d5aec9acdee5a242ca19683bbf4caa24cd53"
FIELD_QUALIDADE_ENERGIA = "c0a23912d889e00f51ed5bd08a55856a7e5dc930"
FIELD_GESTAO_ACL = "8f998d4877d478b3905c126d8b23f205d0686b77"
FIELD_GESTAO_USINA_FOTOVOLTAICA = "1ba1794470354856aaca3e784349cd5f9f4d074e"
FIELD_QUANTIDADE_UCS = "c6d1c300a1d070c1a54494a246f6330beabe36aa"

# Campos numéricos de serviço (UCs) usados em contrato, comissão e observações Plune
CAMPOS_SERVICO_UC = (
    FIELD_QTD_SOLE,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
)
# Removido do Pipedrive (jun/2026); mantido para deals antigos e contrato Word
FIELD_CONTATO_GESTOR = "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"
FIELD_CONTATO_FINANCEIRO = "722da69afe31c1f8fa4f5457a223e2a952ae0978"
FIELD_CONTATO_CONTRATANTE = "3002b2df87f0577585ebaec394fd09a38ca8778f"
FIELD_CONTATO_PRINCIPAL = "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6"
FIELD_REGIONAL = "14855b5973f28e97dafd4e2abccc539d7461dc24"
FIELD_SUBCENTRO_NIVEL_3 = "60ffe8e9c2aa51f717865559e86e6044bfb335e6"
FIELD_EMAIL_CONSULTOR_GEBRAS = "3bacd163054a20c843e79bc525bebc1285773b17"
FIELD_EMAIL_COORDENADOR_GEBRAS = "3a5c1d1dc1b5f023f57c65b9bf725c27d754d31b"
FIELD_EMAIL_DIRETOR_GEBRAS = "a2eba4ca348f3597d570d84c356aa66e81d762cd"
# Removidos do Pipedrive (jun/2026); fallback em SIGNER_FIELDS para deals antigos
FIELD_EMAIL_COORDENADOR_LEGADO = "92359b129485b08fd024b8c28ef022e7635419a3"
FIELD_EMAIL_DIRETOR_LEGADO = "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2"
FIELD_FILIAL = "be20f11317ac66845bf97695f43e57795e26d01d"
FIELD_INSCRICAO_ESTADUAL = "c3e623cfa197040b778400a8977ae2c8a8386024"
FIELD_PERCENTUAL_EXITO = "225005fe8384d97183e5480781ea8ea82982301e"
FIELD_OBSERVACOES_DETALHES = "4fba2f9323c64acdcac770e38f2c0cdb840796bc"

# Tipos Pipedrive v2 relevantes na escrita (PATCH custom_fields)
PIPE_FIELDS_SET = frozenset(
    {
        FIELD_EMAIL_CONSULTOR_GEBRAS,
        FIELD_EMAIL_COORDENADOR_GEBRAS,
        FIELD_EMAIL_DIRETOR_GEBRAS,
    }
)
PIPE_FIELDS_ENUM = frozenset(
    {
        FIELD_FILIAL,
        FIELD_REGIONAL,
        FIELD_SUBCENTRO_NIVEL_3,
        FIELD_PERCENTUAL_EXITO,
    }
)
PIPE_FIELDS_ADDRESS = frozenset({FIELD_ENDERECO, FIELD_CIDADE})
PIPE_FIELDS_MONETARY = frozenset({FIELD_VALOR_MENSAL, FIELD_VALOR_IMPLANTACAO})
# Quantidade de UC's é varchar no Pipe (texto), não double como os demais serviços.
PIPE_FIELDS_NUMERIC = frozenset(CAMPOS_SERVICO_UC)
PIPE_FIELDS_TEXT_NUMERIC = frozenset({FIELD_QUANTIDADE_UCS})
PIPE_FIELDS_DATE = frozenset(
    {FIELD_DATA_PAGAMENTO_IMPLANTACAO, FIELD_DATA_PRIMEIRA_COBRANCA}
)
DEFAULT_PIPE_CURRENCY = "BRL"


def parse_decimal_brl(valor) -> float | None:
    """Interpreta valor monetário em notação BR (1.805,50 / 5.000 / 1805)."""
    texto = str(valor or "").strip()
    if not texto:
        return None
    normalizado = texto.replace("R$", "").replace(" ", "")
    if "," in normalizado and "." in normalizado:
        if normalizado.rfind(",") > normalizado.rfind("."):
            normalizado = normalizado.replace(".", "").replace(",", ".")
        else:
            normalizado = normalizado.replace(",", "")
    elif "," in normalizado:
        normalizado = normalizado.replace(".", "").replace(",", ".")
    elif "." in normalizado:
        partes = normalizado.split(".")
        if len(partes) > 1 and all(re.fullmatch(r"\d+", p) for p in partes):
            if len(partes[-1]) == 3:
                normalizado = "".join(partes)
    try:
        return float(normalizado)
    except ValueError:
        return None


def monetary_value_for_pipe(valor) -> dict[str, float | str]:
    """Formato PATCH v2 para custom field monetary."""
    numero = parse_decimal_brl(valor)
    if numero is None:
        raise ValueError(f"Valor monetário inválido: {valor!r}")
    return {"value": numero, "currency": DEFAULT_PIPE_CURRENCY}


# Ordem Clicksign: Consultor → Coordenador → Cliente → Diretor.
# papel = rótulo nos logs; nome_clicksign = name na API (2+ palavras).
# Grupo 1 Consultor; comercial recebe e-mail informativo separado (aviso_comercial).
SIGNER_FIELDS = [
    ("Consultor", "Gestor Gebras", FIELD_EMAIL_CONSULTOR_GEBRAS, 1, FIELD_CONTATO_GESTOR),
    (
        "Coordenador",
        "Coordenador Principal",
        FIELD_EMAIL_COORDENADOR_GEBRAS,
        2,
        FIELD_EMAIL_COORDENADOR_LEGADO,
    ),
    ("Cliente", "Contato Principal", FIELD_CONTATO_PRINCIPAL, 3, None),
    (
        "Diretor",
        "Diretor Principal",
        FIELD_EMAIL_DIRETOR_GEBRAS,
        4,
        FIELD_EMAIL_DIRETOR_LEGADO,
    ),
]

# Seção Contrato no Pipedrive: obrigatórios para automação, exceto CAMPOS_CONTRATO_OPCIONAIS
CAMPOS_CONTRATO_OPCIONAIS = frozenset({FIELD_OBSERVACOES_DETALHES})

# (rótulo no Pipedrive, hash, tipo) — text | enum | email | cep | uc | money_mensal | date | documento
CAMPOS_CONTRATO_OBRIGATORIOS: tuple[tuple[str, str, str], ...] = (
    ("Filial", FIELD_FILIAL, "enum"),
    ("Contratante", FIELD_NOME_CLIENTE, "text"),
    ("Endereço", FIELD_ENDERECO, "text"),
    ("CEP", FIELD_CEP, "cep"),
    ("Município/Estado", FIELD_CIDADE, "text"),
    ("CPF/CNPJ", FIELD_DOCUMENTO, "documento"),
    ("Inscrição Estadual", FIELD_INSCRICAO_ESTADUAL, "text"),
    ("Inscrição Municipal", FIELD_INSCRICAO_MUNICIPAL, "text"),
    ("Notas", FIELD_NOTAS, "text"),
    ("Código Cliente/Código da Instalação", FIELD_CODIGO_CLIENTE_INSTALACAO, "text"),
    ("SOLE Web", FIELD_QTD_SOLE, "uc"),
    ("Sole Consultoria", FIELD_QUALIDADE_ENERGIA, "uc"),
    ("Gestão ACL - Mercado Livre de Energia", FIELD_GESTAO_ACL, "uc"),
    ("Gestão Usina Fotovoltaica", FIELD_GESTAO_USINA_FOTOVOLTAICA, "uc"),
    ("Gestão da Qualidade de Energia", FIELD_INDICADORES_QUALIDADE, "uc"),
    ("Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"),
    ("Valor Recorrência", FIELD_VALOR_MENSAL, "money_mensal"),
    ("Valor de Implantação", FIELD_VALOR_IMPLANTACAO, "money_implantacao"),
    (
        "Data de Pagamento da Implantação",
        FIELD_DATA_PAGAMENTO_IMPLANTACAO,
        "date",
    ),
    (
        "Data de Pagamento da Primeira Cobrança Mensal",
        FIELD_DATA_PRIMEIRA_COBRANCA,
        "date",
    ),
    ("Porcentagem de Exito", FIELD_PERCENTUAL_EXITO, "enum"),
    ("Regional", FIELD_REGIONAL, "enum"),
    ("Consultor", FIELD_SUBCENTRO_NIVEL_3, "enum"),
    ("E-mail Assinante do Contrato", FIELD_CONTATO_PRINCIPAL, "email"),
    ("E-mail Consultor GEBRAS", FIELD_EMAIL_CONSULTOR_GEBRAS, "email"),
    ("E-mail Coordenador GEBRAS", FIELD_EMAIL_COORDENADOR_GEBRAS, "email"),
    ("E-mail Diretor GEBRAS", FIELD_EMAIL_DIRETOR_GEBRAS, "email"),
    ("Email Financeiro Contratante", FIELD_CONTATO_FINANCEIRO, "email"),
    ("E-mail Gestor Contratante", FIELD_CONTATO_CONTRATANTE, "email"),
)


def get_custom_fields(deal_data: dict) -> dict:
    return deal_data.get("custom_fields") or {}


def _rotulos_opcao_campo(deal_data: dict, field_code: str, raw) -> list[str]:
    """Resolve ids de enum/set (API v2 devolve listas como [91]) para rótulos."""
    rotulos: list[str] = []
    vistos: set[str] = set()
    opcoes = _enum_option_labels_for_field(field_code)

    for opt_id in _ids_opcao_campo(raw):
        rotulo = opcoes.get(opt_id, opt_id).strip()
        if not rotulo or rotulo in vistos:
            continue
        vistos.add(rotulo)
        rotulos.append(rotulo)

    if rotulos:
        return rotulos

    if isinstance(raw, dict):
        for chave in ("label", "name", "value"):
            texto = str(raw.get(chave) or "").strip()
            if texto:
                return [texto]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def get_val(deal_data: dict, code: str) -> str:
    cf = get_custom_fields(deal_data)
    v = cf.get(code)
    if v is None or v == "":
        v = deal_data.get(code)
    if isinstance(v, dict):
        return str(v.get("value", v.get("label", "")))
    if isinstance(v, list):
        rotulos = _rotulos_opcao_campo(deal_data, code, v)
        return ", ".join(rotulos)
    if v is not None and v != "":
        texto = str(v).strip()
        if "@" not in texto:
            rotulo = _enum_option_labels_for_field(code).get(texto, "")
            if rotulo:
                return rotulo
        return texto
    return ""


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


def warm_deal_field_options_cache() -> None:
    """Pre-carrega catálogo enum/set do Pipedrive (evita latência no 1º blur)."""
    if _enum_option_labels is not None:
        return
    _enum_option_labels_for_field(FIELD_FILIAL)


def _label_to_option_id(field_code: str, label: str) -> str | None:
    texto = str(label or "").strip()
    if not texto:
        return None
    options = _enum_option_labels_for_field(field_code)
    for opt_id, opt_label in options.items():
        if opt_label.strip().casefold() == texto.casefold():
            return str(opt_id)
    if texto in options:
        return str(texto)
    return None


def option_ids_for_set_field(field_code: str, label_text: str) -> list[int]:
    """Converte rótulo(s) do formulário em ids para campo set/multi-option (API v2)."""
    partes = [p.strip() for p in str(label_text or "").split(",") if p.strip()]
    if not partes:
        return []
    ids: list[int] = []
    for parte in partes:
        opt_id = _label_to_option_id(field_code, parte)
        if opt_id is None:
            raise ValueError(
                f"Opção «{parte}» não encontrada nas opções do campo Pipedrive."
            )
        ids.append(int(opt_id))
    return ids


def option_id_for_enum_field(field_code: str, label: str) -> int | None:
    """Converte rótulo do formulário em id de opção única (enum)."""
    opt_id = _label_to_option_id(field_code, label)
    if opt_id is None:
        return None
    return int(opt_id)


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


def split_cidade_estado(texto: str) -> tuple[str, str]:
    """Separa cidade e UF do campo Município/Estado (ex.: «Pelotas - RS, Brasil»)."""
    texto = (texto or "").strip()
    if not texto:
        return "", ""
    if "-" in texto:
        cidade, resto = texto.split("-", 1)
        resto = resto.strip()
        if "," in resto:
            estado = resto.split(",", 1)[0].strip()
        else:
            estado = resto
        return cidade.strip(), estado
    if "/" in texto:
        cidade, estado = texto.rsplit("/", 1)
        return cidade.strip(), estado.strip()
    return texto, ""


def get_cidade_estado(deal_data: dict) -> tuple[str, str]:
    return split_cidade_estado(get_val(deal_data, FIELD_CIDADE))


def get_documento(deal_data: dict) -> str:
    return get_val(deal_data, FIELD_DOCUMENTO).strip()


def sufixo_ano_contrato_gebras(*, ano: int | None = None) -> str:
    """Sufixo fixo do número de contrato com os 2 últimos dígitos do ano (ex.: n1r0a26)."""
    if ano is None:
        ano = datetime.now(ZoneInfo("America/Sao_Paulo")).year
    return f"n1r0a{ano % 100:02d}"


def _primeira_instalacao_codigo_contrato(raw: str) -> str:
    """Primeira instalação após «/» no campo combinado (texto original, ex.: 00665)."""
    texto = (raw or "").strip()
    if "/" not in texto:
        return ""
    parte_instalacoes = texto.split("/", 1)[1]
    for parte in re.split(r"[,;\s]+", parte_instalacoes):
        pedaco = parte.strip()
        if pedaco:
            return pedaco
    return ""


def _codigo_cliente_contrato(raw: str) -> str:
    texto = (raw or "").strip()
    if not texto:
        return ""
    return texto.split("/", 1)[0].strip()


def parse_codigo_cliente_instalacao(raw: str) -> tuple[int, list[int]]:
    """
    Campo «Código Cliente/Código da Instalação»:
    - «352» → cliente 352 (sem instalações; HUB exige «/» após o cliente)
    - «352/1234» → cliente 352, instalações [1234]
    - «352/1234,5678» → cliente 352, instalações [1234, 5678]
    """
    texto = (raw or "").strip()
    if not texto:
        raise ValueError(
            "Código Cliente/Código da Instalação ausente. "
            "Informe «codigo_cliente» ou «codigo_cliente/instalacao1,instalacao2»."
        )

    def _parse_inteiro(valor: str, rotulo: str) -> int:
        try:
            return int(valor.strip())
        except ValueError as exc:
            raise ValueError(
                f"Código Cliente/Código da Instalação inválido: {rotulo} "
                f"deve ser numérico. Valor recebido: {valor!r}."
            ) from exc

    def _parse_instalacoes(parte: str) -> list[int]:
        codigos: list[int] = []
        vistos: set[int] = set()
        for item in re.split(r"[,;\s]+", parte.strip()):
            pedaco = item.strip()
            if not pedaco:
                continue
            codigo = _parse_inteiro(pedaco, "instalação")
            if codigo not in vistos:
                vistos.add(codigo)
                codigos.append(codigo)
        return codigos

    if "/" in texto:
        parte_cliente, parte_instalacoes = texto.split("/", 1)
        if not parte_cliente.strip():
            raise ValueError(
                "Código Cliente/Código da Instalação inválido: informe o código "
                f"do cliente antes de «/». Valor recebido: {texto!r}."
            )
        codigo_cliente = _parse_inteiro(parte_cliente, "código do cliente")
        return codigo_cliente, _parse_instalacoes(parte_instalacoes)

    return _parse_inteiro(texto.split(",")[0], "código do cliente"), []


def format_codigo_cliente_instalacao(
    codigo_cliente: int, codigos_instalacao: list[int] | tuple[int, ...]
) -> str:
    """Formato enviado ao Pipedrive: «352» ou «352/1234,3456»."""
    if not codigos_instalacao:
        return str(codigo_cliente)
    return f"{codigo_cliente}/{','.join(str(c) for c in codigos_instalacao)}"


def get_numero_contrato(deal_data: dict) -> str:
    """Monta CGRc{1ª instalação}i{cliente}n1r0a{AA}; instalação vem do campo cliente/instalação."""
    codigo_cliente_raw = get_val(deal_data, FIELD_CODIGO_CLIENTE_INSTALACAO).strip()
    primeira_instalacao = _primeira_instalacao_codigo_contrato(codigo_cliente_raw)
    codigo_cliente = _codigo_cliente_contrato(codigo_cliente_raw)
    sufixo = sufixo_ano_contrato_gebras()
    if primeira_instalacao and codigo_cliente:
        return f"CGRc{primeira_instalacao}i{codigo_cliente}{sufixo}"
    deal_id = str(deal_data.get("id", "")).strip() or "0"
    primeira_instalacao = primeira_instalacao or deal_id
    codigo_cliente = codigo_cliente or deal_id
    return f"CGRc{primeira_instalacao}i{codigo_cliente}{sufixo}"


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
    """Monta signatários Clicksign: Consultor → Coordenador → Cliente → Diretor."""
    sign_sequence: list[dict] = []
    emails_vistos: set[str] = set()

    for papel, nome_clicksign, chave, grupo, chave_legado in SIGNER_FIELDS:
        emails = _emails_signatario_deal(deal_data, chave, chave_legado)
        for indice, email in enumerate(emails):
            chave_email = email.casefold()
            if chave_email in emails_vistos:
                continue
            emails_vistos.add(chave_email)
            nome = nome_clicksign if indice == 0 else f"{nome_clicksign} {indice + 1}"
            papel_log = papel if indice == 0 else f"{papel} {indice + 1}"
            sign_sequence.append(
                {
                    "papel": papel_log,
                    "name": nome,
                    "email": email,
                    "group": grupo,
                }
            )
    return sign_sequence


def signatarios_omitidos_por_email_duplicado(
    deal_data: dict, sign_sequence: list[dict]
) -> list[dict]:
    """Papéis com e-mail preenchido no deal, mas omitidos por deduplicação de e-mail."""
    emails_ativos = {s["email"].casefold() for s in sign_sequence}
    papeis_ativos = {s.get("papel", "") for s in sign_sequence}
    omitidos: list[dict] = []

    for papel, _nome_clicksign, chave, grupo, chave_legado in SIGNER_FIELDS:
        emails = _emails_signatario_deal(deal_data, chave, chave_legado)
        if not emails:
            continue
        email = emails[0]
        if email.casefold() not in emails_ativos:
            continue
        if papel in papeis_ativos or any(p.startswith(f"{papel} ") for p in papeis_ativos):
            continue
        omitidos.append(
            {
                "papel": papel,
                "email": email,
                "group": grupo,
                "motivo": "e-mail duplicado (já usado em outro papel)",
            }
        )
    return omitidos


def _ids_opcao_campo(raw) -> list[str]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        ids: list[str] = []
        for item in raw:
            if isinstance(item, dict):
                val = item.get("id") or item.get("value")
                if val is not None:
                    ids.append(str(val))
            elif item not in (None, ""):
                ids.append(str(item))
        return ids
    if isinstance(raw, dict):
        val = raw.get("id") or raw.get("value")
        return [str(val)] if val is not None else []
    return [str(raw).strip()]


def _emails_signatario_deal(
    deal_data: dict, field_code: str, field_legado: str | None
) -> list[str]:
    for code in (field_code, field_legado):
        if not code:
            continue
        emails = _emails_de_hash_signatario(deal_data, code)
        if emails:
            return emails
    return []


def _email_signatario_deal(
    deal_data: dict, field_code: str, field_legado: str | None
) -> str:
    emails = _emails_signatario_deal(deal_data, field_code, field_legado)
    return emails[0] if emails else ""


def _emails_de_hash_signatario(deal_data: dict, field_code: str) -> list[str]:
    """Resolve um ou mais e-mails (campo set do Pipedrive aceita múltiplas opções)."""
    cf = get_custom_fields(deal_data)
    raw = cf.get(field_code)
    if raw is None or raw == "":
        raw = deal_data.get(field_code)
    if raw is None or raw == "":
        return []

    encontrados: list[str] = []
    vistos: set[str] = set()

    def _adicionar(valor: str) -> None:
        for parte in re.split(r"[,;]+", str(valor or "")):
            email = parte.strip()
            if not email or "@" not in email:
                continue
            chave = email.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            encontrados.append(email)

    if isinstance(raw, str):
        _adicionar(raw)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                for chave in ("label", "name", "value", "email"):
                    texto = str(item.get(chave) or "").strip()
                    if "@" in texto:
                        _adicionar(texto)
                        break
                else:
                    val = item.get("id") or item.get("value")
                    if val is not None:
                        label = _enum_option_labels_for_field(field_code).get(
                            str(val), ""
                        ).strip()
                        if label:
                            _adicionar(label)
            elif isinstance(item, str):
                if "@" in item:
                    _adicionar(item)
                else:
                    label = _enum_option_labels_for_field(field_code).get(
                        item.strip(), ""
                    ).strip()
                    if label:
                        _adicionar(label)
            elif item not in (None, ""):
                label = _enum_option_labels_for_field(field_code).get(
                    str(item).strip(), ""
                ).strip()
                if label:
                    _adicionar(label)

    for opt_id in _ids_opcao_campo(raw):
        label = _enum_option_labels_for_field(field_code).get(opt_id, "").strip()
        if label:
            _adicionar(label)

    if not encontrados:
        texto = get_val(deal_data, field_code).strip()
        if texto:
            _adicionar(texto)

    return encontrados


def get_contato_gestor_contrato(deal_data: dict) -> str:
    """
    E-mail do consultor Gebras na cláusula 10.5 do contrato.

    O template traz ``gpo@gebras.com; {{ contato_gestor }}`` — este valor é só
    o consultor (campo «E-mail Consultor GEBRAS»), com fallback no hash legado.
    """
    return _email_signatario_deal(
        deal_data, FIELD_EMAIL_CONSULTOR_GEBRAS, FIELD_CONTATO_GESTOR
    )
