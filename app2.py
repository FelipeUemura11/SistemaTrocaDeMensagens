# servidor remetente
from flask import Flask, request, jsonify, render_template
import requests
import logging
import hashlib
from datetime import datetime
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lista para armazenar mensagens
mensagens = []

def obter_chave_publica():
    try:
        logger.debug("Obtendo chave publica do servidor receptor...")
        resposta = requests.get('http://localhost:5000/obter_chave_publica')
        resposta.raise_for_status()

        n, e = map(int, resposta.text.split(','))
        chave_publica = (n, e)
        logger.debug("Chave pública obtida com sucesso")
        return chave_publica
    except Exception as e:
        logger.error(f"Erro ao obter chave pública: {str(e)}")
        raise

def criptografar_mensagem(mensagem, chave_publica):
    n, e = chave_publica
    mensagem_bytes = mensagem.encode('utf-8')
    mensagem_int = int.from_bytes(mensagem_bytes, 'big')
    
    criptografado = pow(mensagem_int, e, n)
    return criptografado

def gerar_hash_mensagem(mensagem):
    return hashlib.sha256(mensagem.encode('utf-8')).hexdigest()

def enviar_mensagem_criptografada(mensagem):
    try:
        chave_publica = obter_chave_publica()
        
        logger.debug("Criptografando mensagem...")
        criptografado = criptografar_mensagem(mensagem, chave_publica)
        logger.debug("Mensagem criptografada com sucesso")

        logger.debug("Gerando hash da mensagem...")
        hash_mensagem = gerar_hash_mensagem(mensagem)
        logger.debug("Hash gerado com sucesso")

        logger.debug("Enviando mensagem para o webhook...")
        resposta = requests.post(
            'http://localhost:5000/webhook',
            json={
                "mensagem_criptografada": str(criptografado),
                "hash_mensagem": hash_mensagem
            }
        )
        resposta.raise_for_status()
        logger.debug("Mensagem enviada com sucesso")
        
        return resposta.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão: {str(e)}")
        return {"erro": "Não foi possível conectar ao servidor receptor. Verifique se o servidor está rodando."}
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        return {"erro": str(e)}

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        dados = request.get_json()
        if not dados or 'mensagem' not in dados:
            return jsonify({"erro": "Mensagem não fornecida"}), 400
        mensagem = dados['mensagem']
        resultado = enviar_mensagem_criptografada(mensagem)
        if "status" in resultado:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message_id = str(uuid.uuid4())[:8]
            mensagens.append({
                "id": message_id,
                "timestamp": timestamp,
                "texto": mensagem
            })
            if len(mensagens) > 100:
                mensagens.pop(0)
        return jsonify(resultado)

@app.route("/check_messages", methods=['GET'])
def check_messages():
    try:
        # Busca o histórico de mensagens do receptor
        resposta = requests.get('http://localhost:5000/check_messages')
        resposta.raise_for_status()
        return jsonify(resposta.json())
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens do receptor: {str(e)}")
        return jsonify({"mensagens": [], "erro": str(e)})

if __name__ == '__main__':
    app.run(port=5001, debug=True)