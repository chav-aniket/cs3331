#!/usr/bin/env python3
from socket import *
import sys

if len(sys.argv) != 2:
    print("Enter port.")
    sys.exit(1)

serverPort = int(sys.argv[1])

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(("localhost", serverPort))

serverSocket.listen(1)

print("The server is ready to receive")

while 1:
    connectionSocket, addr = serverSocket.accept()

    sentence = connectionSocket.recv(1024)

    print(sentence)
    fopen = (sentence.split()[1][1:])

    try:
        f = open(fopen)
        page = f.read()
        connectionSocket.send("HTTP/1.1 200 OK \n\n")
        connectionSocket.send(page)
        f.close()

    except IOError:
        f = open('error404.html')
        page = f.read()
        connectionSocket.send("HTTP/1.1 404 File Not Found \n\n")
        connectionSocket.send(page)
        f.close()

    connectionSocket.close()