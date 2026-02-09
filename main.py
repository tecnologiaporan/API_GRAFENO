from bling import bling
from grafeno import grafeno
from btg import btg
import json


def extrair_dados_bling(conta, banco):
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

    if (banco == "BTG"):
        valor_sem_desconto, desconto_por_parcela, tipo_desconto = calcular_desconto_btg(
            valor_parcela,
            qtd_parcelas,
            valor_desconto,
            tipo_desconto_bling
        )
    
    elif (banco == "GRAFENO"):
        valor_sem_desconto, desconto_por_parcela, tipo_desconto = calcular_desconto_grafeno(
            valor_parcela,
            qtd_parcelas,
            valor_desconto,
            tipo_desconto_bling
        )

    else:
        return None

    dados = {
        # Dados do contas a receber
        "conta_id": conta.get("id"),
        "valor": valor_sem_desconto,
        "vencimento": conta.get("vencimento"),

        # Dados do pedido de venda
        "numero_pedido": f"P {origem.get('numero')}",
        "desconto_type": tipo_desconto,
        "valor_desconto": desconto_por_parcela,

        # Dados do contato do pagador
        "nome": contato.get("nome"),
        "documento": contato.get("numeroDocumento"),
        "tipo_pessoa": contato.get("tipo"),
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
        tipo_desconto = "fixed_value"
        desconto_total = valor_desconto
    
    elif (tipo_desconto_bling == "PERCENTUAL"):
        tipo_desconto = "fixed_value"
        total_sem_desconto_grafeno = (total_com_desconto * 100) / (100 - valor_desconto)
        total_sem_desconto_btg = (total_sem_desconto_grafeno * 40) / 60
        desconto_total = (total_sem_desconto_btg + total_sem_desconto_grafeno) * (valor_desconto / 100)
        
    else:
        desconto_total = 0
        tipo_desconto = "fixed_value"

    desconto_por_parcela = desconto_total * (percentual_grafeno / qtd_parcelas)
    valor_parcela_sem_desconto = valor_parcela + desconto_por_parcela

    return valor_parcela_sem_desconto, desconto_por_parcela, tipo_desconto


def calcular_desconto_btg(valor_parcela, qtd_parcelas, valor_desconto, tipo_desconto_bling, percentual_btg = 0.4):
    if (not valor_desconto or qtd_parcelas <= 0):
        return valor_parcela, 0, "FIXED_VALUE"
    
    total_com_desconto = valor_parcela * qtd_parcelas
    
    if (tipo_desconto_bling == "REAL"):
        tipo_desconto = "FIXED_VALUE"
        desconto_total = valor_desconto
    
    elif (tipo_desconto_bling == "PERCENTUAL"):
        tipo_desconto = "FIXED_VALUE"
        total_sem_desconto_grafeno = (total_com_desconto * 100) / (100 - valor_desconto)
        total_sem_desconto_btg = (total_sem_desconto_grafeno * 60) / 40
        desconto_total = (total_sem_desconto_btg + total_sem_desconto_grafeno) * (valor_desconto / 100)
        
    else:
        desconto_total = 0
        tipo_desconto = "FIXED_VALUE"

    desconto_por_parcela = desconto_total * (percentual_btg / qtd_parcelas)
    valor_parcela_sem_desconto = valor_parcela + desconto_por_parcela

    return valor_parcela_sem_desconto, desconto_por_parcela, tipo_desconto


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


def criar_cobranca_btg(dados):
    payload = {
        "type": "BANKSLIP",
        "payer": {
            "personType": dados["tipo_pessoa"],
            "address": {
                "city": dados["cidade"],
                "state": dados["uf"],
                "zipCode": dados["cep"],
                "street": dados["rua"],
                "number": dados["numero"],
                "neighborhood": dados["bairro"],
                "complement": dados["complemento"]
            },
            "name": dados["nome"],
            "taxId": dados["documento"],
            "email": "email@gmail.com",
            "phoneNumber": dados["telefone"] or dados["celular"]
        },
        "interest": {
            "startDate": dados["vencimento"],
            "type": "PERCENTAGE_PER_MONTH",
            "value": 1
        },
        "fine": {
            "startDate": dados["vencimento"],
            "type": "PERCENTAGE",
            "value": 2
        },
        "discounts": [
            {
                "limitDate": dados["vencimento"],
                "type": "FIXED_VALUE",
                "value": dados["valor_desconto"]
            }

        ] if dados["valor_desconto"] > 0 else [],
        "account": {
            "number": "008305304",
            "branch": "0050"
        },
        "detail": {
            "badCredit": { "type": "NOT_APPLICABLE" },
            "documentNumber": dados["numero_pedido"]
        },
        "amount": dados["valor"],
        "dueDate": dados["vencimento"],
        "overDueDate": dados["vencimento"]
    }

    return payload


ARQUIVO_UNICO = "boletos_gerados.txt"

def salvar_dados_payload(payload):
    try:
        with open(ARQUIVO_UNICO, "a", encoding = "utf-8") as f:
            f.write(json.dumps(payload, indent = 4, ensure_ascii = False))
            f.write("\n\n" + " -=" * 50 + "\n\n")
    
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERRO: {e}")

    print(f"Payload salvo em TXT")


def menu():
    print("-=" * 8, "Menu", "-=" * 8)
    print("1. Emitir Boleto BTG PACTUAL")
    print("2. Emitir Boleto GRAFENO DIGITAL")
    print("3. Sair do programa")

    try:
        opcao = int(input("\nEscolha uma opção: "))

        match (opcao):
            case 1:
                return "BTG"
            
            case 2:
                return "GRAFENO"
            
            case 3:
                return "SAIR"
            
            case _:
                return None
            
    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        print(f"ERRO capturado: {e}")

        
def main():
    banco = menu()

    if (banco == "SAIR".upper()):
        print("Encerrando programa...")
        return

    formas = bling.buscar_formas_pagamento()
    formas_grafeno_ids = set()
    formas_btg_ids = set()

    for forma in formas:
        descricao_bling = forma["descricao"]

        if ("GRAFENO" in descricao_bling):
            formas_grafeno_ids.add(forma["id"])
        
        elif ("BTG" in descricao_bling):
            formas_btg_ids.add(forma["id"])

    print(f"IDs GRAFENO detectados: {formas_grafeno_ids}")
    print(f"IDs BTG detectados: {formas_btg_ids}")

    contas = bling.buscar_contas_receber()

    encontrados = 0

    for conta in contas:
        forma_pag = conta.get("formaPagamento")
        forma_id = forma_pag.get("id")

        if (banco == "GRAFENO" and forma_id not in formas_grafeno_ids):
            continue

        if (banco == "BTG" and forma_id not in formas_btg_ids):
            continue
        
        dados = extrair_dados_bling(conta, banco)

        if (not dados):
            continue

        if (banco == "GRAFENO"):
            payload = criar_cobranca_grafeno(dados)

            try:
                resposta = grafeno.criar_pagamento_grafeno(payload)
                print(f"Boleto criado com sucesso!")

            except Exception as error:
                print(f"Erro ao criar o boleto: {error}")

        elif (banco == "BTG"):
            payload = criar_cobranca_btg(dados)

            try:
                resposta = btg.criar_pagamento_btg(payload)
                print("Boleto criado com sucesso!")

            except Exception as error:
                print(f"Erro ao criar o boleto: {error}")
        
        salvar_dados_payload(payload)
        encontrados += 1
    
    print(f"Quantidade de boletos criados: {encontrados}")


if (__name__ == "__main__"):
    main()