import os
import requests
from dotenv import load_dotenv

load_dotenv()

GRAFENO_API_KEY = os.getenv("GRAFENO_API_KEY")
ACCOUNT_NUMBER = os.getenv("GRAFENO_ACCOUNT_NUMBER")
BASE_URL = "https://pagamentos.grafeno.be/api/v2"


def buscar_cobrancas():
    url = f"{BASE_URL}/charges"

    headers = {
        "Authorization": GRAFENO_API_KEY,
        "Account-Number": ACCOUNT_NUMBER,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    return response.json()


def criar_charge(payload):
    url = f"{BASE_URL}/charges"

    headers = {
        "Authorization": GRAFENO_API_KEY,
        "Account-Number": ACCOUNT_NUMBER,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json = payload, headers = headers)

    response.raise_for_status()

    return response.json()
