from enum import Enum
import select
import socket
import os
import sys
import fcntl
import errno

class EventType(Enum):
    READ = 1
    RECV = 2
    SEND = 3
    NONE = 4

class Connection:

    def __init__(self, name, address, port):
        self.username = name
        self.ip_address = address
        self.port = port

        self.fds = sys.stdin.fileno()
        fl = fcntl.fcntl(self.fds, fcntl.F_GETFL)
        fcntl.fcntl(self.fds, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.epoll = select.epoll()
        self.epoll.register(self.fds, select.EPOLLIN)

        self.queue = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.ip_address)
        print(self.port)
        self.server_socket.connect((self.ip_address, int(port)))
        self.server_socket.setblocking(False)

        self.epoll.register(self.server_socket.fileno(), select.EPOLLIN | select.EPOLLOUT)

    def close(self) -> None:
        self.epoll.close()

    def receive(self) -> str:
        msg = b""
        while True:
            try:
                tmp = self.server_socket.recv(2048)
                if tmp == "":
                    break
                msg += tmp
            except IOError as e:
                if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                    break
                raise
        return msg

    def send(self) -> None:
        while len(self.queue) > 0:
            msg = self.queue[0]
            try:
                self.server_socket.send(msg.encode())
                self.queue.pop(0)
            except IOError as e:
                if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                    break
                raise

    def readInput(self) -> None:
        msg = ""
        while True:
            tmp = sys.stdin.read(2048)
            if not tmp:
                break
            msg += tmp
        if msg:
            msg = "[" + self.username + "] -> " + msg
            self.queue.append(msg)

    def waitEvent(self) -> EventType:
        events = self.epoll.poll(1)
        for fileno, event in events:
            if event & select.EPOLLIN:
                if fileno == self.fds:
                    return EventType.READ
                    #connection.readInput()
                else:
                    return EventType.RECV
                    #msg = connection.receive()
                    #print(msg)
        return EventType.SEND
                #connection.send()
        #return EventType.NONE