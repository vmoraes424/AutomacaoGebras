import time
import json
import os
import requests
import base64
from datetime import datetime
from selenium import webdriver
from docxtpl import DocxTemplate

# --- CONFIGURAÇÕES ---
API_TOKEN = "469c97918264d07279f03fe60378daaf8eff2b6a"
XPATH_BOTAO_GANHO = "//button[@data-testid='won-button']"
MODELO_DOCX = "contrato_padrao.docx"
PASTA_SAIDA = "./contratos"

CLICKSIGN_ACCESS_TOKEN = "e8963e51-df88-4455-b19b-5a33098e7a5b"
CLICKSIGN_BASE_URL = "https://app.clicksign.com/api/v3"

# Lista sequencial (A ordem da lista define a ordem de envio)
SIGN_SEQUENCE = [
    {"name": "Vinicius Moraes", "email": "vmoraes424@gmail.com"},  # Grupo 1
    {"name": "Z Cansado Ninja", "email": "zcansadoninja@gmail.com"},  # Grupo 2
    {"name": "HGs Pop", "email": "hgspop@gmail.com"},  # Grupo 3
]

FINAL_NOTIFY_EMAIL = "vmoraes424@gmail.com"


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


def get_deal_data(deal_id):
    url = f"https://api.pipedrive.com/api/v2/deals/{deal_id}"
    headers = {"x-api-token": API_TOKEN}
    print(f"[*] Consultando API para Deal ID: {deal_id}...")
    r = requests.get(url, headers=headers)
    return r.json().get("data") if r.status_code == 200 else None


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

    # [ALTERAÇÃO 1] Adicionado parâmetro 'group'
    def create_signer(self, envelope_id, name, email, group_number):
        payload = {
            "data": {
                "type": "signers",
                "attributes": {
                    "name": name,
                    "email": email,
                    "group": group_number,  # Define a ordem sequencial (1, 2, 3...)
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

    # Notificação manual (só para o primeiro da fila, para garantir o start)
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
def clicksign_fire_and_forget(doc_path: str, envelope_name: str):
    cs = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)

    print(f"[*] 1. Criando envelope '{envelope_name}'...")
    envelope_id = cs.create_envelope(envelope_name)

    print("[*] 2. Upload do documento...")
    document_id = cs.upload_document_base64(envelope_id, doc_path)

    print("[*] 3. Configurando signatários (Sequencial por Grupos)...")
    first_signer_id = None

    # [ALTERAÇÃO 2] Loop usando enumerate para gerar grupos sequenciais (1, 2, 3...)
    for i, person in enumerate(SIGN_SEQUENCE):
        group_num = i + 1  # Vinicius = 1, Z Cansado = 2, HGs = 3

        signer_id = cs.create_signer(
            envelope_id, person["name"], person["email"], group_num
        )
        cs.create_sign_requirement(envelope_id, signer_id, document_id)
        cs.create_auth_requirement(envelope_id, signer_id, document_id)

        if i == 0:
            first_signer_id = signer_id
        print(f"    > {person['name']} adicionado ao Grupo {group_num}.")

    print("[*] 4. Ativando envelope...")
    cs.activate_envelope(envelope_id)

    # IMPORTANTE: No modelo de grupos, ao ativar o envelope, a Clicksign
    # deve enviar automaticamente para o Grupo 1.
    # Mas como estamos usando API, as vezes é bom dar o 'peteleco' inicial.
    if first_signer_id:
        print("[*] Disparando notificação para o Grupo 1...")
        cs.notify_signer_manual(envelope_id, first_signer_id)

    print(f"[v] Envelope {envelope_id} ativado! Fluxo sequencial automático iniciado.")
    # Agora a Clicksign gerencia: Quando G1 assinar, ela notifica G2 automaticamente.
    return envelope_id


# ---------- GERAÇÃO DO CONTRATO (MANTIDA) ----------
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
    }

    clean_title = str(deal_data.get("title", "SemTitulo")).replace("/", "-")
    nome_saida = f"{PASTA_SAIDA}/Contrato_{deal_data['id']}_{clean_title}.docx"
    doc.render(contexto)
    doc.save(nome_saida)
    print(f"[v] Contrato Gerado: {nome_saida}")
    return nome_saida


# ---------- EXECUÇÃO PRINCIPAL ----------
# ---------- EXECUÇÃO PRINCIPAL (OTIMIZADA PARA MÚLTIPLOS DEALS) ----------
def main():
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)

    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    print("--- AUTOMACAO V2 (PIPEDRIVE -> CLICKSIGN FIRE & FORGET) ---")
    print("[i] Aguardando login e navegação para um Deal...")
    driver.get("https://gebras.pipedrive.com/")

    # JS de monitoramento (O mesmo de antes)
    inject_js = f"""
    let btn = document.evaluate("{XPATH_BOTAO_GANHO}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if (btn) {{
        if (!btn.hasAttribute('data-listener-attached')) {{
            btn.addEventListener('click', function() {{ window.buttonClicked = true; }});
            btn.setAttribute('data-listener-attached', 'true');
            return true;
        }}
    }}
    return false;
    """

    last_url = ""
    listener_attached = False

    try:
        while True:
            current_url = driver.current_url

            # [CORREÇÃO CRÍTICA]: Se mudou de página (foi pra outro Deal), reseta o monitoramento
            if current_url != last_url:
                listener_attached = False
                last_url = current_url
                # Se saiu de um deal, reseta a flag de clique pra garantir
                try:
                    driver.execute_script("window.buttonClicked = false;")
                except:
                    pass

            # Se estamos em uma página de Deal e ainda não "grudamos" no botão dessa página específica
            if "/deal/" in current_url and not listener_attached:
                try:
                    attached = driver.execute_script(inject_js)
                    if attached:
                        print(
                            f"[*] Monitorando botão neste Deal ({current_url.split('/deal/')[1].split('?')[0]})..."
                        )
                        listener_attached = True
                except:
                    # Botão pode não ter carregado ainda, tenta no próximo loop
                    pass

            # Se já estamos monitorando, verifica se houve clique
            if listener_attached:
                try:
                    clicked = driver.execute_script("return window.buttonClicked;")
                    if clicked:
                        print("\n[!] GANHO DETECTADO! Iniciando automação...")

                        # Reseta o clique imediatamente para não disparar 2x
                        driver.execute_script("window.buttonClicked = false;")

                        # Extrai ID
                        deal_id = (
                            current_url.split("/deal/")[1].split("?")[0].split("/")[0]
                        )

                        # --- BLOCO DE EXECUÇÃO ---
                        try:
                            print(f"    -> Processando Deal {deal_id}...")
                            data = get_deal_data(deal_id)

                            if data:
                                doc_path = fill_contract(data)
                                if doc_path:
                                    # Envia para Clicksign e libera
                                    clicksign_fire_and_forget(
                                        doc_path, f"Contrato Deal {deal_id}"
                                    )
                                    print(
                                        f"[v] Sucesso! Pode ir para o próximo Deal.\n"
                                    )

                        except Exception as e:
                            print(f"[!] Erro ao processar Deal {deal_id}: {e}")
                            print(
                                "[!] O script continua rodando. Tente novamente ou vá para o próximo."
                            )

                        # Pequena pausa para garantir que a UI do Pipedrive estabilize
                        time.sleep(1)

                except Exception as e:
                    # Se der erro ao checar o clique (ex: página mudou no meio), reseta
                    listener_attached = False

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nFim da automação.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
