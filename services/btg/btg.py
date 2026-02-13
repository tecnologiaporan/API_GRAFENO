import os
import requests
from dotenv import load_dotenv

load_dotenv()

BTG_ACCESS_TOKEN = os.getenv("BTG_ACCESS_TOKEN")
BASE_URL = os.getenv("BTG_BASE_URL")
BTG_CNPJ = os.getenv("BTG_CNPJ")


def listar_contas():
    url = f"{BASE_URL}/{BTG_CNPJ}/banking/accounts"
    
    headers = {
        "Authorization": f"Bearer {BTG_ACCESS_TOKEN}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def criar_pagamento_btg(payload):
    url = f"{BASE_URL}/{BTG_CNPJ}/banking/collections"

    headers = {
        "Authorization": f"Bearer {BTG_ACCESS_TOKEN}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json = payload, headers = headers)
    response.raise_for_status()
    
    return response.json()