from socket import *

# 127.0.0.1 = localhost
serverName = '192.168.100.124'
serverPort = 40000

# Create UDP socket for client
clientSocket = socket(AF_INET,SOCK_DGRAM)

# get user keyboard input
message = input('Input lowercase sentence:')

# send message to server
clientSocket.sendto(message.encode(),(serverName, serverPort))

# read reply characters from socket into string
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print(modifiedMessage.decode())
clientSocket.close()
