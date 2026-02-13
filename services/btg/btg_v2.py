import os
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

BTG_CLIENT_ID = os.getenv("BTG_CLIENT_ID")
BTG_CLIENT_SECRET = os.getenv("BTG_CLIENT_SECRET")
BTG_CNPJ = os.getenv("BTG_CNPJ")
BTG_BASE_URL = os.getenv("BTG_BASE_URL")
ENVIAR_PATH = ".env"

_access_token_cache = None


def renovar_token():
    global _access_token_cache

    response = requests.post("https://auth.api-sandbox.btgpactual.com/oauth2/token",
        data = {
            "grant_type": "client_credentials",
            "scope": "banking"
        },

        auth = (BTG_CLIENT_ID, BTG_CLIENT_SECRET)
    )

    response.raise_for_status()
    data = response.json()

    _access_token_cache = data["access_token"]


def _headers():
    if (not _access_token_cache):
        renovar_token()
    
    return {
        "Authorization": f"Bearer {_access_token_cache}",
        "accept": "application/json",
        "content-type": "application/json",
        "x-btg-cnpj": BTG_CNPJ 
    }


def _post(url, payload):
    response = requests.get(url, json = payload, headers = _headers())

    if (response.status_code == 401):
        renovar_token()
        response = requests.get(url, json = payload, headers=_headers())

    return response


def criar_pagamento_btg(payload):
    url = f"{BTG_BASE_URL}/banking/collections"

    response = _post(url, payload)
    return response.json()