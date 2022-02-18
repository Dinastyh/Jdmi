class Client:
    def __init__(self, fileno, port, address):
        self.fileno = fileno
        self.port = port
        self.address = address
        self.queue = []
        self.uncompleted = ""
        self.size_uncompleted = 0
