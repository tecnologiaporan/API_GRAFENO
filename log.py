from config import ARQUIVO_UNICO
import json


def gerar_log(payload):
    try:
        with open(ARQUIVO_UNICO, "a", encoding = "utf-8") as f:
            f.write(json.dumps(payload, indent = 4, ensure_ascii = False))
            f.write("\n\n" + " -=" * 50 + "\n\n")
    
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERRO: {e}")

    print(f"Payload salvo em TXT")