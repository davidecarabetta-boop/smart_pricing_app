"""
test_alphaposition.py
Esegui con: python test_alphaposition.py

Testa in sequenza:
  1. GET token
  2. GET OffersRanking (prime 3 righe)
"""

import json
import requests

MERCHANT_ID = "sensationprofumerie"
API_KEY = "344890ee-8d6d-4719-96d8-1814bb0ae942"
BASE_URL = "https://services.7pixel.it/api/v1"


def get_token():
    print("\n--- STEP 1: Richiesta token ---")
    url = f"{BASE_URL}/TemporaryToken?merchantid={MERCHANT_ID}&merchantkey={API_KEY}"
    print(f"GET {url}")
    resp = requests.get(url, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    resp.raise_for_status()
    token = resp.json().get("Token")
    print(f"✅ Token: {token}")
    return token


def get_offers_ranking(token):
    print("\n--- STEP 2: OffersRanking ---")
    url = f"{BASE_URL}/OffersRanking?merchantid={MERCHANT_ID}&token={token}&format=json"
    print(f"GET {url}")
    resp = requests.get(url, timeout=60)
    print(f"Status: {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()
    print(f"✅ Prodotti ricevuti: {len(data)}")
    print("\n--- Prime 3 righe ---")
    print(json.dumps(data[:3], indent=2, ensure_ascii=False))
    return data


if __name__ == "__main__":
    token = get_token()
    data = get_offers_ranking(token)