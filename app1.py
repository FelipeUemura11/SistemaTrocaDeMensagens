# servidor receptor
from flask import Flask
from flask import Flask, request, jsonify
import logging
import random
import hashlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def eh_primo(n, k=5):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gerar_primo(bits):
    while True:
        n = random.getrandbits(bits)
        if eh_primo(n):
            return n

def generate_key_pair():
    
    p = gerar_primo(512)
    q = gerar_primo(512)
    
    n = p * q
    
    phi = (p - 1) * (q - 1)
    
    e = 65537
    
    d = pow(e, -1, phi)
    
    return (n, e), (n, d)

public_key, private_key = generate_key_pair()

def criptografar_mensagem(mensagem, chave_publica):
    n, e = chave_publica
    mensagem_bytes = mensagem.encode('utf-8')
    mensagem_int = int.from_bytes(mensagem_bytes, 'big')
    
    criptografado = pow(mensagem_int, e, n)
    return criptografado

def descriptografar_mensagem(criptografado, chave_privada):
    n, d = chave_privada
    descriptografado = pow(criptografado, d, n)
    
    descriptografado_bytes = descriptografado.to_bytes((descriptografado.bit_length() + 7) // 8, 'big')
    return descriptografado_bytes.decode('utf-8')

def verificar_hash(mensagem, hash_recebido):
    hash_mensagem = hashlib.sha256(mensagem.encode('utf-8')).hexdigest()
    return hash_mensagem == hash_recebido

@app.route("/obter_chave_publica", methods=['GET'])
def obter_chave_publica():
    try:
        logger.debug("Gerando chave publica...")
        chave_publica_str = f"{public_key[0]},{public_key[1]}"
        logger.debug("Chave publica gerada com sucesso")
        return chave_publica_str
    except Exception as e:
        logger.error(f"Erro ao gerar chave publica: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        logger.debug("Recebendo mensagem criptografada...")
        criptografado_data = request.json.get('criptografado_message')
        hash_recebido = request.json.get('hash_mensagem')
        
        if not criptografado_data or not hash_recebido:
            raise ValueError("Mensagem criptografada ou hash não recebidos")
            
        criptografado_int = int(criptografado_data)
        logger.debug("Mensagem convertida para inteiro")

        mensagem_descriptografada = descriptografar_mensagem(criptografado_int, private_key)
        
        if not verificar_hash(mensagem_descriptografada, hash_recebido):
            raise ValueError("Hash da mensagem não corresponde - possível manipulação detectada")

        logger.debug(f"Mensagem recebida (Descriptografada): {mensagem_descriptografada}")
        return jsonify({"status": "Mensagem recebida e verificada com sucesso!"}), 200
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)