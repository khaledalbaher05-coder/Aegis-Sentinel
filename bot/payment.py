import requests
import os
from dotenv import load_dotenv

load_dotenv()

WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
API_KEY = os.getenv('TRONGRID_API_KEY')

def check_for_payment(amount_expected):
    url = f"https://api.trongrid.io/v1/accounts/{WALLET_ADDRESS}/transactions/trc20"
    headers = {"TRON-PRO-API-KEY": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        for tx in data.get('data', []):
            if tx['to'] == WALLET_ADDRESS:
                # التأكد من المبلغ (بالـ decimals الخاص بـ USDT وهو 6)
                if (int(tx['value']) / 1000000) >= amount_expected:
                    return True
        return False
    except:
        return False
