import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def autenticar_sendpulse(client_id, client_secret):
    url = 'https://oauth.sendpulse.com/oauth/access_token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

def buscar_pedido_tiny(api_token, identificador):
    url = f'https://api.tiny.com.br/api2/pedidos.pesquisa.php?token={api_token}&formato=json&pesquisa={identificador}'
    response = requests.get(url)
    response.raise_for_status()
    pedidos = response.json().get('retorno', {}).get('pedidos', [])
    return pedidos[0] if pedidos else None

def responder_whatsapp(cliente, telefone):
    url = "https://api.sendpulse.com/whatsapp/sendMessage"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    mensagem = f"Olá {cliente['nome']}, seu pedido {cliente['numero']} está com status: {cliente['status']}!"
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

@app.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():
    data = request.json
    telefone = data.get("phone")
    mensagem = data.get("message")
    
    if not telefone or not mensagem:
        return jsonify({"error": "Dados insuficientes"}), 400
    
    pedido = buscar_pedido_tiny(API_TOKEN_TINY, mensagem)
    
    if pedido:
        resposta = responder_whatsapp(pedido, telefone)
        return jsonify(resposta)
    else:
        return jsonify({"message": "Pedido não encontrado."}), 404

# Configurações
CLIENT_ID = os.getenv("SENDPULSE_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENDPULSE_CLIENT_SECRET")
API_TOKEN_TINY = os.getenv("API_TOKEN_TINY")
ACCESS_TOKEN = autenticar_sendpulse(CLIENT_ID, CLIENT_SECRET)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
