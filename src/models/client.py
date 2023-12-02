import socket
import threading
import json
import os

class Client():

    def __init__(self):
        self.client = None
        self.nickname = None
        self.password = None
        self.stop_thread = False

    def enter_server(self):
        os.system('cls||clear')
        with open('src/resources/servers.json') as f:
            data = json.load(f)
        print('Servers: ', end="")
        for servers in data:
            print(servers, end=" ")
        print('\nServer Name:',end=" ")
        server_name = input()
        print('Nickname:', end=" ")
        self.nickname = input()
        if self.nickname == 'admin':
            print("Enter Password for Admin:", end=" ")
            self.password = input()

        ip = data[server_name]["ip"]
        port = data[server_name]["port"]
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))

    def add_server(self):
        os.system('cls||clear')
        server_name = input("Enter a name for the server:")
        server_ip = input("Enter the ip address of the server:")
        server_port = int(input("Enter the port number of the server:"))

        with open('src/resources/servers.json', 'r') as f:
            data = json.load(f)
        with open('src/resources/servers.json', 'w') as f:
            data[server_name] = {"ip": server_ip, "port": server_port}
            json.dump(data, f, indent=4)

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
        self.enter_server()
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        write_thread = threading.Thread(target=self.write)
        write_thread.start()
