import select
import server.client as client
import socket

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen()

    server_socket.setblocking(0)

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)

    fib = {}
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            if fileno == server_socket.fileno():
                connection, address = server_socket.accept()
                client_connection = client.Client(fileno, 25565, address)
                fib[fileno] = client_connection
            elif event & select.EPOLLIN:
                client_connection = fib[fileno]
                if client_connection.size_uncompleted != 0:
                    #read the size...
            elif event & select.EPOLLOUT:
                #set true to write
            else:
                # deco
