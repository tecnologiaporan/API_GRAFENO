from datetime import datetime
from tkinter import messagebox
from services.bling import bling_v2
from services.btg import btg
from services.grafeno import grafeno
from core import geradores 
import log


def buscar_dados_bling(data_inicial = None, data_final = None):
    try:
        data_inicial = datetime.strptime(data_inicial, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_final = datetime.strptime(data_final, "%d/%m/%Y").strftime("%Y-%m-%d")

    except (Exception) as e:
        return None, f"ERRO no formato da data {e}"
    
    contas = bling_v2.buscar_contas_receber(data_inicial, data_final)
    formas = bling_v2.buscar_formas_pagamento()

    formas_pag = {}

    for forma in formas:
        descricao_bling = forma["descricao"]

        if ("Boleto" in descricao_bling):
            formas_pag[forma["id"]] = descricao_bling

    contas_filtradas = []

    for conta in contas:
        forma_id = conta.get("formaPagamento", {}).get("id")

        if (forma_id in formas_pag):
            conta["forma_descricao"] = formas_pag[forma_id]
            contas_filtradas.append(conta)

    return contas_filtradas, "Sucesso"


def processar_boletos(selecionados_indices, selecionados, banco):
    sucessos = 0
    falhas = 0

    for conta_obj in selecionados_indices:
        try:
            dados = bling_v2.extrair_dados_bling(conta_obj, banco)

            if (banco == "GRAFENO"):
                payload = geradores.criar_cobranca_grafeno(dados)
                grafeno.criar_pagamento_grafeno(payload)

            elif (banco == "BTG"):
                payload = geradores.criar_cobranca_btg(dados)
                btg.criar_pagamento_btg(payload)
            
            
            log.gerar_log(dados)
            sucessos += 1
        
        except Exception as e:
            print(f"Erro: {e}")
            falhas += 1
    
    return sucessos, falhas