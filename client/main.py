import select
import socket
import os
import sys
import fcntl
import errno


def main() -> None:
    name = input("Choose your name:")
    address = input("Server ip:")
    port = input("Server port:")
    # Get stdin as no blocking

    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    epoll = select.epoll()
    epoll.register(fd, select.EPOLLIN)

    queue = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(address)
    print(port)
    server_socket.connect((address, int(port)))
    server_socket.setblocking(False)

    epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLOUT)

    try:
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if event & select.EPOLLIN:
                    if fileno == fd:
                        msg = ""
                        while True:
                            tmp = sys.stdin.read(2048)
                            if not tmp:
                                break
                            msg += tmp
                        if msg:
                            msg = "[" + name + "] -> " + msg
                            queue.append(msg)
                    else:
                        msg = ""
                        while True:
                            try:
                                tmp = server_socket.recv(2048)
                                if msg == "":
                                    break
                                msg += tmp
                            except IOError as e:
                                if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                                    break
                                raise
                        print(msg)
                else:
                    while len(queue) > 0:
                        msg = queue[0]
                        try:
                            server_socket.send(msg.encode())
                        except IOError as e:
                            if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                                break
                            raise
    finally:
        epoll.close()

if __name__ == "__main__":
    main()
