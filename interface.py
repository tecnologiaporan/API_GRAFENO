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