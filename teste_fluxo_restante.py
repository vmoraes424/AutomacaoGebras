import time
import json
import os
import requests
from datetime import datetime

# --- CONFIGURAÇÕES ---
# Vamos usar o Deal 746 (9) que você listou
ENVELOPE_ID_EXISTENTE = "e2361753-aaf0-4fb1-92fb-49512e190749"

CLICKSIGN_ACCESS_TOKEN = "e8963e51-df88-4455-b19b-5a33098e7a5b"
CLICKSIGN_BASE_URL = "https://app.clicksign.com/api/v3"

# Lista sequencial de assinaturas
SIGN_SEQUENCE = [
    {"name": "Vinicius Moraes", "email": "vmoraes424@gmail.com"},
    {"name": "Z Cansado Ninja", "email": "zcansadoninja@gmail.com"},
    {"name": "HGs Pop", "email": "hgspop@gmail.com"},
]

FINAL_NOTIFY_EMAIL = "vmoraes424@gmail.com"


# ---------- CLICKSIGN CLIENT ----------
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

    def get_documents_from_envelope(self, envelope_id):
        print(f"[*] Buscando documentos no envelope {envelope_id}...")
        path = f"/envelopes/{envelope_id}/documents"
        r = self.session.get(self._url(path))
        self._raise(r, "get_documents")

        data = r.json().get("data", [])
        if not data:
            raise RuntimeError("Nenhum documento encontrado neste envelope!")

        doc_id = data[0]["id"]
        print(f"[v] Documento encontrado: ID {doc_id}")
        return doc_id

    # --- FUNÇÃO DE LIMPEZA (NOVA) ---
    def remove_all_signers(self, envelope_id):
        print("[*] Verificando signatários antigos para limpar...")
        path = f"/envelopes/{envelope_id}/signers"
        r = self.session.get(self._url(path))

        if not r.ok:
            return  # Se der erro na listagem, segue o jogo

        signers = r.json().get("data", [])
        if not signers:
            print("[v] Envelope limpo. Nenhum signatário antigo.")
            return

        print(f"[*] Removendo {len(signers)} signatários antigos...")
        for s in signers:
            sid = s["id"]
            del_path = f"/envelopes/{envelope_id}/signers/{sid}"
            r_del = self.session.delete(self._url(del_path))
            if r_del.ok:
                print(f"    - Signatário {sid} removido.")
            else:
                print(f"    ! Falha ao remover {sid}.")

    def create_signer(self, envelope_id, name, email):
        payload = {
            "data": {
                "type": "signers",
                "attributes": {
                    "name": name,
                    "email": email,
                    "has_documentation": True,
                    "group": 1,
                    "communicate_events": {
                        "signature_request": "email",
                        "signature_reminder": "email",
                        "document_signed": "email",
                    },
                },
            }
        }
        path = f"/envelopes/{envelope_id}/signers"
        r = self.session.post(self._url(path), json=payload)
        self._raise(r, "create_signer")
        return r.json()["data"]["id"]

    # Requisito 1: Assinar
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
        path = f"/envelopes/{envelope_id}/requirements"
        r = self.session.post(self._url(path), json=payload)
        self._raise(r, "create_sign_requirement")

    # Requisito 2: Autenticação
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
        path = f"/envelopes/{envelope_id}/requirements"
        r = self.session.post(self._url(path), json=payload)
        self._raise(r, "create_auth_requirement")

    def activate_envelope(self, envelope_id):
        # Verifica status antes
        r_get = self.session.get(self._url(f"/envelopes/{envelope_id}"))
        if r_get.ok:
            status = r_get.json()["data"]["attributes"]["status"]
            if status == "running":
                print("[*] Envelope JÁ está ativo (running).")
                return

        payload = {
            "data": {
                "id": envelope_id,
                "type": "envelopes",
                "attributes": {"status": "running"},
            }
        }
        path = f"/envelopes/{envelope_id}"
        r = self.session.patch(self._url(path), json=payload)
        self._raise(r, "activate_envelope")

    def notify_signer_manual(self, envelope_id, signer_id):
        payload = {
            "data": {
                "type": "notifications",
                "attributes": {"message": "Sua vez de assinar o contrato da BIView."},
            }
        }
        path = f"/envelopes/{envelope_id}/signers/{signer_id}/notifications"
        r = self.session.post(self._url(path), json=payload)

        if r.status_code in [200, 201, 202, 204]:
            print("[v] Notificação enviada com sucesso.")
        else:
            print(f"[!] Erro ao notificar: {r.status_code} - {r.text}")

    def get_envelope_requirements(self, envelope_id):
        r = self.session.get(self._url(f"/envelopes/{envelope_id}/requirements"))
        if r.ok:
            return r.json().get("data", [])
        return []


# ---------- EXECUÇÃO ----------
def main():
    print("--- TESTE FINAL (CLEANUP + AUTH FIX) ---")

    cs = ClicksignClient(CLICKSIGN_BASE_URL, CLICKSIGN_ACCESS_TOKEN)
    envelope_id = ENVELOPE_ID_EXISTENTE
    print(f"[*] Envelope ID: {envelope_id}")

    try:
        # 1. Recuperar Documento (Se falhar aqui, o envelope não tem doc e teremos que criar um novo)
        document_id = cs.get_documents_from_envelope(envelope_id)

        # 2. LIMPEZA: Remove signatários antigos "sujos"
        cs.remove_all_signers(envelope_id)

        # 3. Configurar Novos Signatários
        print("[*] Configurando signatários...")
        signers_map = []

        for person in SIGN_SEQUENCE:
            # Signer
            signer_id = cs.create_signer(envelope_id, person["name"], person["email"])

            # Req 1: Assinar
            cs.create_sign_requirement(envelope_id, signer_id, document_id)

            # Req 2: Auth Email
            cs.create_auth_requirement(envelope_id, signer_id, document_id)

            signers_map.append(
                {
                    "name": person["name"],
                    "email": person["email"],
                    "signer_id": signer_id,
                }
            )
            print(f"    > {person['name']} adicionado.")

        # 4. Ativar Envelope
        print("[*] Ativando envelope...")
        cs.activate_envelope(envelope_id)

        # 5. Fluxo Sequencial
        print("\n--- INICIANDO FLUXO SEQUENCIAL DE ASSINATURAS ---")

        for idx, signer in enumerate(signers_map):
            print(f"\n[*] Vez de: {signer['name']} ({signer['email']})")

            print("    -> Enviando notificação...")
            cs.notify_signer_manual(envelope_id, signer["signer_id"])

            print("    ... Aguardando assinatura ...")
            start_time = time.time()

            while True:
                reqs = cs.get_envelope_requirements(envelope_id)
                current_status = "pending"

                for r in reqs:
                    try:
                        r_sid = r["relationships"]["signer"]["data"]["id"]
                        r_act = r["attributes"].get("action")
                        if r_sid == signer["signer_id"] and r_act == "agree":
                            current_status = r["attributes"].get("status")
                            break
                    except:
                        continue

                if current_status == "signed":
                    print(f"    [v] {signer['name']} assinou!")
                    break
                if current_status == "refused":
                    raise RuntimeError("Recusado!")
                if time.time() - start_time > 3600:
                    raise TimeoutError("Timeout.")

                time.sleep(10)

        print("\n[v] Todos assinaram!")
        print(f"[*] Fim do teste. Notificar: {FINAL_NOTIFY_EMAIL}")

    except Exception as e:
        print(f"\n[!] ERRO CRÍTICO: {e}")


if __name__ == "__main__":
    main()
