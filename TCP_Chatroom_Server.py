from datetime import datetime
import socket
import threading
import sys


class TCPHandlerChatRoom:
    """Class used to handle multiple TCP connections for a chat room

    ----------------------------------------------------------------

    Attributes
    ----------
    messages : list
        stores the messages received from the clients
    clients_info : dict
        stores socket and address of the clients connected
    clients_names : dict
        Stores username and address of the clients connected
    received_messages : int
        set to zero and used to send all the messages received to all the clients connected
    host : str
        host's address
    port : int
        number of the port bound to the host
    socket_server = tuple
        socket of the server


    Methods
    -------
    connections_handler
        handling of incoming requests
    get_username
        ask the client for a username
    clients_handler
        receive and broadcast messages
    clients_disconnection
        disconnect the client
    closing_server_message
        waits for the server to close and warns the clients connected when closing
    closing
        handle the closing of the server
    """

    messages = []
    clients_info = {}
    clients_names = {}
    received_messages = 0

    def __init__(self, host_server, port_server):
        """Creating the sever's socket."""

        self.host = host_server
        self.port = port_server
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # UPDATE Reuse address in case of many subsequent tries because of the time wait after closing the connection
        self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket_server.bind((self.host, self.port))
        self.socket_server.listen(5)

    def connections_handler(self):
        """Handling incoming requests, starting the thread to manage
        multiple clients and the thread to manage the closing of the server."""

        closing_thread = threading.Thread(target=self.closing_server_message)
        closing_thread.start()
        while True:
            try:
                # The exception is needed because of the closing of the server.
                client_socket, address = self.socket_server.accept()
                self.clients_info[client_socket] = address
                client_thread = threading.Thread(target=self.clients_handler, args=(client_socket, address))
                client_thread.start()
            except KeyboardInterrupt:
                self.closing()
            except OSError:
                self.closing()

    def get_username(self, sock, address):
        """Ask the client for a username, welcome him to the chat and warning him of the option to quit."""

        try:
            print(f'{address[0]}::{address[1]} is connected')
            sock.sendall(bytes('Enter your username (Type "[quit]" or close the window to quit the chat):\n', 'utf-8'))
            client_name = sock.recv(2048).decode()
            if client_name == '[quit]':
                print(f'{address[0]}::{address[1]} left before joining ...')
                del self.clients_info[sock]
                # UPDATE Double two-way handshake
                sock.shutdown(1)

                sock.close()
            else:
                while client_name in self.clients_names.values():
                    sock.sendall(bytes("This username has been already taken, sorry! "
                                       "Enter another username:\n", "utf-8"))
                    client_name = sock.recv(2048).decode()
                print(client_name, "has joined the chat room!")
                self.clients_names[address] = client_name
                sock.sendall(bytes(f'{client_name} welcome to the chat room!\n', "utf-8"))
                sock.sendall(bytes(f'There are {len(self.clients_info)} users available in the chat including you.\n'
                                   f'Type "[quit]" or close the window to quit the chat room. '
                                   f'Enjoy!\n', "utf-8"))
        except ConnectionAbortedError:
            pass

    def clients_handler(self, client, address):
        """Receiving and broadcasting messages from and to multiple clients"""

        try:
            # Add thread for username
            self.get_username(client, address)
            while True:
                for client_sock in list(self.clients_info.keys()):
                    if client_sock == client:
                        message = client_sock.recv(2048).decode()
                        if message == '[quit]':
                            self.client_disconnection(client_sock)
                        elif message:
                            self.messages.append({
                                "username": self.clients_names[self.clients_info[client_sock]],
                                "message": message
                            })
                            print(f'{self.clients_names[self.clients_info[client_sock]]} has sent a message! '
                                  f'Let\'s celebrate!')
                            if self.received_messages < len(self.messages):
                                for i in range(self.received_messages, len(self.messages)):
                                    user = self.messages[i]["username"]
                                    message = self.messages[i]["message"]
                                    for j in range(len(self.clients_info)):
                                        if user != list(self.clients_names.values())[j]:
                                            current_time = datetime.now()
                                            clock_time = current_time.strftime("%H:%M:%S")
                                            list(self.clients_info.keys())[j].sendall(bytes(f'[{clock_time}] {user} > '
                                                                                            f'{message}\r\n', "utf-8"))
                                    del message
                                self.received_messages += 1
                        else:
                            self.client_disconnection(client_sock)
        except OSError:
            pass

    def client_disconnection(self, disconnecting_sock):
        """Handle the client disconnection closing his socket and deleting his data"""

        for client_sock in list(self.clients_info.keys()):
            if client_sock != disconnecting_sock:
                client_sock.sendall(bytes(self.clients_names[self.clients_info[disconnecting_sock]] +
                                          " has left us, bye!\n", "utf-8"))
        print(self.clients_names[self.clients_info[disconnecting_sock]], "has left ...")
        del self.clients_names[self.clients_info[disconnecting_sock]]
        del self.clients_info[disconnecting_sock]
        # UPDATE Double two-way handshake
        disconnecting_sock.shutdown(1)

        disconnecting_sock.close()

    def closing_server_message(self):
        """Once the server decides to close, send a warning message to all the clients and close."""

        try:
            input('Press "Enter" or "CTRL+C" to close the server.\n')
        except EOFError:
            pass
        if self.clients_info:
            for client_sock in list(self.clients_info.keys()):
                client_sock.sendall(bytes('The server has disconnected! You may leave the chat.', 'utf-8'))
        print('\nThe server is closed.')
        self.closing()

    def closing(self):
        """Handle the closing of the server. Closes the sockets of
        the clients connected, the server's socket and exits the program"""
        try:
            if self.clients_info:
                for client_sock in list(self.clients_info.keys()):
                    # UPDATE Double two-way handshake
                    client_sock.shutdown(1)

                    client_sock.close()
                self.socket_server.close()
                sys.exit()
            else:
                self.socket_server.close()
                sys.exit()
        except OSError:
            sys.exit()


def main():
    host = socket.gethostname()
    port = 10000
    my_ip = socket.gethostbyname(host)
    print('My IP is', my_ip)
    print('The host name is:', host)
    print(f"Waiting for someone to connect to {host}::{port}")
    running_server = TCPHandlerChatRoom('', port)
    running_server.connections_handler()


if __name__ == "__main__":
    main()
