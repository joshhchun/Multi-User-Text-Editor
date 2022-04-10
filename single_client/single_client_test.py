#!/usr/bin/env python3

import sys
import socket

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
        
    userInput = input("Enter something: ")
    clientSocket.sendall(str.encode(userInput)) # Have to send byte-object
    response = clientSocket.recv(1024)
    clientSocket.close()
        
    print(f"Recieved {response.decode('utf-8')}!")

        
