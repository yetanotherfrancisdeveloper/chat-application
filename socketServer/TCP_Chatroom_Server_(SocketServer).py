# from socketserver import BaseRequestHandler
# from socketserver import ThreadingTCPServer
# from socketserver import TCPServer
# from socketserver import ThreadingMixIn
from datetime import datetime
from requests import get
import socket
import socketserver
import select


clients_list = []
messages = []


class MyTCPHandler(socketserver.BaseRequestHandler):

    clients_data = {}
    username = ""
    received_messages = 0

    def setup(self):
        self.clients_data["socket"] = self.request
        self.clients_data["address"] = self.client_address
        print(f'{self.client_address[0]}::{self.client_address[1]} is connected')
        self.request.sendall(bytes("Enter your username: ", "utf-8"))

    def handle(self):
        try:
            client_name = self.request.recv(2048).decode()
            print(client_name, "has joined the chat room!")
            self.username = client_name
            self.clients_data["username"] = client_name
            clients_list.append(self.clients_data)
            self.request.sendall(bytes(f'{client_name} welcome to the chat room!', "utf-8"))
            # Insert a conditional to custom the message sent in case there is only one person in the chat
            self.request.sendall(bytes(f'There are {len(clients_list)} users available in the chat including you. '
                                       f'Enjoy!', "utf-8"))
        except Exception:
            print(f'{self.client_address[0]}::{self.client_address[1]} left before joining ...')
        try:
            while True:
                current_time = datetime.now()
                time = current_time.strftime("%H:%M:%S")
                r_list, w_list, x_list = select.select([self.request], [], [], 0.01)
                for client in r_list:
                    if client == self.request:
                        message = client.recv(2048).decode()
                        if message:
                            messages.append({
                                "username": self.username,
                                "message": message
                            })
                            print(f'{self.username} has sent a message! Let\'s celebrate!')
                if self.received_messages < len(messages):
                    for i in range(self.received_messages, len(messages)):
                        user = messages[i]["username"]
                        message = messages[i]["message"]
                        if user != self.username:
                            self.request.sendall(bytes(f'[{time}] {user} > {message}\r\n', "utf-8"))
                    self.received_messages += 1
        except Exception:
            print(f"{self.username} dead. Disconnected.")

    def finish(self):
        for index, i in enumerate(clients_list):
            if i["socket"] == self.request:
                del clients_list[index]


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def get_my_ip():
    my_ip = get('https://api.ipify.org').text
    return my_ip


def main():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 10000
    my_public_ip = get_my_ip()
    print('My IP is', my_public_ip)
    print('The host name is:', host, '({})'.format(ip))
    print(f"Waiting for someone to connect to {host}::{port}")
    server = ThreadedTCPServer(("", port), MyTCPHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
