import socket
import threading
from time import sleep

class Server():

    def __init__(self, host = '192.168.1.14', port = 8080, qnt_users = 10):
        self.host = host
        self.port = port
        self.qnt_users = qnt_users
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET is IPv4 and SOCK_STREAM is TCP
        self.server.bind((self.host, self.port)) # associa o socket a um endereço específico
        self.server.listen()
        self.clients = []
        self.nicknames = []
    
    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message.decode('ascii').startswith('KICK'):
                    if self.nicknames[self.clients.index(client)] == 'admin':
                        name_to_kick = message.decode('ascii')[5:]
                        self.kick_user(name_to_kick)
                    else:
                        client.send('Command Refused!'.encode('ascii'))
                elif message.decode('ascii').startswith('BAN'):
                    if self.nicknames[self.clients.index(client)] == 'admin':
                        name_to_ban = message.decode('ascii')[4:]
                        self.kick_user(name_to_ban)
                        with open('src/resources/bans.txt', 'a') as f:
                            f.write(f'{name_to_ban}\n')
                        print(f'{name_to_ban} was banned by the Admin!')
                    else:
                        client.send('Command Refused!'.encode('ascii'))
                else:
                    self.broadcast(message)  # As soon as message received, broadcast it.

            except socket.error:
                if client in self.clients:
                    index = self.clients.index(client)
                    # Index is used to remove client from list after getting disconnected
                    self.clients.remove(client)
                    client.close()
                    nickname = self.nicknames[index]
                    self.broadcast(f'{nickname} left the Chat!'.encode('ascii'))
                    self.nicknames.remove(nickname)
                    break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")

            if len(self.clients) < self.qnt_users:

                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')

                with open('src/resources/bans.txt', 'r') as f:
                    bans = f.readlines()

                if nickname + '\n' in bans:
                    client.send('BAN'.encode('ascii'))
                    client.close()
                    continue

                if nickname == 'admin':
                    client.send('PASS'.encode('ascii'))
                    password = client.recv(1024).decode('ascii')

                    if password != 'admin':
                        client.send('REFUSE'.encode('ascii'))
                        client.close()
                        continue

                self.nicknames.append(nickname)
                self.clients.append(client)

                self.broadcast(f"{nickname} joined the chat!".encode('ascii'))
                client.send('Connected to the server!'.encode('ascii'))

                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()

            else:
                print(f'{str(address)} was refused to connect: too many clients')
                client.send('Too many clients!'.encode('ascii'))
                sleep(3)
                client.close()

    def kick_user(self, name):
        if name in self.nicknames:
            name_index = self.nicknames.index(name)
            client_to_kick = self.clients[name_index]
            self.clients.remove(client_to_kick)
            client_to_kick.send('You were kicked by an admin!'.encode('ascii'))
            client_to_kick.close()
            self.nicknames.remove(name)
            self.broadcast(f'{name} was kicked by an admin!'.encode('ascii'))

    def start(self):
        print(f'Server is listening on {self.host}:{self.port}')
        self.receive()
