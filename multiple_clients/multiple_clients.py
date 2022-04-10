#!/usr/bin/env python3

import sys
import socket

def main():
    host = "127.0.0.1"
    port = 8000

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
        
    while True:                                                         
        try:
            userInput = input("Enter something: ")          
        except EOFError:
            break
        clientSocket.sendall(str.encode(userInput)) 
        response = clientSocket.recv(1024)
        print(f"Recieved: {response.decode('utf-8')}!")
    
    clientSocket.close()

if __name__ == "__main__":
    main()

        
