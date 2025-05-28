# servidor remetente
from flask import Flask, request, jsonify, render_template
import requests
import logging
import hashlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def obter_chave_publica():
    try:
        logger.debug("Obtendo chave publica do servidor receptor...")
        response = requests.get('http://localhost:5000/obter_chave_publica')
        response.raise_for_status()

        n, e = map(int, response.text.split(','))
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
        response = requests.post(
            'http://localhost:5000/webhook',
            json={
                "criptografado_message": str(criptografado),
                "hash_mensagem": hash_mensagem
            }
        )
        response.raise_for_status()
        logger.debug("Mensagem enviada com sucesso")
        
        return response.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro de conexão: {str(e)}")
        return {"error": "Não foi possível conectar ao servidor receptor. Verifique se o servidor está rodando."}
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        return {"error": str(e)}

@app.route("/", methods=['GET', 'POST'])
def enviar():
    if request.method == 'GET':
        return render_template('index.html')
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Mensagem não fornecida"}), 400
            
        mensagem = data['message']
        resultado = enviar_mensagem_criptografada(mensagem)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro na rota /: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)