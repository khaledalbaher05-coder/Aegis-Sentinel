import requests

def check_wallet_balance(address):
    # استخدام الـ API الخاص بـ TronGrid
    url = f"https://api.trongrid.io/v1/accounts/{address}"
    headers = {"TRON-PRO-API-KEY": "أدخل الـ API KEY الخاص بك هنا"}
    
    response = requests.get(url, headers=headers).json()
    
    if "data" in response and len(response["data"]) > 0:
        balance_sun = response["data"][0].get("balance", 0)
        return balance_sun / 1000000  # تحويل من Sun إلى USDT
    return 0
