from config import PERCENTUAL_BTG, PERCENTUAL_GRAFENO

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