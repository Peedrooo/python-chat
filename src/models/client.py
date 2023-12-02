import socket
import threading
import os
from src.models.server_manager import ServerManager

class Client(ServerManager):

    def __init__(self):
        self.client = None
        self.nickname = None
        self.password = None
        self.stop_thread = False

    def receive(self):
        while True:
            if self.stop_thread:
                break
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                    next_message = self.client.recv(1024).decode('ascii')
                    if next_message == 'PASS':
                        self.client.send(self.password.encode('ascii'))
                        if self.client.recv(1024).decode('ascii') == 'REFUSE':
                            print("Connection is Refused !! Wrong Password")
                            return
                    elif next_message == 'BAN':
                        print('Connection Refused due to Ban')
                        self.client.close()
                        return
                else:
                    print(message)
            except socket.error:
                print('Error Occured while Connecting')
                self.client.close()
                break
    
    def write(self):
        while True:
            if self.stop_thread:
                break
            message = f'{self.nickname}: {input("")}'
            if message[len(self.nickname)+2:].startswith('/'):
                if self.nickname == 'admin':
                    if message[len(self.nickname)+2:].startswith('/kick'):
                        self.client.send(f'KICK {message[len(self.nickname)+2+6:]}'.encode('ascii'))
                    elif message[len(self.nickname)+2:].startswith('/ban'):
                        self.client.send(f'BAN {message[len(self.nickname)+2+5:]}'.encode('ascii'))
                else:
                    print("Commands can only be executed by the admin")
            else:
                self.client.send(message.encode('ascii'))

    def start(self):
        while True:
            os.system('cls||clear')
            option = input("(1)Enter server\n(2)Add server\n")
            if option == '1':
                self.enter_server()
                break
            elif option == '2':
                self.add_server()

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        write_thread = threading.Thread(target=self.write)
        write_thread.start()
