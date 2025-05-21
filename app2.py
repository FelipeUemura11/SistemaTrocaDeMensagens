# servidor remetente
from flask import Flask, request, jsonify
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import logging

# Configurar logging p/ fluxo de execucao do programa
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_public_key():
    """Obtém a chave pública do servidor receptor"""
    try:
        logger.debug("Obtendo chave publica do servidor receptor...")
        response = requests.get('http://localhost:5000/get_public_key')
        response.raise_for_status()

        public_key = serialization.load_pem_public_key(response.content)
        logger.debug("Chave pública obtida com sucesso")
        return public_key
    except Exception as e:
        logger.error(f"Erro ao obter chave pública: {str(e)}")
        raise

# envia a msg criptografada para o servidor receptor(app1.py)
def send_encrypted_message(message):
    try:
        public_key = get_public_key()
        
        logger.debug("Criptografando mensagem...")
        encrypted_message = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_b64 = base64.b64encode(encrypted_message).decode('utf-8')
        logger.debug("Mensagem criptografada com sucesso")

        # envia via POST (Webhook)
        logger.debug("Enviando mensagem para o webhook...")
        response = requests.post(
            'http://localhost:5000/webhook',
            json={"encrypted_message": encrypted_b64}
        )
        response.raise_for_status()
        logger.debug("Mensagem enviada com sucesso")
        
        # Retorna o conteúdo JSON da resposta
        return response.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão: {str(e)}")
        return {"error": "Não foi possível conectar ao servidor receptor. Verifique se o servidor está rodando."}
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        return {"error": str(e)}

@app.route("/")
def send():
    try:
        message = "Enviando mensagem criptografada para o servidor receptor!"
        result = send_encrypted_message(message)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro na rota /: {str(e)}")
        return jsonify({"error": str(e)}), 500

# servidor remetente
if __name__ == '__main__':
    app.run(port=5001, debug=True)