import time
import os
import requests
import base64
from datetime import datetime, timezone
from docxtpl import DocxTemplate

# --- CONFIGURAÇÕES ---
API_TOKEN = "469c97918264d07279f03fe60378daaf8eff2b6a"
MODELO_DOCX = "contrato_padrao.docx"
PASTA_SAIDA = "./contratos"

CLICKSIGN_ACCESS_TOKEN = "541dc480-3b74-4dc6-99f7-b0b44de5ad67"
CLICKSIGN_BASE_URL = "https://app.clicksign.com/api/v3"

# Configurações do Polling
INTERVALO_POLLING_SEGUNDOS = 30  # Verifica a cada 1 minuto
ARQUIVO_DEALS_PROCESSADOS = "deals_processados.txt"

# Define a data/hora de início do script em UTC para comparar com o won_time do Pipedrive
DATA_INICIO_SCRIPT = datetime.now(timezone.utc)


# ---------- GERENCIAMENTO DE ESTADO ----------
def carregar_deals_processados():
    if not os.path.exists(ARQUIVO_DEALS_PROCESSADOS):
        return set()
    with open(ARQUIVO_DEALS_PROCESSADOS, "r") as f:
        return set(line.strip() for line in f if line.strip())


def salvar_deal_processado(deal_id):
    with open(ARQUIVO_DEALS_PROCESSADOS, "a") as f:
        f.write(f"{deal_id}\n")


# ---------- FUNÇÕES AUXILIARES ----------
def formatar_moeda(valor):
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(valor)


def formatar_data_ptbr(data_iso):
    if not data_iso:
        return datetime.now().strftime("%d/%m/%Y")
    try:
        data_str = str(data_iso).split("T")[0]
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)


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


# ---------- EXTRAÇÃO DINÂMICA DE SIGNATÁRIOS ----------
def extrair_signatarios(deal_data):
    """
    Extrai os signatários dos custom_fields do Pipedrive na ordem exata necessária.
    """
    cf = deal_data.get("custom_fields", {})

    ordem_chaves = [
        ("Coordenador Principal", "92359b129485b08fd024b8c28ef022e7635419a3"),
        ("Contato Principal", "a23ea2d277d95f8fa1c3d02d1db36a032be7f4a6"),
        ("Gestor Gebras", "ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"),
        ("Diretor Principal", "35cc64cc4f30bc9df0a919cc61b42f69a2b4f1c2"),
    ]

    sign_sequence = []
    for nome_cargo, chave in ordem_chaves:
        email = cf.get(chave)
        if email and str(email).strip() != "":
            sign_sequence.append({"name": nome_cargo, "email": str(email).strip()})

    return sign_sequence


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

    def _raise(self, r, ctx):
        if not r.ok:
            try:
                body = r.json()
            except:
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
        r = self.session.post(self._url("/envelopes"), json=payload)
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
        r = self.session.post(
            self._url(f"/envelopes/{envelope_id}/documents"), json=payload
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
        r = self.session.post(
            self._url(f"/envelopes/{envelope_id}/signers"), json=payload
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
        r = self.session.post(
            self._url(f"/envelopes/{envelope_id}/requirements"), json=payload
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
        r = self.session.post(
            self._url(f"/envelopes/{envelope_id}/requirements"), json=payload
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
        r = self.session.patch(self._url(f"/envelopes/{envelope_id}"), json=payload)
        self._raise(r, "activate_envelope")

    def notify_signer_manual(self, envelope_id, signer_id):
        payload = {
            "data": {
                "type": "notifications",
                "attributes": {"message": "Sua vez de assinar o contrato."},
            }
        }
        self.session.post(
            self._url(f"/envelopes/{envelope_id}/signers/{signer_id}/notifications"),
            json=payload,
        )


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

    cf = deal_data.get("custom_fields", {})

    def get_val(code):
        v = cf.get(code)
        if isinstance(v, dict):
            return str(v.get("value", ""))
        return str(v) if v is not None else ""

    p1 = get_val("14720dca0fd36e1e5b47f8d3d71f3f3868b0df9b")
    p2 = get_val("41a3157128d51e2fc803eeec4b242efafcb55b4e")
    qtd_sole = get_val("f9923cdce1274da8c10cec1b9ab561e024504620")

    raw_dt_implantacao = get_val("2b8f62a107891e26390459cfa4048b3eedade11b")
    dt_implantacao = (
        formatar_data_ptbr(raw_dt_implantacao) if raw_dt_implantacao else "A definir"
    )

    raw_dt_primeira_cobranca = get_val("f5f69ea52e5f65b37c9672fdb4dcfb3b6a4cdbb2")
    dt_primeira_cobranca = (
        formatar_data_ptbr(raw_dt_primeira_cobranca)
        if raw_dt_primeira_cobranca
        else "A definir"
    )

    contexto = {
        "numero_contrato": f"CGRc{p1}i{p2}n1r0a26",
        "nome_cliente": get_val("28d491e0263008b437e28fc55bbad8302c4646c8"),
        "endereco": get_val("81566ac6e038bb0ba3adfa122c798b3e497b7538"),
        "cidade": get_val("2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5"),
        "documento": get_val("176d2a0d5167d1edc9b949c75f8b9a7597eabe91"),
        "sole_web": numero_por_extenso_unidades(qtd_sole),
        "valor_mensal": formatar_moeda(
            get_val("c5dfc907c53bb12ca916f9d0d20df23e3847e54d")
        ),
        "valor_implantacao": formatar_moeda(
            get_val("015407d5106c321a227f1ca881f920fe2e1042ec")
        ),
        "data_hoje": datetime.now().strftime("%d/%m/%Y"),
        "data_inicio": formatar_data_ptbr(
            deal_data.get("won_time") or deal_data.get("add_time")
        ),
        "indicadores_qualidade": get_val("ffb2d5aec9acdee5a242ca19683bbf4caa24cd53"),
        "qualidade_energia": get_val("c0a23912d889e00f51ed5bd08a55856a7e5dc930"),
        "data_pagamento_implantacao": dt_implantacao,
        "data_pagamento_primeira_cobranca": dt_primeira_cobranca,
        "contato_gestor": get_val("ecb0e3a2cb2dbbc8c0caf9e695930f594406c80b"),
        "contato_financeiro": get_val("722da69afe31c1f8fa4f5457a223e2a952ae0978"),
        "contato_contratante": get_val("3002b2df87f0577585ebaec394fd09a38ca8778f"),
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

                    clicksign_fire_and_forget(
                        doc_path, envelope_name, sequence_dinamica
                    )

                    salvar_deal_processado(deal_id)
                    print(
                        f"[v] Sucesso! Contrato enviado. Deal ID {deal_id} salvo no log."
                    )
                else:
                    print(
                        "[!] Nenhum e-mail de signatário encontrado no Deal. Contrato não enviado para assinatura."
                    )
                    # Se não foi enviado porque falta email, podes decidir se salvas ou não no log.
                    # Se não salvares, ele vai tentar enviar de novo no próximo polling (útil se o user preencher o email depois).

        except Exception as e:
            print(f"[!] Erro ao processar Deal {deal_id}: {e}")


def main():
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)

    print("--- INICIANDO AUTOMACAO V3 (POLLING PIPEDRIVE -> CLICKSIGN) ---")
    print(
        f"[*] Script iniciado em: {DATA_INICIO_SCRIPT.strftime('%d/%m/%Y %H:%M:%S')} UTC"
    )
    print(f"[*] Apenas deals ganhos após este momento serão processados.")
    print(
        f"[*] Verificando Pipedrive a cada {INTERVALO_POLLING_SEGUNDOS} segundos...\n"
    )

    try:
        while True:
            processar_deals_pendentes()
            time.sleep(INTERVALO_POLLING_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n[!] Automação encerrada pelo usuário.")


if __name__ == "__main__":
    main()
