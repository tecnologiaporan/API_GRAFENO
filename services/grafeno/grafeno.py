import os
import requests
from dotenv import load_dotenv

load_dotenv()

GRAFENO_API_KEY_P = os.getenv("GRAFENO_API_KEY")
ACCOUNT_NUMBER_P = os.getenv("GRAFENO_ACCOUNT_NUMBER")
BASE_URL_P = os.getenv("GRAFENO_BASE_API")


def buscar_cobrancas():
    url = f"{BASE_URL_P}/charges"

    headers = {
        "Authorization": GRAFENO_API_KEY_P,
        "Account-Number": ACCOUNT_NUMBER_P,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    return response.json()


def criar_pagamento_grafeno(payload):
    url = f"{BASE_URL_P}/charges"

    headers = {
        "Authorization": GRAFENO_API_KEY_P,
        "Account-Number": ACCOUNT_NUMBER_P,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json = payload, headers = headers)
    response.raise_for_status()

    return response.json()