# servidor receptor
from flask import Flask
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64
import logging

# Configurar logging p/ fluxo de execucao do programa
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# fornece a chave publica para o servidor remetente
@app.route("/get_public_key", methods=['GET'])
def get_public_key():
    try:
        logger.debug("Gerando chave publica...")
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        logger.debug("Chave publica gerada com sucesso")
        return public_pem.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao gerar chave publica: {str(e)}")
        return jsonify({"error": str(e)}), 500

# recebe mensagens criptografadas (Webhook)
@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        logger.debug("Recebendo mensagem criptografada...")
        encrypted_data = request.json.get('encrypted_message')
        if not encrypted_data:
            raise ValueError("Nenhuma mensagem criptografada recebida")
            
        encrypted_bytes = base64.b64decode(encrypted_data)
        logger.debug("Mensagem decodificada do base64")

        # descriptografando a mensagem
        decrypted_message = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        logger.debug(f"Mensagem recebida (Descriptografada): {decrypted_message.decode('utf-8')}")
        return jsonify({"status": "Mensagem recebida!"}), 200
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)