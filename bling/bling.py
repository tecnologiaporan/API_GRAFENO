import os
import requests
from dotenv import load_dotenv

load_dotenv()

BLING_API_KEY = os.getenv("BLING_API_KEY")
BLING_BASE_URL = "https://bling.com.br/Api/v3"


def buscar_contas_receber():
    url = f"{BLING_BASE_URL}/contas/receber"
    headers = {"Authorization": f"Bearer {BLING_API_KEY}"}

    todas_contas = []
    pagina = 1
    limite = 100
    max_paginas = 50

    while (pagina <= max_paginas):
        params = {
            "pagina": pagina,
            "limite": limite,
            "situacoes[]": [1, 3],
            "tipoFiltroData": "E",
            "dataInicial": "2026-02-06",
            "dataFinal": "2026-02-06"
        }

        print(f"🔄 Buscando página {pagina}...")

        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()

        dados = response.json().get("data", [])

        if (not dados):
            print("Nenhum dado retornado. Finalizando busca...")
            break

        if (pagina > 1 and dados[0]["id"] == todas_contas[0]["id"]):
            print("Página repetida detectada. Parando...")
            break

        todas_contas.extend(dados)
        pagina += 1

    print(f"📦 Total de títulos carregados: {len(todas_contas)}\n")
    return todas_contas


def buscar_pedidos_venda(id_pedido):
    url = f"{BLING_BASE_URL}/pedidos/vendas/{id_pedido}"
    headers = {"Authorization": f"Bearer {BLING_API_KEY}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    return response.json().get("data", [])


def buscar_formas_pagamento():
    url = f"{BLING_BASE_URL}/formas-pagamentos"
    headers = {"Authorization": f"Bearer {BLING_API_KEY}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()
    
    return response.json().get("data", [])


def buscar_pedidos():
    url = f"{BLING_BASE_URL}/pedidos/vendas"
    headers = {"Authorization": f"Bearer {BLING_API_KEY}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()
    
    
    return response.json().get("data", [])


def buscar_contato(contato_id):
    url = f"{BLING_BASE_URL}/contatos/{contato_id}"
    headers = {"Authorization": f"Bearer {BLING_API_KEY}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    return response.json().get("data", {})