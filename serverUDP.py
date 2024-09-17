from socket import *
import pprint
import threading
import sys

convert_coma = lambda txt: str(txt).replace('%;', ',')

class Users:
    def __init__(self):
        self.data = dict()

    def add(self, username, client_ip, client_port):
        new_user = {
            'socket_type': 'udp',
            'client_ip': client_ip,
            'client_port': client_port,
            'username': username,
        }
        self.data[username] = new_user
        self.data[(client_ip, client_port)] = new_user

    def remove(self, username):
        ip = self.data[username]['client_ip']
        port = self.data[username]['client_port']
        del self.data[username]
        del self.data[(ip, port)]

    def get(self, user):
        return self.data[user]
    
    def get_client_ip(self, user):
        return self.data[user]['client_ip']
    
    def get_client_port(self, user):
        return self.data[user]['client_port']

    def __contains__(self, user):
        return user in self.data

    def __str__(self):
        return str(self.data)
    
    def __iter__(self): 
        return iter(self.data)

class ServerUDP:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = int(port)
        self.UDP_SOCKET = socket(AF_INET, SOCK_DGRAM)
        self.UDP_SOCKET.bind((self.HOST, self.PORT))
        self.USERS = Users()

    def listen(self):
        print(f'Listening UDP on {self.UDP_SOCKET.getsockname()}')
        while True:
            try:
                message, clientAddress = self.UDP_SOCKET.recvfrom(2048)
                print(f'Received message from {clientAddress}')
                self.handle(message, clientAddress)
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
        self.UDP_SOCKET.close()

    def handle(self, message, clientAddr):
        print(f'message: {message}')
        data = self.unpack_message(message.decode())
        print(f'data: {data}')
        # Handle login, logout, and message logic here...
    
    def unpack_message(self, message):
        data = message.strip('][').split(', ')
        return data

def main():
    server_ip = sys.argv[1]
    server = ServerUDP(server_ip, 12001)
    try:
        server.listen()
    except KeyboardInterrupt:
        pass

main()