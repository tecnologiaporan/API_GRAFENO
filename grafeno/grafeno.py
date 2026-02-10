import os
import requests
from dotenv import load_dotenv

load_dotenv()

GRAFENO_API_KEY = os.getenv("GRAFENO_API_KEY_P")
ACCOUNT_NUMBER = os.getenv("GRAFENO_ACCOUNT_NUMBER_P")
BASE_URL = os.getenv("GRAFENO_BASE_API_P")


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


def criar_pagamento_grafeno(payload):
    url = f"{BASE_URL}/charges"

    headers = {
        "Authorization": GRAFENO_API_KEY,
        "Account-Number": ACCOUNT_NUMBER,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json = payload, headers = headers)

    response.raise_for_status()

    return response.json()