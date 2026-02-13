from customtkinter import *
from tkinter import messagebox
from datetime import datetime
from view import interface_logica

referencias_selecao = []


def atualizar_listagem():
    try:
        global referencias_selecao 

        selecionar_todos_var.set(False)

        for widget in scroll_lista.winfo_children():
            widget.destroy()
        
        referencias_selecao = []
        
        resultado = interface_logica.buscar_dados_bling(data_entry_inicio.get(), data_entry_final.get())
        contas, status = resultado

        if (contas is None):
            CTkLabel(scroll_lista, text = f"ERRO: {status}", text_color = "red", font = ("Arial", 16)).pack(pady = 50)
            return
        
        if (len(contas) == 0):
            CTkLabel(scroll_lista, text = "Nenhum título encontrado neste período.", text_color = "white", font = ("Arial", 16, "bold")).pack(pady = 50)
            return


        for conta in contas:
            linha = CTkFrame(scroll_lista, fg_color = "transparent")
            linha.pack(fill = "x", pady = 2)

            var_selecao = BooleanVar(value = False)

            chk = CTkCheckBox(linha, text = "", variable = var_selecao, width = 20)
            chk.grid(row = 0, column = 0, padx = (10, 10))

            nome = conta.get("contato", {}).get("nome")[:30]
            nome_label = CTkLabel(linha, text = nome, width = 200, anchor="w")
            nome_label.grid(row = 0, column = 1, padx = 5)

            documento = conta.get("contato", {}).get("numeroDocumento")
            documento_label = CTkLabel(linha, text = documento, width = 150, anchor="w")
            documento_label.grid(row = 0, column = 2, padx = 5)

            forma_pagamento = conta.get("forma_descricao")
            forma_pagamento_label = CTkLabel(linha, text = forma_pagamento, width = 150, anchor = "w")
            forma_pagamento_label.grid(row = 0, column = 3, padx = 5)

            valor = conta.get("valor")
            valor_format = f"R$ {valor :.2f}"
            valor_label = CTkLabel(linha, text = valor_format, width = 100, anchor="e")
            valor_label.grid(row = 0, column = 4, padx = 5)

            vencimento = conta.get("vencimento")
            vencimento_label = CTkLabel(linha, text = vencimento, width = 100, anchor="center")
            vencimento_label.grid(row = 0, column = 5, padx = 5)

            referencias_selecao.append({"dados": conta, "check": var_selecao})

    except Exception as e:
        print(f"Erro na interface: {e}")


def emitir_boletos():
    banco = banco_combo_box.get()

    selecionados = []

    for item in referencias_selecao:
        var_checkbox = item["check"]
        dados_conta = item["dados"]

        if (var_checkbox.get() == True):
            selecionados.append(dados_conta)
        
    
    if (not selecionados):
        messagebox.showwarning("Atenção!", "Selecione pelo menos um título!")
        return
    
    if (not messagebox.askyesno("Confirmar", f"Deseja gerar {len(selecionados)} boletos para o {banco}?")):
        return

    status_label.configure(text = "Processando...", text_color = "yellow")
    tela.update_idletasks() 

    sucessos, falhas = interface_logica.processar_boletos(selecionados, banco)
    
    messagebox.showinfo("Concluído", f"Emissão finalizada!\nSucessos: {sucessos}\nFalhas: {falhas}")
    status_label.configure(text = "Emissão concluída.", text_color = "green")
    
    atualizar_listagem()


def toggle_selecionar_todos():
    estado_mestre = selecionar_todos_var.get()

    for item in referencias_selecao:
        var_item = item["check"]
        var_item.set(estado_mestre)

tela = CTk()
tela.geometry("1000x700")
tela.title("Sistema Emissor de Boletos")
tela.resizable(False, False)

main_frame = CTkFrame(tela, fg_color = "black") 
main_frame.pack(fill = "both", expand = True, padx = 20, pady = 20)

title_label = CTkLabel(main_frame, text = "Sistema Emissor de Boletos", text_color = "white", font = ("Arial", 24, "bold")).pack(pady = (20, 20))

filtro_frame = CTkFrame(main_frame, fg_color = "#1a1a1a", corner_radius = 10)
filtro_frame.pack(fill = "x", padx = 20, pady = 10)

data_label_inicio = CTkLabel(filtro_frame, text = "Data Início:", text_color = "white", font = ("Arial", 14)).grid(row = 0, column = 0, padx = 10, pady = 10)
data_entry_inicio = CTkEntry(filtro_frame, placeholder_text = "DD/MM/AAAA", width = 120, font = ("Arial", 14))
data_entry_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
data_entry_inicio.grid(row = 0, column = 1, padx = 5)

data_label_final = CTkLabel(filtro_frame, text = "Data Final:", text_color = "white", font = ("Arial", 14)).grid(row = 0, column = 2, padx = 10, pady = 10)
data_entry_final = CTkEntry(filtro_frame, placeholder_text = "DD/MM/AAAA", width = 120, font = ("Arial", 14))
data_entry_final.insert(0, datetime.now().strftime("%d/%m/%Y"))
data_entry_final.grid(row = 0, column = 3, padx = 5)

btn_listar = CTkButton(filtro_frame, text = "Listar contas", text_color = "white", fg_color = "green", hover_color = "#0a5c0a", cursor = "hand2", font = ("Arial", 14, "bold"), command = atualizar_listagem)
btn_listar.grid(row = 0, column = 4, padx = 30)

listagem_label = CTkLabel(main_frame, text = "Selecione os títulos abaixo para emissão:")
listagem_label.pack(anchor = "w", padx = 25)

selecionar_todos_var = BooleanVar(value = False)

header_frame = CTkFrame(main_frame, fg_color = "#2b2b2b", height = 30, corner_radius = 0)
header_frame.pack(fill = "x", padx = 20, pady = (10, 0))

selecionar_todos_check_box = CTkCheckBox(header_frame, text = "Selecionar", variable = selecionar_todos_var, width = 50, command = toggle_selecionar_todos)
selecionar_todos_check_box.grid(row = 0, column = 0, padx = (10, 10))

CTkLabel(header_frame, text="Cliente", width = 200, anchor="w").grid(row = 0, column = 1, padx = 5)
CTkLabel(header_frame, text="CNPJ/CPF", width = 150, anchor = "w").grid(row = 0, column = 2, padx = 5)
CTkLabel(header_frame, text="Forma de Pagamento", width = 150, anchor = "w").grid(row = 0, column = 3, padx = 5)
CTkLabel(header_frame, text="Valor R$", width = 100, anchor = "w").grid(row = 0, column = 4, padx = 5)
CTkLabel(header_frame, text="Vencimento", width = 100, anchor = "w").grid(row = 0, column = 5, padx = 5)

scroll_lista = CTkScrollableFrame(main_frame, width = 900, height = 350, fg_color = "#565656", border_width = 2)
scroll_lista.pack(fill = "both", expand = True, padx = 20, pady = 20)

acao_frame = CTkFrame(main_frame, fg_color = "transparent")
acao_frame.pack(fill = "x", padx = 20, pady = 10)

status_label = CTkLabel(acao_frame, text = "Aguardando seleção...", text_color = "gray")
status_label.pack(side = "left", padx = 10)

banco_combo_box = CTkComboBox(acao_frame, values = ["GRAFENO", "BTG"], width = 150, state="readonly") 
banco_combo_box.set("GRAFENO")
banco_combo_box.pack(side = "right", padx = 10)

btn_gerar_boleto = CTkButton(acao_frame, text = "Gerar Boletos", text_color = "white", fg_color = "green", hover_color = "#0a5c0a", cursor = "hand2", font = ("Arial", 14, "bold"), command = emitir_boletos)
btn_gerar_boleto.pack(side = "right", padx = 10)