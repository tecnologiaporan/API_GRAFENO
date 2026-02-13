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