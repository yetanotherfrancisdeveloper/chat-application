from tkinter import *
from tkinter import messagebox
from datetime import datetime
import pathlib
import socket
import threading
import pygame


# Creating the server's socket.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Notification sound.
pygame.mixer.init()
notification = pygame.mixer.Sound(str(pathlib.Path('Media/App_Sounds/soft_notification.wav')))
# Tkinter attributes for the GUI.
base = Tk()
text_frame = Frame(base, width=720, height=480)
text = Text(text_frame, borderwidth=3, relief='sunken',  bg='#00134d')
frame = LabelFrame(text_frame, padx=50, pady=100)
input_user = StringVar()
input_field = Entry(base, text=input_user, bg='black', fg='green', insertbackground='green', relief='sunken')


def chat_rules():
    """Rules of the chat displayed on the right of the window."""

    rule1 = Label(frame, text='Be kind', bd=1, relief=SUNKEN, fg='#473b83')
    rule1_text = Label(frame, text='Giving constructive feedback is good.\n'
                                   'Being unnecessarily mean isn’t what we\n'
                                   'do here. Make sure you take the time\n '
                                   'to evaluate which you are doing\n'
                                   'before you post.\n')
    rule2 = Label(frame, text="Respect other humans", bd=1, relief=SUNKEN, fg='#473b83')
    rule2_text = Label(frame, text="Sexually objectifying, creeping on,\n"
                                   "describing violent actions toward,\n"
                                   "describing your physical reactions to,\n"
                                   "or otherwise dehumanizing others is not\n"
                                   "tolerated. You can insult HAL9000\n"
                                   "if you want though, he does NOT care!\n")
    rule1.grid(row=0, column=1, columnspan=10)
    rule1_text.grid(row=1, column=1, columnspan=10)
    rule2.grid(row=2, column=1, columnspan=10)
    rule2_text.grid(row=3, column=1, columnspan=10)


def sending(event):
    """Send messages to the server. The messages are inserted in the input line of the
    window on the bottom, the messages sent are displayed on the main frame of the window."""

    try:
        current_time = datetime.now()
        clock_time = current_time.strftime('%H:%M:%S')
        input_get = input_user.get()
        if input_get == '[quit]':
            client_socket.sendall(bytes('[quit]', 'utf-8'))
            # UPDATE Sending FIN packet
            client_socket.shutdown(1)

            client_socket.close()
            base.destroy()
        else:
            text.configure(state='normal')
            text.insert(END, '[{}] You: {}\r\n'.format(clock_time, input_get))
            text.yview(END)
            text.configure(state='disabled')
            input_user.set('')
            client_socket.sendall(bytes(input_get, 'utf-8'))
    except ConnectionResetError:
        print('The connection has been terminated. Close the window.')


def receiving(event):
    """Receive messages from the server. They are displayed on the on the main frame of the window."""

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message:
                text.configure(state='normal')
                text.insert(END, '{}'.format(message))
                notification_sound()
                text.yview(END)
                text.configure(state='disabled')
            else:
                # UPDATE Sending FIN packet
                client_socket.shutdown(1)

                client_socket.close()
                break
    except ConnectionAbortedError:
        print('Disconnected!')
    except ConnectionResetError:
        print('Disconnected!')
    except OSError:
        print('Disconnected successfully! (FIN)')


def gui():
    """Creation and management of the GUI."""

    base.title('The HAL9000 Chat Room')
    base.iconbitmap(str(pathlib.Path('Media/App_Images/speaking-bubbles-black.ico')))
    text_frame.pack(fill=BOTH, expand=True)
    text_frame.grid_propagate(True)
    text_frame.grid_rowconfigure(0, weight=3)
    text_frame.grid_columnconfigure(0, weight=3)
    text.config(font=('consolas', 10), undo=True, wrap='word', state='disabled', fg='white')
    text.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
    frame.grid(row=0, column=1, rowspan=2)
    chat_rules()
    scrollbar = Scrollbar(text_frame, command=text.yview)
    scrollbar.grid(row=0, column=2, sticky='nsew')
    text['yscrollcommand'] = scrollbar.set
    input_field.pack(side=BOTTOM, fill=X, anchor=W)
    input_field.bind('<Return>', sending)
    base.protocol('WM_DELETE_WINDOW', closing_window)
    base.mainloop()


def notification_sound():
    """Play the notifications sound."""

    notification.play()


def closing_window():
    """Attempts to disconnect when closing the GUI's window. A confirmation box pops up when closing."""

    if messagebox.askokcancel('Closing ...', 'Do you want to close the chat?'):
        try:
            client_socket.sendall(bytes('[quit]', 'utf-8'))
        except ConnectionResetError:
            print('Tried to disconnect when closing window, but you were already disconnected.')
            base.destroy()
        except OSError:
            print('Disconnected successfully closing window! (FIN)')
            base.destroy()
        # UPDATE Sending FIN packet
        try:
            client_socket.shutdown(1)

            client_socket.close()
        except OSError:
            print('Server disconnected! (FIN)')

        try:
            base.destroy()
        except TclError:
            print('Window closed.')


def main():
    # Variable used to connect with local host
    my_server_name = socket.gethostname()
    # Variable used to connect to other hosts
    server_ip = str(input('Enter the IP of the server to connect to: '))

    server_port = int(input('Enter the port number: '))
    client_socket.connect((my_server_name, server_port))
    # Thread to receive messages while sending
    receiving_thread = threading.Thread(target=receiving, args=(client_socket, ))
    receiving_thread.start()
    gui()


if __name__ == "__main__":
    main()
