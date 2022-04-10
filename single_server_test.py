#!/usr/bin/env python3

import sys
import socket

if __name__ == "__main__":
    host = '127.0.0.1'              # Make default host localhost
    port = 8000                     # Random port (non privileged ports are > 1023)
    
    serverSocket = socket.socket(socket.AF_INET,          # returns IPv4 address
                       socket.SOCK_STREAM)                # to use TCP
    serverSocket.bind((host, port))                       # bind the socket to the host/port
    serverSocket.listen()                                 # enables server to accept connections
    client, addr = serverSocket.accept()                  # creates the actual socket to communicate
    with client:
        print(f"Connected to {addr}")                     # Prints what host and port the client is on
        while True:                                       # loop to print echo whatever the client says
            response = client.recv(1024)
            if not response:
                break
            client.sendall(response)                      # Keeps sending data until all has been sent
    
    serverSocket.close()
        
        
        
        
        
        
        
    