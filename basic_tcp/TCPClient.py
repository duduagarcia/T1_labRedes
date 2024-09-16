from socket import *


# Acho q pra testar com PCs diferentes, basta os dois entrarem na mesma rede e o serverName ser o IP da máquina do servidor

# 127.0.0.1 = localhost
serverName = '127.0.0.1'
serverPort = 12000

# create TCP socket for server, remote port 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))


sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())

# No need to attach server name, port 
modifiedSentence = clientSocket.recv(1024)

print ('From Server:', modifiedSentence.decode())
clientSocket.close()