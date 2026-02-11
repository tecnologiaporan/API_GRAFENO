from bling import renovar
from grafeno import grafeno
from btg import btg
import json

PERCENTUAL_BTG = 0.40
PERCENTUAL_GRAFENO = 0.60

def extrair_dados_bling(conta, banco):
    origem = conta.get("origem", {})
    contato_id = conta.get("contato", {}).get("id")
    pedido_id = origem.get("id")

    contato = renovar.buscar_contato(contato_id)
    pedido = renovar.buscar_pedidos_venda(pedido_id)    

    parcelas = pedido.get("parcelas", [])
    desconto = pedido.get("desconto", {})
    
    endereco = contato.get("endereco", {}).get("geral", {})

    valor_parcela = conta.get("valor")
    valor_desconto = desconto.get("valor")
    tipo_desconto_bling = desconto.get("unidade")
    
    qtd_parcelas = len(parcelas)

    valor_sem_desconto, desconto_final = calcular_desconto(
        valor_parcela,
        qtd_parcelas,
        valor_desconto,
        tipo_desconto_bling,
        banco
    )

    dados = {
        # Dados do contas a receber
        "conta_id": conta.get("id"),
        "valor": valor_sem_desconto,
        "vencimento": conta.get("vencimento"),

        # Dados do pedido de venda
        "numero_pedido": f"P {origem.get('numero')}",
        # "desconto_type": tipo_desconto,
        "valor_desconto": desconto_final,

        # Dados do contato do pagador
        "nome": contato.get("nome"),
        "documento": contato.get("numeroDocumento"),
        "tipo_pessoa": contato.get("tipo"),
        "telefone": contato.get("telefone"),
        "celular": contato.get("celular"),
        "email": contato.get("email") or contato.get("emailNotaFiscal") or "financeiro@porancosmeticos.com.br",
        
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


def calcular_desconto(valor_parcela_bling, qtd_parcelas, valor_desconto_bling, tipo_desconto_bling, banco):
    if (banco == "GRAFENO"):
        percentual = PERCENTUAL_GRAFENO
    
    else:
        percentual = PERCENTUAL_BTG

    if (not valor_desconto_bling or valor_desconto_bling <= 0):
        return (valor_parcela_bling * percentual), 0

    if (tipo_desconto_bling == "PERCENTUAL"):
        fator_desconto = valor_desconto_bling / 100
        valor_por_parcela_com_desconto = valor_parcela_bling * percentual
        
        valor_por_parcela_sem_desconto = valor_por_parcela_com_desconto / (1 - fator_desconto)
        valor_desconto_por_parcela = valor_por_parcela_sem_desconto - valor_por_parcela_com_desconto

    elif (tipo_desconto_bling == "REAL"):
        desconto_por_parcela = valor_desconto_bling / qtd_parcelas
        valor_desconto_por_parcela = desconto_por_parcela * percentual
        
        valor_por_parcela_com_desconto = valor_parcela_bling * percentual
        valor_por_parcela_sem_desconto = valor_por_parcela_com_desconto + valor_desconto_por_parcela

    return valor_por_parcela_sem_desconto, valor_desconto_por_parcela


def criar_cobranca_grafeno(dados):
    payload = {
        "paymentMethod": "boleto",
        "discounts": [
            {
                "discountType": "fixed_value",
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
            "email": dados["email"]
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
            "email": dados["email"],
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
            "branch": "50"
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

    if (banco == "SAIR"):
        print("Encerrando programa...")
        return

    formas = renovar.buscar_formas_pagamento()
    formas_ids = set()

    for forma in formas:
        descricao_bling = forma["descricao"]

        if ("Boleto" in descricao_bling):
            formas_ids.add(forma["id"])
    
    print(f"Formas encontradas = {formas_ids}")

    contas = renovar.buscar_contas_receber()
    contas_processar = []

    for conta in contas:
        forma_id = conta.get("formaPagamento", {}).get("id")

        if (forma_id in formas_ids):
            contas_processar.append(conta)

    if (not contas_processar):
        print("Nenhuma conta com forma de pagamento 'Boleto' encontrada.")
        return
    
    print("\n" + "="*70)
    print(f"{'CONFERÊNCIA DE CONTAS - DESTINO: ' + banco:^70}")
    print("="*70)
    print(f"{'CLIENTE':<35} | {'VENCIMENTO':<12} | {'VALOR (TOTAL)':<12}")
    print("-" * 70)

    total_soma = 0

    for c in contas_processar:
        nome = c.get("contato", {}).get("nome")[:33]
        vencimento = c.get("vencimento")
        valor =  c.get("valor")

        total_soma += valor

        print(f"{nome:<35} | {vencimento:<12} | R$ {valor:>10.2f}")

    print("-" * 70)
    print(f"TOTAL: {len(contas_processar)} contas | SOMA: R$ {total_soma:.2f}")
    
    confirmar = str(input(f"\nDeseja gerar os boletos de {banco} para estas contas? (S/N): ").upper())
    
    if (confirmar != "S"):
        print("Operação cancelada pelo usuário.")
        return

    encontrados = 0

    for conta in contas_processar:
        print(f"Processando: {conta.get('contato', {}).get('nome')}...")
        
        dados = extrair_dados_bling(conta, banco)

        if (not dados):
            continue

        try:
            if (banco == "GRAFENO"):
                payload = criar_cobranca_grafeno(dados)
                grafeno.criar_pagamento_grafeno(payload)
                print(" -> Boleto Grafeno criado!")
            
            elif (banco == "BTG"):
                payload = criar_cobranca_btg(dados)
                btg.criar_pagamento_btg(payload)
                print(" -> Boleto BTG criado!")

            salvar_dados_payload(payload)
            encontrados += 1

        except Exception as error:
            print(f" -> Erro ao criar o boleto: {error}")

    print(f"\nSucesso: {encontrados} boletos criados.")

if (__name__ == "__main__"):
    main()