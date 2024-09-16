from socket import *

serverPort = 40000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

clients = {}  # Para armazenar clientes conectados

print('The server is ready to receive')

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    decodedMessage = message.decode()

    # Verificar se o cliente já está registrado
    if clientAddress not in clients:
        clients[clientAddress] = True
        print(f"Novo cliente registrado: {clientAddress}")

    # Para todos os clientes conectados, menos o remetente, enviar a mensagem
    for client in clients:
        if client != clientAddress:
            serverSocket.sendto(f"Mensagem de {clientAddress}: {decodedMessage}".encode(), client)
