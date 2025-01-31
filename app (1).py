from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # Estruturando os dados recebidos
    response_data = {
        'nome': data.get('nome', 'Desconhecido'),
        'pedido': data.get('pedido', 'Sem Pedido'),
        'status': data.get('status', 'Sem Status')
    }

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
