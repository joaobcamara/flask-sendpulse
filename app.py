from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "API do Tiny ERP integrada com SendPulse está rodando!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Processa os dados recebidos do Tiny ERP
    response_data = {
        "nome": data.get("cliente_nome", ""),
        "pedido": data.get("pedido_id", ""),
        "status": data.get("status_pedido", "")
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
