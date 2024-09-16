from socket import *

serverPort = 12000

# create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))

# server begins listening for incoming TCP requests
serverSocket.listen(1)

print ('The server is ready to receive')
while True:

    # server waits on accept() for incoming requests, new socket created on return
    connectionSocket, addr = serverSocket.accept()

    # read bytes from socket (butnot address as in UDP)
    sentence = connectionSocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())

# close connection to this client (but not welcoming socket)
connectionSocket.close()