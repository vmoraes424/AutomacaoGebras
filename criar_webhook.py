import requests

from core.config import CLICKSIGN_ACCESS_TOKEN, CLICKSIGN_BASE_URL, CLICKSIGN_WEBHOOK_URL


def criar_webhook():
    if not CLICKSIGN_WEBHOOK_URL:
        raise SystemExit("Defina CLICKSIGN_WEBHOOK_URL no .env")

    url = f"{CLICKSIGN_BASE_URL}/webhooks?access_token={CLICKSIGN_ACCESS_TOKEN}"

    headers = {"Accept": "application/json", "Content-Type": "application/vnd.api+json"}

    payload = {
        "data": {
            "type": "webhooks",
            "attributes": {
                "endpoint": CLICKSIGN_WEBHOOK_URL,
                "events": ["auto_close", "sign"],
                "status": "active",
            },
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Status: {response.status_code}")
    print("Resposta:", response.text)


if __name__ == "__main__":
    criar_webhook()
