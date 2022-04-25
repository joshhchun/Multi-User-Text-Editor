#!/usr/bin/env python3
from select import select
from argparse import ArgumentParser
import socket
import curses
import sys
import pickle
from terminal_include import *

PREFIX_LENGTH = 8

# Parser for the command line arguments
def parser() -> ArgumentParser:
    result = ArgumentParser()
    result.add_argument("-p", "--port", type=int, default=8000)
    return result

# TODO: Function to send the CRDT to the server
def sendOverNetwork(key) -> None:
    ...

# TODO: Make the CRDT to send to the server
def makeCrdt(key) -> object:
    ...

# TODO: Server sending client a CRDT
def receiveCrdtFromFile(file) -> object:
    ...

# Function to create the client socket that connects to the server
def createClientSocket(port) -> socket.socket:
    # Create client socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Try to connect to the server 
    try:
        clientSocket.connect(('localhost', port))
    except socket.error as e:
        print(str(e))
        sys.exit(1)
    
    return clientSocket


# TODO: Handle recieving a CRDT and implementing it into the text data structure
def commitCrdtToEditor(crdt) -> None:
    ...

 # Reading data from the socket
def readAllFromSocket(serverSocket, length) -> bytearray:
    buffer = bytearray()
    while len(buffer) < length:
        buffer += serverSocket.recv(length - len(buffer))
    return buffer

# Loading the file in from the server
def loadInFile(serverSocket):
    # Getting the prefix length to ensure we recieve what we want 
    prefix = int(readAllFromSocket(serverSocket, PREFIX_LENGTH))
    # Reading prefix # of bytes from the socket
    body = pickle.loads(readAllFromSocket(serverSocket, prefix))
    buffer = CRDT()
    # Merge existing sequence into new client-side one
    file_name = body['file_name']
    buffer.text.merge(body['elem_list'], 'elem')
    buffer.text.merge(body['id_remv_list'], 'id_remv_list')
    return (file_name, buffer)

    

def main(screen):
    # Parsing the command line arguments (for port)
    args = parser().parse_args()    
    # Creating the client socket that is connected to the server
    clientSocket = createClientSocket(args.port)
    # Loading in the current text file
    file_name, buffer = loadInFile(clientSocket)
    # Creating a window & cursor object for the terminal
    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()
    while True:
        # Output the data structure holding the text onto the screen
        renderEditor(buffer, screen, window, cursor)  
        # All the sockets the client is connected to (just be one thing for now - the server file desc)
        networkFiles = [clientSocket.fileno()] 
        # Select returns list of files ready to read, write, and (errors? doesnt matter to us)
        rlist, wlist, xlist = select([0] + networkFiles, [], [])
        """ Essentially, wait until there is activity on networkFiles, OR activity on 
        descriptor 0 (stdin) ready to read """
        for file in rlist:
            if file == 0: # stdin
                # This means I am typing. I need to send someone.
                key = screen.getkey()
                handleKey(screen, buffer, window , cursor, key, file_name)
                #sendOverNetwork(makeCrdt(key))
            else:
                # This means I got something from someone else.
                crdt = receiveCrdtFromFile(file)
                commitCrdtToEditor(crdt)



if __name__ == "__main__":
    curses.wrapper(main)
