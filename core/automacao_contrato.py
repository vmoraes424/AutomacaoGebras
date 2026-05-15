import time
import os
import requests
import base64
from datetime import datetime, timezone
from docxtpl import DocxTemplate

from .config import (
    ARQUIVO_DEALS_PROCESSADOS,
    CLICKSIGN_ACCESS_TOKEN,
    CLICKSIGN_BASE_URL,
    CLICKSIGN_RATE_LIMIT_BUFFER_SEC,
    CLICKSIGN_RATE_LIMIT_MAX_RETRIES,
    INTERVALO_POLLING_SEGUNDOS,
    MODELO_DOCX,
    PASTA_SAIDA,
    PIPEDRIVE_API_TOKEN,
    TESTE_PLUNE_SEM_ASSINATURA,
)
from .envelope_state import listar_aguardando_pedido_plune, salvar_envelope_pendente
from .plune_pedido import PluneError, buscar_parceiro_plune_por_documento, criar_pedido_plune
from .pipedrive_fields import (
    FIELD_CONTATO_CONTRATANTE,
    FIELD_CONTATO_FINANCEIRO,
    FIELD_CONTATO_GESTOR,
    FIELD_DATA_IMPLANTACAO,
    FIELD_DATA_PRIMEIRA_COBRANCA,
    FIELD_DOCUMENTO,
    FIELD_ENDERECO,
    FIELD_CIDADE,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_NOME_CLIENTE,
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    FIELD_QTD_SOLE,
    FIELD_QUALIDADE_ENERGIA,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
    extrair_signatarios,
    formatar_data_ptbr,
    get_val,
)

# --- CONFIGURAÇÕES (ver config.py) ---
API_TOKEN = PIPEDRIVE_API_TOKEN

# Define a data/hora de início do script em UTC para comparar com o won_time do Pipedrive
DATA_INICIO_SCRIPT = datetime.now(timezone.utc)


# ---------- GERENCIAMENTO DE ESTADO ----------
def carregar_deals_processados():
    if not os.path.exists(ARQUIVO_DEALS_PROCESSADOS):
        return set()
    with open(ARQUIVO_DEALS_PROCESSADOS, "r") as f:
        return set(line.strip() for line in f if line.strip())


def salvar_deal_processado(deal_id):
    pasta_estado = os.path.dirname(ARQUIVO_DEALS_PROCESSADOS)
    if pasta_estado:
        os.makedirs(pasta_estado, exist_ok=True)
    with open(ARQUIVO_DEALS_PROCESSADOS, "a") as f:
        f.write(f"{deal_id}\n")


# ---------- FUNÇÕES AUXILIARES ----------
def formatar_moeda(valor):
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(valor)


def numero_por_extenso_unidades(num):
    try:
        n = int(num)
    except:
        return str(num)
    extenso = {
        1: "uma",
        2: "duas",
        3: "três",
        4: "quatro",
        5: "cinco",
        6: "seis",
        7: "sete",
        8: "oito",
        9: "nove",
        10: "dez",
        11: "onze",
        12: "doze",
        13: "treze",
        14: "quatorze",
        15: "quinze",
    }
    texto = extenso.get(n, str(n))
    return f"{n} ({texto}) {'unidade' if n==1 else 'unidades'}"


# ---------- CLICKSIGN CLIENT (V3) ----------
class ClicksignClient:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/vnd.api+json"}
        )

    def _url(self, path: str):
        sep = "&" if "?" in path else "?"
        return f"{self.base_url}{path}{sep}access_token={self.access_token}"

    def _seconds_until_rate_reset(self, response: requests.Response) -> float | None:
        reset_raw = response.headers.get("X-Rate-Limit-Reset")
        if reset_raw:
            try:
                wait = int(reset_raw) - time.time() + CLICKSIGN_RATE_LIMIT_BUFFER_SEC
                return max(wait, 0.5)
            except ValueError:
                pass
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after) + CLICKSIGN_RATE_LIMIT_BUFFER_SEC, 0.5)
            except ValueError:
                pass
        return None

    def _request(self, method: str, path: str, ctx: str, **kwargs) -> requests.Response:
        url = self._url(path)
        response = None
        for attempt in range(1, CLICKSIGN_RATE_LIMIT_MAX_RETRIES + 1):
            response = self.session.request(method, url, **kwargs)
            if response.status_code != 429:
                return response

            wait = self._seconds_until_rate_reset(response)
            if wait is None:
                wait = min(2**attempt, 30)
            remaining = response.headers.get("X-Rate-Limit-Remaining", "?")
            reset_at = response.headers.get("X-Rate-Limit-Reset", "?")
            print(
                f"[!] Clicksign rate limit em {ctx} "
                f"(tentativa {attempt}/{CLICKSIGN_RATE_LIMIT_MAX_RETRIES}, "
                f"remaining={remaining}, reset={reset_at}). "
                f"Aguardando {wait:.1f}s..."
            )
            time.sleep(wait)

        assert response is not None
        self._raise(response, ctx)
        return response

    def _raise(self, r, ctx):
        if not r.ok:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise RuntimeError(f"[Clicksign] {ctx} -> {r.status_code}: {body}")

    def create_envelope(self, name: str):
        payload = {
            "data": {
                "type": "envelopes",
                "attributes": {
                    "name": name,
                    "locale": "pt-BR",
                    "auto_close": True,
                    "block_after_refusal": True,
                },
            }
        }
        r = self._request("POST", "/envelopes", "create_envelope", json=payload)
        self._raise(r, "create_envelope")
        return r.json()["data"]["id"]

    def upload_document_base64(self, envelope_id, file_path):
        print("[*] Upload documento (V3)...")
        with open(file_path, "rb") as f:
            raw = base64.b64encode(f.read()).decode()
        header = "data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,"
        payload = {
            "data": {
                "type": "documents",
                "attributes": {
                    "filename": os.path.basename(file_path),
                    "content_base64": header + raw,
                },
            }
        }
        r = self._request(
            "POST",
            f"/envelopes/{envelope_id}/documents",
            "upload_document",
            json=payload,
        )
        self._raise(r, "upload_document")
        return r.json()["data"]["id"]

    def create_signer(self, envelope_id, name, email, group_number):
        payload = {
            "data": {
                "type": "signers",
                "attributes": {
                    "name": name,
                    "email": email,
                    "group": group_number,
                    "communicate_events": {
                        "signature_request": "email",
                        "signature_reminder": "email",
                        "document_signed": "email",
                    },
                },
            }
        }
        r = self._request(
            "POST",
            f"/envelopes/{envelope_id}/signers",
            "create_signer",
            json=payload,
        )
        self._raise(r, "create_signer")
        return r.json()["data"]["id"]

    def create_sign_requirement(self, envelope_id, signer_id, document_id):
        payload = {
            "data": {
                "type": "requirements",
                "attributes": {"action": "agree", "role": "sign"},
                "relationships": {
                    "document": {"data": {"type": "documents", "id": document_id}},
                    "signer": {"data": {"type": "signers", "id": signer_id}},
                },
            }
        }
        r = self._request(
            "POST",
            f"/envelopes/{envelope_id}/requirements",
            "create_sign_requirement",
            json=payload,
        )
        self._raise(r, "create_sign_requirement")

    def create_auth_requirement(self, envelope_id, signer_id, document_id):
        payload = {
            "data": {
                "type": "requirements",
                "attributes": {"action": "provide_evidence", "auth": "email"},
                "relationships": {
                    "signer": {"data": {"type": "signers", "id": signer_id}},
                    "document": {"data": {"type": "documents", "id": document_id}},
                },
            }
        }
        r = self._request(
            "POST",
            f"/envelopes/{envelope_id}/requirements",
            "create_auth_requirement",
            json=payload,
        )
        self._raise(r, "create_auth_requirement")

    def activate_envelope(self, envelope_id):
        payload = {
            "data": {
                "id": envelope_id,
                "type": "envelopes",
                "attributes": {"status": "running"},
            }
        }
        r = self._request(
            "PATCH", f"/envelopes/{envelope_id}", "activate_envelope", json=payload
        )
        self._raise(r, "activate_envelope")

    def notify_signer_manual(self, envelope_id, signer_id):
        payload = {
            "data": {
                "type": "notifications",
                "attributes": {"message": "Sua vez de assinar o contrato."},
            }
        }
        r = self._request(
            "POST",
            f"/envelopes/{envelope_id}/signers/{signer_id}/notifications",
            "notify_signer",
            json=payload,
        )
        self._raise(r, "notify_signer")

    def get_envelope_status(self, envelope_id: str) -> str | None:
        r = self._request(
            "GET", f"/envelopes/{envelope_id}", "get_envelope_status"
        )
        if not r.ok:
            return None
        return r.json().get("data", {}).get("attributes", {}).get("status")


# ---------- FLUXO RÁPIDO (FIRE & FORGET COM GRUPOS) ----------
def clicksign_fire_and_forget(doc_path: str, envelope_name: str, sign_sequence: list):
    cs = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)

    print(f"[*] 1. Criando envelope '{envelope_name}'...")
    envelope_id = cs.create_envelope(envelope_name)

    print("[*] 2. Upload do documento...")
    document_id = cs.upload_document_base64(envelope_id, doc_path)

    print(
        f"[*] 3. Configurando {len(sign_sequence)} signatários (Sequencial por Grupos)..."
    )
    first_signer_id = None

    for i, person in enumerate(sign_sequence):
        group_num = i + 1
        signer_id = cs.create_signer(
            envelope_id, person["name"], person["email"], group_num
        )
        cs.create_sign_requirement(envelope_id, signer_id, document_id)
        cs.create_auth_requirement(envelope_id, signer_id, document_id)

        if i == 0:
            first_signer_id = signer_id
        print(
            f"    > {person['name']} ({person['email']}) adicionado ao Grupo {group_num}."
        )

    print("[*] 4. Ativando envelope...")
    cs.activate_envelope(envelope_id)

    if first_signer_id:
        print("[*] Disparando notificação para o Grupo 1...")
        cs.notify_signer_manual(envelope_id, first_signer_id)

    print(f"[v] Envelope {envelope_id} ativado! Fluxo sequencial automático iniciado.")
    return envelope_id


# ---------- GERAÇÃO DO CONTRATO ----------
def fill_contract(deal_data):
    if not os.path.exists(MODELO_DOCX):
        print(f"[!] Erro: Modelo '{MODELO_DOCX}' não encontrado.")
        return None
    try:
        doc = DocxTemplate(MODELO_DOCX)
    except Exception as e:
        print(f"[!] Erro ao abrir docx: {e}")
        return None

    p1 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P1)
    p2 = get_val(deal_data, FIELD_NUMERO_CONTRATO_P2)
    qtd_sole = get_val(deal_data, FIELD_QTD_SOLE)

    raw_dt_implantacao = get_val(deal_data, FIELD_DATA_IMPLANTACAO)
    dt_implantacao = (
        formatar_data_ptbr(raw_dt_implantacao) if raw_dt_implantacao else "A definir"
    )

    raw_dt_primeira_cobranca = get_val(deal_data, FIELD_DATA_PRIMEIRA_COBRANCA)
    dt_primeira_cobranca = (
        formatar_data_ptbr(raw_dt_primeira_cobranca)
        if raw_dt_primeira_cobranca
        else "A definir"
    )

    documento_pipe = get_val(deal_data, FIELD_DOCUMENTO)
    nome_pipe = get_val(deal_data, FIELD_NOME_CLIENTE)
    parceiro_plune = None
    try:
        parceiro_plune = buscar_parceiro_plune_por_documento(documento_pipe, nome_pipe)
    except PluneError as e:
        print(f"[!] Aviso: busca Plune por CNPJ falhou ({e}); usando dados do Pipedrive no contrato.")

    if parceiro_plune:
        nome_cliente = parceiro_plune.get("razao_social") or nome_pipe
        endereco = parceiro_plune.get("endereco") or get_val(deal_data, FIELD_ENDERECO)
        cidade = parceiro_plune.get("cidade") or get_val(deal_data, FIELD_CIDADE)
        documento = parceiro_plune.get("documento_formatado") or documento_pipe
        print(f"[*] Contrato com dados do Plune: {nome_cliente} ({documento})")
    else:
        nome_cliente = nome_pipe
        endereco = get_val(deal_data, FIELD_ENDERECO)
        cidade = get_val(deal_data, FIELD_CIDADE)
        documento = documento_pipe

    contexto = {
        "numero_contrato": f"CGRc{p1}i{p2}n1r0a26",
        "nome_cliente": nome_cliente,
        "endereco": endereco,
        "cidade": cidade,
        "documento": documento,
        "sole_web": numero_por_extenso_unidades(qtd_sole),
        "valor_mensal": formatar_moeda(get_val(deal_data, FIELD_VALOR_MENSAL)),
        "valor_implantacao": formatar_moeda(
            get_val(deal_data, FIELD_VALOR_IMPLANTACAO)
        ),
        "data_hoje": datetime.now().strftime("%d/%m/%Y"),
        "data_inicio": formatar_data_ptbr(
            deal_data.get("won_time") or deal_data.get("add_time")
        ),
        "indicadores_qualidade": get_val(deal_data, FIELD_INDICADORES_QUALIDADE),
        "qualidade_energia": get_val(deal_data, FIELD_QUALIDADE_ENERGIA),
        "data_pagamento_implantacao": dt_implantacao,
        "data_pagamento_primeira_cobranca": dt_primeira_cobranca,
        "contato_gestor": get_val(deal_data, FIELD_CONTATO_GESTOR),
        "contato_financeiro": get_val(deal_data, FIELD_CONTATO_FINANCEIRO),
        "contato_contratante": get_val(deal_data, FIELD_CONTATO_CONTRATANTE),
    }

    clean_title = str(deal_data.get("title", "SemTitulo")).replace("/", "-")
    nome_saida = f"{PASTA_SAIDA}/Contrato_{deal_data['id']}_{clean_title}.docx"
    doc.render(contexto)
    doc.save(nome_saida)
    print(f"[v] Contrato Gerado: {nome_saida}")
    return nome_saida


# ---------- NOVO FLUXO: POLLING DA API ----------
def buscar_deals_ganhos():
    """Faz a requisição para a API do Pipedrive buscando os deals ganhos."""
    url = "https://api.pipedrive.com/api/v2/deals"
    params = {"status": "won"}
    headers = {"x-api-token": API_TOKEN}

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"[!] Erro ao buscar deals: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[!] Falha na conexão com Pipedrive: {e}")
        return []


def processar_deals_pendentes():
    """Função principal executada a cada ciclo do loop."""
    deals = buscar_deals_ganhos()
    if not deals:
        return

    deals_processados = carregar_deals_processados()

    for deal in deals:
        deal_id = str(deal.get("id"))
        won_time_str = deal.get("won_time")

        if not won_time_str or deal_id in deals_processados:
            continue

        try:
            won_time_dt = datetime.strptime(won_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            print(f"[!] Formato de data desconhecido no deal {deal_id}: {won_time_str}")
            continue

        if won_time_dt < DATA_INICIO_SCRIPT:
            continue

        print(
            f"\n[!] NOVO DEAL GANHO DETECTADO! Deal ID: {deal_id} | Título: {deal.get('title')}"
        )

        try:
            print(f"    -> Gerando contrato...")
            doc_path = fill_contract(deal)

            sequence_dinamica = extrair_signatarios(deal)

            if doc_path:
                if len(sequence_dinamica) > 0:
                    print(f"    -> Enviando para Clicksign...")
                    envelope_name = f"Contrato Deal {deal_id} - {deal.get('title')}"

                    envelope_id = clicksign_fire_and_forget(
                        doc_path, envelope_name, sequence_dinamica
                    )

                    salvar_envelope_pendente(deal_id, envelope_id, envelope_name)
                    salvar_deal_processado(deal_id)
                    print(
                        f"[v] Sucesso! Contrato enviado. Deal ID {deal_id} salvo no log."
                    )

                    if TESTE_PLUNE_SEM_ASSINATURA:
                        print(f"    -> [TESTE] Criando pedido Plune sem aguardar assinaturas...")
                        try:
                            result = criar_pedido_plune(deal_id)
                            print(f"[v] Pedido Plune: {result}")
                        except PluneError as exc:
                            print(f"[!] Erro ao criar pedido Plune (deal {deal_id}): {exc}")
                else:
                    print(
                        "[!] Nenhum e-mail de signatário encontrado no Deal. Contrato não enviado para assinatura."
                    )

        except Exception as e:
            print(f"[!] Erro ao processar Deal {deal_id}: {e}")


def processar_contratos_assinados():
    """Quando o envelope Clicksign fechou (todos assinaram), cria o pedido no Plune."""
    if TESTE_PLUNE_SEM_ASSINATURA:
        return

    pendentes = listar_aguardando_pedido_plune()
    if not pendentes:
        return

    cs = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)

    for record in pendentes:
        deal_id = str(record.get("deal_id"))
        envelope_id = record.get("envelope_id")
        status = cs.get_envelope_status(envelope_id)
        if status != "closed":
            continue

        print(f"\n[!] Contrato assinado! Deal {deal_id} → criando pedido no Plune...")
        try:
            result = criar_pedido_plune(deal_id)
            print(f"[v] Pedido Plune: {result}")
        except PluneError as exc:
            print(f"[!] Erro ao criar pedido Plune (deal {deal_id}): {exc}")


def main():
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)

    print("--- INICIANDO AUTOMACAO (PIPEDRIVE -> CLICKSIGN -> PLUNE) ---")
    print(
        f"[*] Script iniciado em: {DATA_INICIO_SCRIPT.strftime('%d/%m/%Y %H:%M:%S')} UTC"
    )
    print(f"[*] Apenas deals ganhos após este momento serão processados.")
    if TESTE_PLUNE_SEM_ASSINATURA:
        print("[*] MODO TESTE: pedido Plune criado logo após envio ao Clicksign (sem assinaturas).")
    print(
        f"[*] Verificando Pipedrive a cada {INTERVALO_POLLING_SEGUNDOS} segundos...\n"
    )

    try:
        while True:
            processar_deals_pendentes()
            processar_contratos_assinados()
            time.sleep(INTERVALO_POLLING_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n[!] Automação encerrada pelo usuário.")


if __name__ == "__main__":
    main()
