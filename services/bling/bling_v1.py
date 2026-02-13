import os
import requests
import base64
from dotenv import load_dotenv
from config import EMAIL_PADRAO
from core import calculos

load_dotenv()

BLING_API_KEY = os.getenv("BLING_API_KEY")
BLING_BASE_URL = os.getenv("BLING_BASE_URL")


def buscar_contas_receber(data_inicial = None, data_final = None):
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
            "dataInicial": data_inicial,
            "dataFinal": data_final
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