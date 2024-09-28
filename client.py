from socket import socket, timeout, AF_INET, SOCK_DGRAM, SOCK_STREAM
import threading
from sys import argv
import base64

#Trata o formato da mensagem
generate_message = lambda data: '[' + ", ".join(list(map(replace_coma, data))) + ']'

#Evitar conflitos na hora de separar os dados
replace_coma = lambda txt: str(txt).replace(',', '%;')

class Client:
    def __init__(self, server_ip, server_port, socket_type='tcp'):
        #tipo do socket
        self.SOCKET_TYPE = socket_type
        self.SERVER_IP = server_ip
        self.SERVER_PORT = int(server_port)
        self.DATA_SOCKET = socket(AF_INET, SOCK_STREAM) if socket_type == 'tcp' else socket(AF_INET, SOCK_DGRAM)
        self.CONTROLL_SOCKET = socket(AF_INET, SOCK_STREAM) if socket_type == 'tcp' else socket(AF_INET, SOCK_DGRAM)
        self.file_counter = 0
        self.username = None

    #Conecta os sockets no servidor
    def connect(self):
        print(f'connecting to {self.SERVER_IP}:{self.SERVER_PORT}')
        self.CONTROLL_SOCKET.connect((self.SERVER_IP, self.SERVER_PORT + 2))
        self.DATA_SOCKET.connect((self.SERVER_IP, self.SERVER_PORT + 3))
    
    #Utilizado para leitura de arquivos, decodifica base64 
    def is_base64(self, message):
        message = message.split("b'")[1].replace("'", "")
        decoded_message = base64.b64decode(message)
        return decoded_message
    
    #Fecha os sockets
    def close(self):
        self.CONTROLL_SOCKET.close()
        self.DATA_SOCKET.close()

    #Envia a mensagem
    def send_message(self, msg, socket:socket):
        msg = generate_message(msg)
        if self.SOCKET_TYPE == 'tcp':
            socket.send(msg.encode())
        else:
            socket.sendto(msg.encode(), (self.SERVER_IP, self.SERVER_PORT))

    #Trata a mensagem recebida
    def handle_message(self, message):
        if message.startswith('<file'): # Verifica se a mensagem contém um arquivo
            file_text = self.is_base64(message) # Decodifica o arquivo
            file_path = f'output({self.file_counter}).txt' # Cria um arquivo de saída
            with open(file_path, 'wb') as file:
                file.write(file_text)
            self.file_counter += 1
        print(message)

    # Método para receber mensagens via socket TCP
    def handle_tcp_socket(self, socket:socket):
        message = socket.recv(2048) # Recebe a mensagem
        if not message:  
            print('closing socket') # Caso a mensagem seja vazia, fecha o socket
            socket.close()
            return
        message = message.decode()
        self.handle_message(message)

    # Método para receber mensagens via socket UDP
    def handle_udp_socket(self, socket:socket):
        message, _ = socket.recvfrom(2048)
        if not message:  
            print('closing socket')
            socket.close()
            return
        message = message.decode()
        self.handle_message(message)

    # Método para escutar mensagens em loop
    def listen(self, socket:socket):
        socket.settimeout(2)
        while True:
            try:
                if self.SOCKET_TYPE == 'tcp':
                    self.handle_tcp_socket(socket)
                else:
                    self.handle_udp_socket(socket)
                pass
            except timeout:
                # Encerra se a thread principal não estiver mais ativa
                if not threading.main_thread().is_alive(): break
            except Exception as e:
                print(e)
                break

    #Mensagem para usuario especifico	
    def private_message(self, username, message):
        self.send_message(['MSG', username, self.username, message], self.DATA_SOCKET)

    #Arquivo para usuario especifico
    def private_message_with_file(self, username, file_path):
        with open(file_path, 'rb') as file:
            content = file.read()
        self.send_message(['MSGF', username, self.username, base64.b64encode(content)], self.DATA_SOCKET)
    
    #Conecta usuario no servidor
    def login(self, username):
        self.username = username #Armazena nome do usuario localmente
        self.send_message(['REG', username], self.CONTROLL_SOCKET)

    def logout(self):
        self.username = None #Limpa o nome do usuario
        self.send_message(['LOGOUT'], self.CONTROLL_SOCKET)
        
    #Mensagem para todos os usuarios
    def broadcast_message(self, message):
        self.send_message(['MSGA', self.username, message], self.DATA_SOCKET)
        pass

    #Trata a entrada do usuario
    def handle_user_input(self):
        try:
            msg = input()
        except KeyboardInterrupt:
            return -1
        join_message = lambda msg: ' '.join(msg)
        if (msg.startswith('/')):
            msg = msg[1:].split(' ') # Separa a mensagem
            option = msg[0]
            if (option == 'exit'): return -1
            elif (option == 'MSG'): 
                self.private_message(msg[1], join_message(msg[2:]))
            elif (option == 'MSGF'): 
                self.private_message_with_file(msg[1], join_message(msg[2:]))
            elif (option == 'MSGA'):
                self.broadcast_message(join_message(msg[1:]))
            elif (option == 'REG'):
                self.login(msg[1])
            elif (option == 'LOGOUT'):
                self.logout()
            # else: print('invalid command')
        return 0

    def run(self):
        if (self.SOCKET_TYPE == 'tcp'):
            print('running tcp client')
            self.connect()
        
        # Inicia as threads para escutar os sockets
        threading.Thread(target=self.listen, args=(self.CONTROLL_SOCKET,)).start()
        threading.Thread(target=self.listen, args=(self.DATA_SOCKET,)).start()

        # Loop para tratar a entrada do usuário
        while True:
            if (self.handle_user_input() == -1): break

def main():
    server_ip = argv[1]
    protocol  = argv[2]
    client = Client(server_ip, 40000, protocol)
    try:
        client.run()
    except timeout:
        print('teste')
    except KeyboardInterrupt:
        pass
    print('closing client')
    client.close()


main()
