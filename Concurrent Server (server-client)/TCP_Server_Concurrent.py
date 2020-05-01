from requests import get
from datetime import datetime
import socket
import threading
import sys


class TCPHandler:

    clients = []

    def __init__(self, host_server, port_server, hostname):
        self.host = host_server
        self.port = port_server
        self.hostname = hostname
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind((self.host, self.port))
        self.socket_server.listen(5)

    def connections_handler(self):
        closing_thread = threading.Thread(target=self.closing_server_message)
        closing_thread.daemon = True
        closing_thread.start()
        while True:
            try:
                client_socket, address = self.socket_server.accept()
                if self.clients:
                    client_socket.sendall(bytes(f'The {self.hostname} is busy with another client. '
                                                f'Please try again later!\n'
                                                f'Sorry for the inconvenience ...\n', 'utf-8'))
                    print('A new client tried to connect.')
                    client_socket.close()
                else:
                    print('Press "CTRL+C" to close the server.')
                    self.clients.append(client_socket)
                    print(f'{address[0]}::{address[1]} is connected')
                    sending_thread = threading.Thread(target=self.sending, args=(client_socket, ))
                    receiving_thread = threading.Thread(target=self.receiving, args=(client_socket, ))
                    sending_thread.setDaemon(True)
                    receiving_thread.setDaemon(True)
                    sending_thread.start()
                    receiving_thread.start()
            except KeyboardInterrupt:
                self.closing()
            except OSError:
                self.closing()

    def receiving(self, sock):
        sock.sendall(bytes('Enter your username (Type "[quit]" or close the window to quit the chat):\n', 'utf-8'))
        client_name = sock.recv(2048).decode()
        if client_name == '[quit]':
            self.clients.clear()
            sock.close()
            print('User left the chat before joining.')
        else:
            sock.sendall(bytes(f'Welcome to the chat with {self.hostname}!\nStart typing your messages!\n'
                               f'Type "[quit]" or close the window to quit the chat.\n', 'utf-8'))
            print(client_name, 'has joined the chat!')
            while True:
                message = sock.recv(1024).decode()
                if message == '[quit]':
                    self.disconnection(sock, client_name)
                    break
                elif len(message) == 0:
                    self.disconnection(sock, client_name)
                    break
                current_time = datetime.now()
                clock_time = current_time.strftime('%H:%M:%S')
                print(f'[{clock_time}] {client_name} > {message}')

    def sending(self, sock):
        try:
            while True:
                input_message = input()
                sending_sock = sock
                current_time = datetime.now()
                clock_time = current_time.strftime('%H:%M:%S')
                message = f'{self.hostname} > {input_message}'
                if sending_sock != sock:
                    break
                else:
                    print(f'[{clock_time}] {message}')
                    sock.sendall(bytes(f'[{clock_time}] {message}\r\n', 'utf-8'))
        except EOFError:
            pass

    def disconnection(self, sock, username):
        self.clients.clear()
        sock.close()
        print(f'{username} left the chat!')

    def closing_server_message(self):
        try:
            input('')
        except EOFError:
            if self.clients:
                for client_sock in self.clients:
                    client_sock.sendall(bytes('The server has disconnected! You may leave the chat.', 'utf-8'))
            print('\nThe server is closed.')
            self.closing()

    def closing(self):
        self.socket_server.close()
        sys.exit()


def main():
    host = socket.gethostname()
    port = 10000
    my_public_ip = get('https://api.ipify.org').text
    print('My IP is', my_public_ip)
    print('The host name is:', host)
    print(f"Waiting for someone to connect to {host}::{port}")
    # print('Press "CTRL+C" to close the server.')
    running_server = TCPHandler('', port, host)
    running_server.connections_handler()


if __name__ == "__main__":
    main()
