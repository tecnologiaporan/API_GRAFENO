import geradores
import log
import interface
from bling import bling_v2
from grafeno import grafeno
from btg import btg


def main():
    banco = interface.menu()

    if (banco == "SAIR"):
        print("Encerrando programa...")
        return

    formas = bling_v2.buscar_formas_pagamento()
    formas_ids = set()

    for forma in formas:
        descricao_bling = forma["descricao"]

        if ("Boleto" in descricao_bling):
            formas_ids.add(forma["id"])

    contas = bling_v2.buscar_contas_receber()
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
        
        dados = bling_v2.extrair_dados_bling(conta, banco)

        if (not dados):
            continue

        try:
            if (banco == "GRAFENO"):
                payload = geradores.criar_cobranca_grafeno(dados)
                grafeno.criar_pagamento_grafeno(payload)
                print("Boleto Grafeno criado!")
            
            elif (banco == "BTG"):
                payload = geradores.criar_cobranca_btg(dados)
                btg.criar_pagamento_btg(payload)
                print("Boleto BTG criado!")

            log.gerar_log(payload)
            encontrados += 1

        except Exception as error:
            print(f"Erro ao criar o boleto: {error}")

    print(f"\nSucesso: {encontrados} boletos criados.")

if (__name__ == "__main__"):
    main()