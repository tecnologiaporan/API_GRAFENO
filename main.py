from bling import bling
from grafeno import grafeno
import json


def extrair_dados_bling(conta):
    origem = conta.get("origem", {})
    contato_id = conta.get("contato", {}).get("id")
    pedido_id = origem.get("id")

    contato = bling.buscar_contato(contato_id)
    pedido = bling.buscar_pedidos_venda(pedido_id)

    parcelas = pedido.get("parcelas", [])
    desconto = pedido.get("desconto", {})
    
    endereco = contato.get("endereco", {}).get("geral", {})

    valor_parcela = conta.get("valor")
    valor_desconto = desconto.get("valor")
    tipo_desconto_bling = desconto.get("unidade")
    
    qtd_parcelas = len(parcelas) // 2

    valor_sem_desconto, desconto_por_parcela, tipo_desconto_grafeno = calcular_desconto_grafeno(
        valor_parcela = valor_parcela,
        qtd_parcelas = qtd_parcelas,
        valor_desconto = valor_desconto,
        tipo_desconto_bling = tipo_desconto_bling
    )

    dados = {
        # Dados do contas a receber
        "conta_id": conta.get("id"),
        "valor": valor_sem_desconto,
        "vencimento": conta.get("vencimento"),

        # Dados do pedido de venda
        "numero_pedido": f"P{origem.get('numero')}",
        "desconto_type": tipo_desconto_grafeno,
        "valor_desconto": desconto_por_parcela,

        # Dados do contato do pagador
        "nome": contato.get("nome"),
        "documento": contato.get("numeroDocumento"),
        "telefone": contato.get("telefone"),
        "celular": contato.get("celular"),
        
        # Dados do endereço do pagador
        "rua": endereco.get("endereco"),
        "numero": endereco.get("numero"),
        "bairro": endereco.get("bairro"),
        "cidade": endereco.get("municipio"),
        "uf": endereco.get("uf"),
        "cep": endereco.get("cep"),
        "complemento": endereco.get("complemento"),
    }
    
    return dados


def calcular_desconto_grafeno(valor_parcela, qtd_parcelas, valor_desconto, tipo_desconto_bling, percentual_grafeno = 0.6):
    if (not valor_desconto or qtd_parcelas <= 0):
        return valor_parcela, 0, "fixed_value"
    
    total_com_desconto = valor_parcela * qtd_parcelas
    
    if (tipo_desconto_bling == "REAL"):
        tipo_desconto_grafeno = "fixed_value"
        desconto_total = valor_desconto
    
    elif (tipo_desconto_bling == "PERCENTUAL"):
        tipo_desconto_grafeno = "fixed_value"
        total_sem_desconto_grafeno = (total_com_desconto * 100) / (100 - valor_desconto)
        total_sem_desconto_btg = (total_sem_desconto_grafeno * 40) / 60
        desconto_total = (total_sem_desconto_btg + total_sem_desconto_grafeno) * (valor_desconto / 100)
        
    else:
        desconto_total = 0
        tipo_desconto_grafeno = "fixed_value"

    desconto_por_parcela = desconto_total * (percentual_grafeno / qtd_parcelas)
    valor_parcela_sem_desconto = valor_parcela + desconto_por_parcela

    return valor_parcela_sem_desconto, desconto_por_parcela, tipo_desconto_grafeno


def criar_cobranca_grafeno(dados):
    payload = {
        "paymentMethod": "boleto",
        "discounts": [
            {
                "discountType": dados["desconto_type"],
                "discountUntil": dados["vencimento"],
                "discountValue": dados["valor_desconto"]
        }
    ] if dados["valor_desconto"] > 0 else [],

        "payer": {
            "address": {
                "street": dados["rua"],
                "neighborhood": dados["bairro"],
                "number": dados["numero"],
                "state": dados["uf"],
                "city": dados["cidade"],
                "zipCode": dados["cep"],
                "complement": dados["complemento"]
            },

            "phone": { 
                "number": dados["telefone"] or dados["celular"]
            },
            "name": dados["nome"],
            "documentNumber": dados["documento"],
            "email": "email@gmail.com"
        },

        "boletoDetails": {
            "registrationMethod": "online",
            "titleType": "trade_bill",
            "yourNumber": dados["numero_pedido"],
            "observation": "Após o vencimento, sujeito a juros de 2% mensal e multa de 1%."
        },

        "grantor": {
            "name": "B.G COMERCIO E DISTRIBUICAO DE PRODUTOS COSMETICOS",
            "documentNumber": "32871376000168"
        },

        "dueDate": dados["vencimento"],
        "abatementValue": 0,
        "value": dados["valor"],
        "interestType": "percentage",
        "interestValue": 2,
        "applicableFine": 1,
        "expiresAfter": 60
    }
    
    return payload


ARQUIVO_UNICO = "boletos_payloads.txt"

def salvar_dados_payload(payload):
    with open(ARQUIVO_UNICO, "a", encoding = "utf-8") as f:
        f.write(json.dumps(payload, indent = 4, ensure_ascii = False))
        f.write("\n\n" + " = " * 80 + "\n\n")

    print(f"Payload salvo em TXT")

        
def main():
    formas = bling.buscar_formas_pagamento()

    formas_grafeno_ids = set()

    for forma in formas:
        if ("GRAFENO" in forma["descricao"].upper()):
            formas_grafeno_ids.add(forma["id"])

    if (not formas_grafeno_ids):
        print("Nenhuma forma GRAFENO encontrada...")
        return

    print(f"IDs GRAFENO detectados: {formas_grafeno_ids}")

    contas = bling.buscar_contas_receber()

    encontrados = 0

    for conta in contas:
        forma_pag = conta.get("formaPagamento")

        if (not forma_pag or forma_pag.get("id") not in formas_grafeno_ids):
            continue
        
        dados = extrair_dados_bling(conta)

        if (not dados):
            continue

        payload = criar_cobranca_grafeno(dados)
        salvar_dados_payload(payload)

        try:
            resposta = grafeno.criar_charge(payload)
            print(f"Boleto criado com sucesso: {resposta}")
        
            encontrados += 1

        except Exception as error:
            print(f"Erro ao criar o boleto: {error}")
  
    
    print(f"Quantidade de boletos criados: {encontrados}")


if (__name__ == "__main__"):
    main()
