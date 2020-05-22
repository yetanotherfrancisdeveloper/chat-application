<h1 align="center">

![Chat logo](Media/App_Images/Chat_Logo.png)

<h4 align="center">A simple chat application!</h4>

</h1>

---

## About

The HAL9000 chat is a chat application that can be used for a *chatroom* or a *1-1 server-client chat*. The server makes use of
the terminal of your choice in both types of chat while the client uses a simple interface.

In the *chatroom* version of the server, it accepts multiple clients allowing them to comunicate. In the *server-client chat* version
the server does not accept more than one client thus, when the comunication ends, to start a new chat it is needed to restart the server.

### Client Interface

<h1 align="center">

<h4 align="center">An example of the client interface</h4>

![Client interface](Media/App_Images/Client_interface_example.gif)

</h1>

## Extra
In the 'Extra' directory there are two scripts:

- TCP_Chatroom_Server_(SocketServer).py
- TCP_Server_Concurrent.py

The first one is a server for a chat room made with the use of the module [socketServer](https://docs.python.org/3.7/library/socketserver.html). The second one is an intermediate server that allows more clients to connect but, in case the server is
already connected to a client, they are asked to try again in a second moment.

Both the programs at the moment are not in further development and not up-to-date with the main ones. It is thus suggested to look at the programs in the main directory and only consider the extra for a glimpse at the different approaches.

## Performance
In development ...

## Requirements

- Python 3.7+
- Pygame

## Installation

Clone or download zip
- Run `pipenv install` in directory to install requirements

## Development setup

- Run `pipenv install --dev` to install dev dependencies

## License

Distributed under the MIT license. See [LICENSE](/LICENSE) for more information.
