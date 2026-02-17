import requests

# CONFIG
ACCESS_TOKEN = "e8963e51-df88-4455-b19b-5a33098e7a5b"
BASE_URL = "https://app.clicksign.com/api/v3"

# URL DO SEU SERVIDOR (Use webhook.site para testar se não tiver server ainda)
# Exemplo: "https://webhook.site/seu-uuid-unico"
URL_WEBHOOK = "https://webhook.site/70859493-04d8-4842-9820-ba23feb1f96a"


def criar_webhook():
    url = f"{BASE_URL}/webhooks?access_token={ACCESS_TOKEN}"

    headers = {"Accept": "application/json", "Content-Type": "application/vnd.api+json"}

    # Eventos: 'auto_close' dispara quando TODOS assinam e o envelope fecha.
    payload = {
        "data": {
            "type": "webhooks",
            "attributes": {
                "endpoint": URL_WEBHOOK,
                "events": ["auto_close", "sign"],  # auto_close = finalizado
                "status": "active",
            },
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Status: {response.status_code}")
    print("Resposta:", response.text)


if __name__ == "__main__":
    criar_webhook()
