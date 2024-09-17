from socket import *
import pprint
import threading
import sys

convert_coma = lambda txt: str(txt).replace('%;', ',')

class Users:
    def __init__(self):
        self.data = dict()

    def add(self, username, client_ip, client_port, tcp_socket=None):
        new_user = {
            'socket_type': 'tcp',
            'client_ip': client_ip,
            'client_port': client_port,
            'tcp_socket': tcp_socket,
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
    
    def get_socket(self, user):
        return self.data[user]['tcp_socket']

    def get_username(self, user):
        return self.data[user]['username']
    
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

class ServerTCP:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = int(port)
        self.TCP_SOCKET = socket(AF_INET, SOCK_STREAM)
        self.TCP_SOCKET.bind((self.HOST, self.PORT))
        self.TCP_SOCKET.listen(1)
        self.USERS = Users()

    def listen(self):
        print(f'Listening TCP on {self.TCP_SOCKET.getsockname()}')
        while True:
            try:
                clientSocket, clientAddress = self.TCP_SOCKET.accept()
                client_ip, client_port = clientAddress
                print(f"Accepted connection from {clientAddress}")
                threading.Thread(target=self.listen_user, args=(clientSocket, clientAddress)).start()
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
        self.TCP_SOCKET.close()

    def listen_user(self, client_socket:socket, clientAddress):
        print(f'Listening for user on {client_socket.getsockname()}')
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    print(f'Closing socket {client_socket.getsockname()}')
                    client_socket.close()
                    return
                print(f'{message.decode()} / {client_socket.getsockname()}')
                self.handle(message, clientAddress, client_socket)
            except:
                break
        client_socket.close()

    def handle(self, message, clientAddr, tcp_socket=None):
        print(f'message: {message}')
        data = self.unpack_message(message.decode())
        print(f'data: {data}')
        # Handle login, logout, and message logic here...

    def unpack_message(self, message):
        data = message.strip('][').split(', ')
        return data

def main():
    server_ip = sys.argv[1]
    server = ServerTCP(server_ip, 12000)
    try:
        server.listen()
    except KeyboardInterrupt:
        pass

main()