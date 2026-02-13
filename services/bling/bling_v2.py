import os
import requests
from dotenv import load_dotenv, set_key
from config import EMAIL_PADRAO
from core import calculos

load_dotenv()

BLING_CLIENT_ID = os.getenv("BLING_CLIENT_ID")
BLING_CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
BLING_REFRESH_TOKEN = os.getenv("BLING_REFRESH_TOKEN")
BLING_BASE_URL = os.getenv("BLING_BASE_URL")
ENVIAR_PATH = ".env"

_access_token_cache = None


def renovar_token():
    global _access_token_cache, BLING_REFRESH_TOKEN

    response = requests.post("https://bling.com.br/Api/v3/oauth/token",
        data = {
            "grant_type": "refresh_token",
            "refresh_token": BLING_REFRESH_TOKEN
        },

        auth = (BLING_CLIENT_ID, BLING_CLIENT_SECRET)
    )

    response.raise_for_status()
    data = response.json()

    _access_token_cache = data["access_token"]
    BLING_REFRESH_TOKEN = data["refresh_token"]

    set_key(ENVIAR_PATH, "BLING_REFRESH_TOKEN", BLING_REFRESH_TOKEN)


def _headers():
    if (not _access_token_cache):
        renovar_token()
    
    return {"Authorization": f"Bearer {_access_token_cache}"}


def _get(url, ** kwargs):
    response = requests.get(url, headers =_headers(), ** kwargs)

    if (response.status_code == 401):
        renovar_token()
        response = requests.get(url, headers=_headers(), ** kwargs)

    response.raise_for_status()
    return response


def buscar_contas_receber(data_inicial = None, data_final = None):
    url = f"{BLING_BASE_URL}/contas/receber"
    todas_contas = []
    pagina = 1

    while (pagina <= 50):
        params = {
            "pagina": pagina,
            "limite": 100,
            "situacoes[]": [1, 3],
            "tipoFiltroData": "E",
            "dataInicial": data_inicial,
            "dataFinal": data_final 
        }

        print(f"🔄 Buscando página {pagina}...")
        dados = _get(url, params = params).json().get("data", [])

        if (not dados):
            break

        if (pagina > 1 and dados[0]["id"] == todas_contas[0]["id"]):
            print("Página repetida detectada. Parando...")
            break

        todas_contas.extend(dados)
        pagina += 1

    print(f"📦 Total de títulos carregados: {len(todas_contas)}\n")
    return todas_contas


def buscar_pedidos_venda(id_pedido):
    return _get(f"{BLING_BASE_URL}/pedidos/vendas/{id_pedido}").json().get("data", [])


def buscar_formas_pagamento():
    return _get(f"{BLING_BASE_URL}/formas-pagamentos").json().get("data", [])


def buscar_pedidos():
    return _get(f"{BLING_BASE_URL}/pedidos/vendas").json().get("data", [])


def buscar_contato(contato_id):
    return _get(f"{BLING_BASE_URL}/contatos/{contato_id}").json().get("data", {})


def extrair_dados_bling(conta, banco):
    contato = buscar_contato(conta.get("contato", {}).get("id"))
    pedido = buscar_pedidos_venda(conta.get("origem", {}).get("id"))    

    parcelas = pedido.get("parcelas", [])
    desconto = pedido.get("desconto", {})
    
    endereco = contato.get("endereco", {}).get("geral", {})

    valor_parcela = conta.get("valor" or 0)
    total_desconto = desconto.get("valor" or 0)
    tipo_desconto_bling = desconto.get("unidade")
    
    qtd_parcelas = len(parcelas)

    valor_sem_desconto, desconto_final = calculos.calcular_desconto(
        valor_parcela,
        qtd_parcelas,
        total_desconto,
        tipo_desconto_bling,
        banco
    )

    dados = {
        "conta_id": conta.get("id"),
        "valor": valor_sem_desconto,
        "vencimento": conta.get("vencimento"),
        "numero_pedido": f"P {conta.get('origem', {}).get('numero')}",
        "valor_desconto": desconto_final,
        "nome": contato.get("nome"),
        "documento": contato.get("numeroDocumento"),
        "tipo_pessoa": contato.get("tipo").upper(),
        "telefone": contato.get("telefone"),
        "celular": contato.get("celular"),
        "email": contato.get("email") or EMAIL_PADRAO,
        "rua": endereco.get("endereco"),
        "numero": endereco.get("numero"),
        "bairro": endereco.get("bairro"),
        "cidade": endereco.get("municipio"),
        "uf": endereco.get("uf"),
        "cep": endereco.get("cep"),
        "complemento": endereco.get("complemento"),
    }
    
    return dados