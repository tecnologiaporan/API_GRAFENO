from config import ARQUIVO_UNICO, PASTA_LOGS
import json
import os


def gerar_log(payload):
    try:
        if (not os.path.exists(PASTA_LOGS)):
            os.makedirs(PASTA_LOGS)

        with open(ARQUIVO_UNICO, "a", encoding = "utf-8") as f:
            f.write(json.dumps(payload, indent = 4, ensure_ascii = False))
            f.write("\n\n" + " -=" * 50 + "\n\n")
        
        print(f"Boleto registrado com sucesso!")
    
    except (Exception, FileNotFoundError, RuntimeError) as e:
        print(f"ERRO: {e}")