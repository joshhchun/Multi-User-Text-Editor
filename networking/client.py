#!/usr/bin/env python3
from select import select
from argparse import ArgumentParser
import socket
import curses
import sys
import pickle
from terminal_include import *

PREFIX_LENGTH = 8
DELETE = ("KEY_DELETE", "\x04", "\x7f")

# Parser for the command line arguments
def parser() -> ArgumentParser:
    result = ArgumentParser()
    result.add_argument("-p", "--port", type=int, default=8000)
    return result

# Function to send the change to the server
def sendOverNetwork(server_socket, CRDT) -> None:
    server_socket.sendall(pickle.dumps(CRDT))

# Function to make the CRDT based on the user change
def makeCrdt(key: str, index: int) -> tuple:
    global DELETE
    if key in DELETE:
        return ('delete', 0, index)
    else:
        return ('insert', key, index)

# Function to create the client socket that connects to the server
def create_client_socket(port) -> socket.socket:
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Try to connect to the server 
    try:
        client_socket.connect(('localhost', port))
    except socket.error as e:
        print(str(e))
        sys.exit(1)
    
    return client_socket

# TODO: Handle recieving a CRDT and implementing it into the text data structure
def commitCrdtToEditor(file, buffer) -> None:
    op, char, index = pickle.loads(file.recv(1024))
    if op == 'insert':
        buffer.insert(char, index)
    else:
        buffer.remove(index)

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
    client_socket = create_client_socket(args.port)
    # Loading in the current text file
    file_name, buffer = loadInFile(client_socket)
    # Creating a window & cursor object for the terminal
    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()
    while True:
        # Output the data structure holding the text onto the screen
        renderEditor(buffer, screen, window, cursor)  
        # All the sockets the client is connected to (just be one thing for now - the server file desc)
        networkFiles = [client_socket.fileno()] 
        # Select returns list of files ready to read, write, and (errors? doesnt matter to us)
        rlist, wlist, xlist = select([0] + networkFiles, [], [])
        """ Essentially, wait until there is activity on networkFiles, OR activity on 
        descriptor 0 (stdin) ready to read """
        for file in rlist:
            if file == 0: # stdin
                # This means I am typing. I need to send someone.
                key = screen.getkey()
                # If user wants to insert
                if handleKey(screen, buffer, window , cursor, key, file_name):
                    sendOverNetwork(client_socket, makeCrdt(key))
            else:
                # This means I got something from someone else.
                commitCrdtToEditor(file, buffer)



if __name__ == "__main__":
    curses.wrapper(main)
