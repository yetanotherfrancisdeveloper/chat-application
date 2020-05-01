from datetime import datetime
import socket
import threading


class TCPHandler:
    """Class used to handle a TCP connection for a server-client chat

        ----------------------------------------------------------------

        Attributes
        ----------
        host : str
            name of the server host
        port : int
            number of the port bound to the host
        hostname : str
            name of the host
        socket_server = tuple
            socket of the server


        Methods
        -------
        connection_handler
            handling of the incoming request
        receiving
            ask the client for a username and receive his messages
        sending
            send messages to the client connected
        disconnection
            disconnect the client
        """

    def __init__(self, host_server, port_server, hostname):
        """Creating the server's socket."""

        self.host = host_server
        self.port = port_server
        self.hostname = hostname
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind((self.host, self.port))
        self.socket_server.listen(5)

    def connection_handler(self):
        """Handle the incoming request, starting the threads to send and receive messages simultaneously,
        manage exception handling in case of the closing of the server."""

        try:
            client_socket, address = self.socket_server.accept()
            print('Press "CTRL+C" to close the server.')
            print(f'{address[0]}::{address[1]} is connected')
            sending_thread = threading.Thread(target=self.sending, args=(client_socket, ))
            receiving_thread = threading.Thread(target=self.receiving, args=(client_socket, ))
            sending_thread.start()
            receiving_thread.start()
            try:
                sending_thread.join()
                receiving_thread.join()
            except KeyboardInterrupt:
                print('Server closed!')
                client_socket.sendall(bytes('The server has disconnected! '
                                            'You may leave the chat.', 'utf-8'))
                client_socket.close()
                self.socket_server.close()

        except KeyboardInterrupt:
            print('Server closed!')
            self.socket_server.close()

    def receiving(self, sock):
        """Receive and print messages from the client connected."""

        try:
            sock.sendall(bytes('Enter your username (Type "[quit]" or close the window to quit the chat):\n', 'utf-8'))
            client_name = sock.recv(2048).decode()
            if client_name == '[quit]':
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
                    elif message:
                        current_time = datetime.now()
                        clock_time = current_time.strftime('%H:%M:%S')
                        print(f'[{clock_time}] {client_name} > {message}')
                    else:
                        self.disconnection(sock, client_name)
        except ConnectionAbortedError:
            pass

    def sending(self, sock):
        """Send messages to the client connected and print the message sent."""

        try:
            while True:
                input_message = input()
                current_time = datetime.now()
                clock_time = current_time.strftime('%H:%M:%S')
                message = f'{self.hostname} > {input_message}'
                print(f'[{clock_time}] {message}')
                sock.sendall(bytes(f'[{clock_time}] {message}\r\n', 'utf-8'))
        except EOFError:
            pass
        except OSError:
            print('The connection has been terminated.')

    def disconnection(self, sock, username):
        """Closing the socket of the client when he is disconnecting, print that the user has left the chat."""

        sock.close()
        print(f'{username} left the chat!')


def main():
    host = socket.gethostname()
    port = 10000
    my_ip = socket.gethostbyname(host)
    print('My IP is', my_ip)
    print('The host name is:', host)
    print(f"Waiting for someone to connect to {host}::{port}")
    running_server = TCPHandler('', port, host)
    running_server.connection_handler()


if __name__ == "__main__":
    main()
