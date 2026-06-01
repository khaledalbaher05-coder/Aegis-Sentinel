import requests

from bot.config import (
    TRON_API_KEY,
    WALLET_ADDRESS
)

HEADERS = {
    "TRON-PRO-API-KEY": TRON_API_KEY
}


def verify_transaction(tx_hash):
    url = f"https://api.trongrid.io/v1/transactions/{tx_hash}/events"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return False, 0

        data = response.json().get("data", [])

        for event in data:

            to_address = event.get("to_address")
            value = event.get("value", 0)

            if to_address and WALLET_ADDRESS[1:] in to_address:

                amount = float(value) / 1_000_000

                return True, amount

        return False, 0

    except requests.exceptions.RequestException as e:
        print(f"[PAYMENT ERROR] {e}")
        return False, 0
