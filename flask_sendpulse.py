import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Função para autenticar na API do SendPulse
def autenticar_sendpulse():
    url = "https://oauth.sendpulse.com/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("e813ef99130a7e6bdd3f7157a0bdb880"),
        "client_secret": os.getenv("b4ad043884a0be91210ff97bc6c63b72")
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

# Função para buscar um produto no Tiny ERP pelo SKU
def buscar_produto_tiny(sku):
    api_token = os.getenv("e46061418c080bef38a9dc057270ca775bc55b22")
    url = f"https://api.tiny.com.br/api2/produto.obter.estrutura.php?token={api_token}&formato=json&id={sku}"
    response = requests.get(url)
    response.raise_for_status()
    produto = response.json().get("retorno", {}).get("produto", {})
    return produto if produto else None

# Função para buscar um pedido no Tiny ERP pelo ID
def buscar_pedido_tiny(pedido_id):
    api_token = os.getenv("e46061418c080bef38a9dc057270ca775bc55b22")
    url = f"https://api.tiny.com.br/api2/pedidos.pesquisa.php?token={api_token}&formato=json&numero={pedido_id}"
    response = requests.get(url)
    response.raise_for_status()
    pedidos = response.json().get("retorno", {}).get("pedidos", [])
    return pedidos[0]["pedido"] if pedidos else None

# Função para enviar mensagem no WhatsApp via SendPulse
def responder_whatsapp(mensagem, telefone, access_token):
    url = "https://api.sendpulse.com/whatsapp/sendMessage"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Webhook do WhatsApp para processar pedidos ou produtos
@app.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type deve ser application/json"}), 415

    data = request.get_json()
    telefone = data.get("phone")
    mensagem = data.get("message")

    if not telefone or not mensagem:
        return jsonify({"error": "Campos obrigatórios ausentes"}), 400

    access_token = autenticar_sendpulse()

    # Verifica se a mensagem é um ID de pedido ou SKU de produto
    pedido = buscar_pedido_tiny(mensagem)
    if pedido:
        resposta_mensagem = f"Pedido {pedido['numero']} de {pedido['nome']} está com status: {pedido['situacao']}."
        resposta = responder_whatsapp(resposta_mensagem, telefone, access_token)
        return jsonify(resposta)

    produto = buscar_produto_tiny(mensagem)
    if produto:
        resposta_mensagem = f"Produto: {produto['nome']} - Código: {produto['codigo']}."
        resposta = responder_whatsapp(resposta_mensagem, telefone, access_token)
        return jsonify(resposta)

    return jsonify({"message": "Nenhum pedido ou produto encontrado."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
