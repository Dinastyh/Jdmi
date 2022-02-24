import errno
import select
import socket
import fcntl
import os


class Client:
    def __init__(self, fileno: int, port: int, address, connection):
        self.fileno = fileno
        self.port = port
        self.address = address
        self.queue = []
        self.connection = connection


fib = {}


def main() -> None:

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Ip -> "+IPAddr)
    print("Port -> 25565")
    server_socket.bind((IPAddr, 25565))
    server_socket.listen()

    server_socket.setblocking(False)

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)
    try:
        while True:
            events = epoll.poll(1)
            send = []
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    print("Connection")
                    connection, address = server_socket.accept()

                    client_connection = Client(connection.fileno(), 25565, address, connection)
                    fib[connection.fileno()] = client_connection
                    fcntl.fcntl(connection, fcntl.F_SETFL, os.O_NONBLOCK)
                    epoll.register(client_connection.fileno, select.EPOLLIN | select.EPOLLOUT)
                elif event & select.EPOLLIN:
                    client_connection = fib[fileno]
                    while True:
                        try:
                            msg = client_connection.connection.recv(2048)
                            print(msg)
                            print("read")
                            if msg == "":
                                break
                        except IOError as e:
                            if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                                break
                            raise
                        print(msg)
                        queue_msg(client_connection, msg)
                elif event & select.EPOLLOUT:
                    client_connection = fib[fileno]
                    send.append(client_connection)
                else:
                    client_connection = fib[fileno]
                    fib.pop(client_connection.fileno)
                    socket.close(client_connection.fileno)
            for client_connection in send:
                send_msg(client_connection)
            send = []
    finally:
        epoll.close()


def send_msg(client_connection: Client) -> None:
    while len(client_connection.queue) > 0:
        msg = client_connection.queue[0]
        print(msg)
        print("send")
        try:
            client_connection.connection.send(msg)
        except IOError as e:
            if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                break
            raise
        client_connection.queue.pop(0)


def queue_msg(sender: Client, msg: str) -> None:
    if msg == "":
        return

    for connection in fib.values():
        if connection.fileno != sender.fileno:
            connection.queue.append(msg)


if __name__ == "__main__":
    main()