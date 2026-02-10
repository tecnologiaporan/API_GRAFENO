import flask
from bling import renovar

app = flask.Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    data_inicial = None
    data_final = None
    items = [] 

    if (flask.request.method == "POST"):
        data_inicial = flask.request.form.get("data_emissao_inicial")
        data_final = flask.request.form.get("data_emissao_final")

        contas = renovar.buscar_contas_receber(data_inicial, data_final)

        for conta in contas:
            contato_info = conta.get("contato", {})
            contato_id = contato_info.get("id")
            origem = conta.get("origem", {})

            detalhe_contato = renovar.buscar_contato(contato_id)
            
            item = {
                "nome": detalhe_contato.get("nome"),
                "documento": detalhe_contato.get("codigo"),
                "valor": conta.get("valor"),
                "vencimento": conta.get("vencimento"),
                "numero_pedido": origem.get("numero")
            }
            
            items.append(item)

    return flask.render_template(
        "index.html",
        data_emissao_inicial = data_inicial,
        data_emissao_final = data_final,
        contas = items 
    )

if __name__ == "__main__":
    app.run(debug=True)