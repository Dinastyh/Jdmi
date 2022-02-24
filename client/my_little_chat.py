from enum import Enum

class EventType(Enum):
    READ = 1
    RECV = 2
    SEND = 3
    NONE = 4

class Connection:

    def __init__(self, name, address, port, epoll, queue, fds):
        self.username = name
        self.ip_address = address
        self.port = port
        self.epoll = epoll
        self.queue = queue
        self.fds = fds

    def connect(name, ip_address, port):
        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        epoll = select.epoll()
        epoll.register(fd, select.EPOLLIN)

        queue = []
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(ip_address)
        print(port)
        server_socket.connect((ip_address, int(port)))
        server_socket.setblocking(False)

        epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLOUT)

        return Connection(name, ip_address, port, epoll, queue, fd)

    def close(connection) -> None:
        connection.epoll.close()

    def receive(connection) -> str:
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
        return msg

    def send(connection) -> None:
        while len(connection.queue) > 0:
            msg = connection.queue[0]
            try:
                server_socket.send(msg.encode())
            except IOError as e:
                if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                    break
                raise

    def readInput(connection) -> None:
        msg = ""
        while True:
            tmp = sys.stdin.read(2048)
            if not tmp:
                break
            msg += tmp
        if msg:
            msg = "[" + connection.name + "] -> " + msg
            connection.queue.append(msg)

    def waitEvent(self) -> EventType:
        events = self.epoll.poll(1)
        for fileno, event in events:
            if event & select.EPOLLIN:
                if fileno == self.fd:
                    return EventType.READ
                    #connection.readInput()
                else:
                    return EventType.RECV
                    #msg = connection.receive()
                    #print(msg)
            else:
                return EventType.SEND
                #connection.send()
        return EventType.NONE