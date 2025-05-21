# Sistema de Troca de Mensagens Criptografadas

Um sistema simples de troca de mensagens criptografadas usando criptografia assimétrica (RSA) implementado em Python com Flask.

## Descrição

Este projeto consiste em dois servidores:
- **Servidor Receptor (app1.py)**: Gera um par de chaves RSA e fornece a chave pública. Recebe e descriptografa mensagens.
- **Servidor Remetente (app2.py)**: Obtém a chave pública, criptografa mensagens e as envia para o servidor receptor.

## Requisitos

- Python 3.x
- Flask
- cryptography
- requests

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd SistemaTrocaDeMensagens
```

2. Instale as dependências:
```bash
pip install flask cryptography requests
```

## Como Usar

1. Inicie o servidor receptor (em um terminal):
```bash
python app1.py
```

2. Inicie o servidor remetente (em outro terminal):
```bash
python app2.py
```

3. Acesse http://localhost:5001/ no navegador para enviar uma mensagem criptografada.

## Funcionamento

1. O servidor receptor (porta 5000) gera um par de chaves RSA
2. O servidor remetente (porta 5001) obtém a chave pública
3. Ao acessar a rota "/" do servidor remetente, uma mensagem é criptografada e enviada
4. O servidor receptor recebe a mensagem, descriptografa e exibe no console

## Segurança

- Utiliza criptografia RSA com padding OAEP
- Chaves de 2048 bits
- Mensagens são criptografadas antes do envio
- A chave privada permanece apenas no servidor receptor
