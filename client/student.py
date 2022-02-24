import select
import socket
import os
import sys
import fcntl
import errno

import my_little_chat


def main() -> None:
    name = input("Choose your name:")
    address = input("Server ip:")
    port = input("Server port:")

    connection = connect(name, address, port)

    while True:
        event = connection.waitEvent()

        if (event == EventType.READ):
            connection.readInput()
        elif (event == EventType.RECV):
            msg = connection.receive
            print(msg)
        elif (event == EventType.SEND):
            connection.send()
        else:
            print("Error: Bad Event Type: #TATOUKC")
        
    connection.close()

if __name__ == "__main__":
    main()
