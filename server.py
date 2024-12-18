from socket import *
import pprint
import threading
import sys # manipular argumentos via linha de comando

# usado para conseguir digitar "," nas mensagens
convert_coma = lambda txt: str(txt).replace('%;', ',')

class Users:
    def __init__(self):
        # inicia a classe com dicionário vazio para armazenar as infos do user
        self.data = dict()

    # adiciona um usuário ao dicionário, sendo a chave o proprio nome
    def add(self, username, client_ip, client_port, tcp_socket=None):
        new_user = {
            'socket_type': 'tcp' if tcp_socket else 'udp',
            'client_ip': client_ip,
            'client_port': client_port,
            'tcp_socket': tcp_socket,
            'username': username,
        }
        self.data[username] = new_user
        self.data[(client_ip, client_port)] = new_user

    # extrai um usuário do dicionário, bem como o ip e a porta deste usuário
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
    
    def get_udp_client_addr(self, user):
        return (self.data[user]['client_ip'], self.data[user]['client_port'])

    def get_socket_type(self, user):
        return self.data[user]['socket_type']

    # auxiliares

    # verifica se user está dentro do dicionário
    def __contains__(self, user):
        return user in self.data

    # toString
    def __str__(self):
        return str(self.data)
    
    # permite itrar sobre users
    def __iter__(self): 
        return iter(self.data)

class Server:
    def __init__(self, host, port):
        # define as portas TCP e UDP de uma só vez, ao invés de criar uma aplicaçõa separada para UDP e outra para TCP
        self.HOST = host
        self.UDP_CONTROLL_PORT = int(port)
        self.UDP_DATA_PORT = int(port) + 1
        self.TCP_CONTROLL_PORT = int(port) + 2
        self.TCP_DATA_PORT = int(port) + 3


        # Criando os sockets TCP e UDP

        # DATA = gerencia as transferências de mensagens ou arquivos dos clientes
        # CONTROL = gerencia as conexões e comandos dos clientes
        
        self.UDP_CONTROLL_SOCKET = socket(AF_INET, SOCK_DGRAM)
        self.UDP_DATA_SOCKET = socket(AF_INET, SOCK_DGRAM)

        self.TCP_CONTROLL_SOCKET = socket(AF_INET, SOCK_STREAM)
        self.TCP_DATA_SOCKET = socket(AF_INET, SOCK_STREAM)
        
        # Dando o binding dos sockets com as portas
        self.TCP_CONTROLL_SOCKET.bind((self.HOST, self.TCP_CONTROLL_PORT))
        self.TCP_DATA_SOCKET.bind((self.HOST, self.TCP_DATA_PORT))
        self.UDP_CONTROLL_SOCKET.bind((self.HOST, self.UDP_CONTROLL_PORT))
        self.UDP_DATA_SOCKET.bind((self.HOST, self.UDP_DATA_PORT))

        # Configura os sockets TCP para usar conexões
        self.TCP_CONTROLL_SOCKET.listen(1)
        self.TCP_DATA_SOCKET.listen(1)

        self.USERS = Users()


    # Inicia e escuta as conexões tcp com limite de 2s
    def listen_tcp(self, socket:socket):
        socket.settimeout(2)
        print(socket)
        print(f'listening tcp on {socket.getsockname()}')


        while True:

            # tentando aceitar a conexão do cliente
            try:

                # Se a conexão der certo, pegamos os dados dos clientes e criamos uma nova thread pra conexão
                clientSocket, clientAddress = socket.accept()
                client_ip, client_port = clientAddress
                print(f"Accepted connection from {clientAddress}")
                threading.Thread(target=self.listen_user_tcp, args=(clientSocket, clientAddress)).start()
            except:
                if not threading.main_thread().is_alive(): break
        print(f'closing tcp on {socket.getsockname()}')
        # socket.shutdown(SHUT_RDWR)
        # socket.close()

    # Trata as mensagens TCP dos clientes
    def listen_user_tcp(self, client_socket:socket, clientAddress):
        client_socket.settimeout(2)
        print(f'listening user tcp on {client_socket.getsockname()}')

        # Loop para receber mensagens dos clientes
        while True:
            try:
                message = client_socket.recv(2048)
                if not message:  
                    print(F'closing socket {client_socket.getsockname()}')
                    client_socket.close()
                    return
                # Exibe e processa a mensagem
                print(f'{message.decode()} / {client_socket.getsockname()}')
                self.handle(message, clientAddress, client_socket)
            except  :
                if not threading.main_thread().is_alive(): break
        print(f'closing user tcp on {client_socket.getsockname()}')
        client_socket.shutdown(SHUT_RDWR)
        client_socket.close()

    # Escuta as mensagens UDP
    def listen_udp(self, socket:socket):
        socket.settimeout(2)
        print(f'listening udp on {socket.getsockname()}')
        while True:
            try:
                message, clientAddress = socket.recvfrom(2048)
                self.handle(message, clientAddress)
            except:
                if not threading.main_thread().is_alive():
                    socket.close() 
                    return

    # Function para descompactar a mensagem e tratar ela no manipulador apropriado
    def handle(self, message, clientAddr, tcp_socket=None):
        print(f'message: {message}')
        print(f'clientAddress: {clientAddr}')
        HANDLER = {
            'REG': self.handle_login,
            'LOGOUT': self.handle_logout,
            'MSG': self.handle_private_message,
            'MSGF': self.handle_private_message_with_file,
            'MSGA': self.handle_broadcast
        }
        data = self.unpack_message(message.decode())
        print(f'data: {data}')
        HANDLER[data[0]](data[1:], clientAddr, tcp_socket)


    def handle_private_message_with_file(self, data, clientAddr, tcp_socket=None):
        print('handle_private_message_with_file')
        receiver, sender, message = data[0], data[1], convert_coma(data[2])
        print('message: ' + message)
        if (receiver not in self.USERS):
            print(f'user {receiver} not logged in')
            self.respond(f'user {receiver} not logged in', clientAddr, tcp_socket)
            return

        if self.USERS.get_socket_type(receiver) == 'tcp':
            tcp_socket = self.USERS.get_socket(receiver)
            print(f'sending message to {receiver} on {tcp_socket.getsockname()}')
        else:
            clientAddr = self.USERS.get_udp_client_addr(receiver)
            tcp_socket = None


        self.respond(f'<file: {sender}> {message}', clientAddr, tcp_socket)

    def handle_broadcast(self, data, clientAddr, tcp_socket=None):
        print(f'handle_broadcast, {data}')
        print(clientAddr)
        sender, message = data[0], convert_coma(data[1])
        message = f'<broadcast: {sender}> {message}'

        for user in self.USERS:
            # user pode ser uma string ou uma tupla, se for uma string len(user[0]) == 1
            if len(user[0]) == 1: continue
            print(user, clientAddr)
            if self.USERS.get_socket_type(user) == 'tcp':
                tcp_socket = self.USERS.get_socket(user)
            else:
                clientAddr = self.USERS.get_udp_client_addr(user)
                tcp_socket = None
            self.respond(message, clientAddr, tcp_socket)

    def handle_private_message(self, data, clientAddr, tcp_socket=None):
        print('handle_private_message, ' + str(data))
        print(data, clientAddr)
        receiver, sender, message = data[0], data[1], convert_coma(data[2])
        print(receiver, '-', message)

        if (receiver not in self.USERS):
            print(f'user {receiver} not logged in')
            self.respond(f'user {receiver} not logged in', clientAddr, tcp_socket)
            return

        if self.USERS.get_socket_type(receiver) == 'tcp':
            tcp_socket = self.USERS.get_socket(receiver)
            print(f'sending message to {receiver} on {tcp_socket.getsockname()}')
        else:
            clientAddr = self.USERS.get_udp_client_addr(receiver)
            tcp_socket = None
        print('----------------------------')
        print(f'Responding {message[0]}')
        
        message = f'<MSG: {sender}> {message}'

        self.respond(message, clientAddr, tcp_socket)

    def handle_login(self, login_data, clientAddr, tcp_socket:socket=None):
        print(f'handling login {login_data[0]}')
        if (login_data[0] in self.USERS):
            self.respond(f'User {login_data[0]} already logged in', clientAddr, tcp_socket)
            return
        
        if (tcp_socket):
            self.USERS.add(login_data[0], clientAddr[0], clientAddr[1], tcp_socket)
        else:
            self.USERS.add(login_data[0], clientAddr[0], clientAddr[1], tcp_socket)
        pprint.pprint(str(self.USERS))
        self.respond(f'<REG> Login success', clientAddr, tcp_socket)
    
    def handle_logout(self, _, clientAddr, tcp_socket:socket=None):
        print('handle_logout')
        user = self.USERS.get_username(clientAddr)
        if (user):
            self.USERS.remove(user)
        print(f'handling logout {clientAddr} {tcp_socket} {user}')
        pprint.pprint(str(self.USERS))

    def respond(self, message, clientAddr, tcp_socket:socket=None, message_type='data'):
        if (tcp_socket):
            tcp_socket.send(message.encode())
            return
        print(f'sending message {message} to {clientAddr}')
        if (message_type == 'data'):
            socket = self.UDP_DATA_SOCKET
        else:
            socket = self.UDP_CONTROLL_SOCKET
        
        socket.sendto(message.encode(), clientAddr)

    def run(self):
        print('running server')
        threading.Thread(target=self.listen_udp, args=(self.UDP_CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen_udp, args=(self.UDP_DATA_SOCKET,)).start()

        threading.Thread(target=self.listen_tcp, args=(self.TCP_CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen_tcp, args=(self.TCP_DATA_SOCKET,)).start()

        input()

    def unpack_message(self, message):
        data = message.strip('][').split(', ')
        return data
    
def main():
    server_ip = sys.argv[1]
    server = Server(server_ip, 40000)
    try:
        server.run()
    except KeyboardInterrupt:
        print('bye')

main()
