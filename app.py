import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Função para autenticar na API do SendPulse
def autenticar_sendpulse():
    url = "https://oauth.sendpulse.com/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("SENDPULSE_CLIENT_ID"),
        "client_secret": os.getenv("SENDPULSE_CLIENT_SECRET")
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

# Função para buscar um pedido no Tiny ERP
def buscar_pedido_tiny(identificador):
    api_token = os.getenv("API_TOKEN_TINY")
    url = f"https://api.tiny.com.br/api2/pedidos.pesquisa.php?token={api_token}&formato=json&pesquisa={identificador}"
    response = requests.get(url)
    response.raise_for_status()
    pedidos = response.json().get("retorno", {}).get("pedidos", [])
    return pedidos[0] if pedidos else None

# Função para buscar um produto no Tiny ERP
def buscar_produto_tiny(sku):
    api_token = os.getenv("API_TOKEN_TINY")
    url = f"https://api.tiny.com.br/api2/produto.obter.estrutura.php?token={api_token}&formato=json&id={sku}"
    response = requests.post(url)
    response.raise_for_status()
    produto = response.json().get("retorno", {}).get("produto", {})
    return produto if produto else None

# Função para responder no WhatsApp via SendPulse
def responder_whatsapp(cliente, telefone, access_token):
    url = "https://api.sendpulse.com/whatsapp/sendMessage"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    mensagem = f"Olá! Aqui estão as informações solicitadas: {cliente}"
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Rota para o webhook do WhatsApp
@app.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():
    data = request.json
    telefone = data.get("phone")
    mensagem = data.get("message")
    
    if not telefone or not mensagem:
        return jsonify({"error": "Dados insuficientes"}), 400
    
    access_token = autenticar_sendpulse()
    
    if mensagem.isdigit():  # Se for um ID numérico, busca pedido
        pedido = buscar_pedido_tiny(mensagem)
        if pedido:
            resposta = responder_whatsapp(pedido, telefone, access_token)
            return jsonify(resposta)
        else:
            return jsonify({"message": "Pedido não encontrado."}), 404
    else:  # Caso contrário, assume que é um SKU e busca produto
        produto = buscar_produto_tiny(mensagem)
        if produto:
            resposta = responder_whatsapp(produto, telefone, access_token)
            return jsonify(resposta)
        else:
            return jsonify({"message": "Produto não encontrado."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
