#!/usr/bin/env python3
from __future__ import annotations
from argparse import ArgumentParser
from select import select
import socket
import json
import sys
import pickle
from py3crdt.sequence import Sequence
import uuid
from dataclasses import dataclass
from random import uniform

# Globals
nextClientId = 2
lamportClock = 0.0
PREFIX_LENGTH = 8

# Class for the buffer holding the text
@dataclass
class Buffer():
    text: Sequence() = Sequence(uuid.uuid4())
    
    @property
    def length(self):
        return len(self.text.id_seq)
    
    @property
    def positions(self):
        return self.text.id_seq

    @property
    def removed_list(self):
        return self.text.id_remv_list
    
    # Method to insert a character at an index
    def insert(self, letter, index):
        # If user wants to edit the existing text (vs appending)
        if index < self.length:
            if index == 0:
                # If user wants to add character to beginning of text, give it an ID of prev first char / 2
                index = self.positions[0] / 2
            else:
                # If user wants to add a character in between 2 chars, give it an ID in between the 2 chars
                index = (self.positions[index - 1] + self.positions[index]) / 2
            self.text.add(letter, index)
        # If user wants to append to file
        else:
            # Assign first character in the text 0.5. If an ID of 0.5 has already been taken, then increment the ID by a little bit
            if index == 0:
                index = 0.5 + uniform(0.05, 0.1) if index in self.removed_list else 0.5
            else:
                index = index + uniform(0.05, 0.3) if index in self.removed_list else index
            self.text.add(letter, index)
            
    # Method to remove a character by index
    def remove(self, index):
        if index <= self.length and index - 1 >= 0:
            id = self.text.id_seq[index - 1]
            self.text.remove(id)
        else:
            pass

# Function to open the file
def openfile(args) -> Buffer():
    index = 0.5
    try:
        buffer = Buffer()
        for line in open(args.fpath).readlines():
            for letter in line:
                buffer.insert(letter, index)
                index += 1
        return buffer
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)

def parser() -> ArgumentParser:
    result = ArgumentParser()
    result.add_argument("fpath")
    result.add_argument("-p", "--port", type=int, default=8080)
    return result


def createServerSocket(port) -> socket.socket:
    socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    socketObject.bind(("localhost", port))
    socketObject.listen(20)
    return socketObject

def incrementLamportClock() -> None:
    global lamportClock
    lamportClock += 1

def getNextClientId() -> int:
    global nextClientId
    nextClientId += 1
    return nextClientId

def broadcastBytes(data) -> None:
    """
    :param data:    Data to send to each client (except server).
    :type data:     bytes
    """
    for fileno, socketObject in networkMap.items():
        if fileno != serverSocket.fileno():
            socketObject.send(data)
        
# Function to send the existing file contents in Sequence to client
def sendFileToClient(clientSocket, textData, fileName) -> None:
    merge_list = pickle.dumps({"file_name": fileName, "elem_list": textData.elem_list, "id_remv_list": textData.id_remv_list})
    prefix = f"{len(merge_list)}".zfill(PREFIX_LENGTH).encode("utf-8")
    if len(prefix) > PREFIX_LENGTH:
        raise ValueError("prefix too long")
    clientSocket.sendall(prefix + merge_list)
    
    
    
def newConnectionHook(clientSocket, address, textData, fileName) -> None:
    sendFileToClient(clientSocket, textData, fileName)

def connectionLostHook(clientSocket, address) -> None:
    # TODO: Maybe broadcast to clients that this client disconnected?
    ...
    
def handleData(clientSocket, address, data) -> None:
    jsonObject = json.loads(data.read().decode("utf-8"))

    """
        jsonObject might look like {
            type: "add",
            position: [
                [index 0, "josh"], # Identifier 1
            ],
            lamport: 0,
            value: "b"
        }
    """

    # 1. Decode JSON-object from bytes.
    # 2. Set 
           

def main() -> None:
    args = parser().parse_args()
    buffer = openfile(args)
    lamportClock = 0
    nextClientId = 0
    serverSocket = createServerSocket(args.port)
    networkMap = {
        serverSocket.fileno(): serverSocket,
    }
    while True:
        for file in select([*networkMap.keys()], [], [])[0]:
            # If we have activity on serverSocket, someone is trying to connect.
            if file == serverSocket.fileno():
                clientSocket, address = serverSocket.accept()
                newConnectionHook(clientSocket, address, buffer.text, args.fpath)
                networkMap[clientSocket.fileno()] = (clientSocket, address)
            # If we have activity on any other socket, someone is sending us information.
            else:
                clientSocket, address = networkMap[file]
                data = clientSocket.recv(1024)
                if not data:
                    # This socket sent nothing, which means it disconnected!
                    connectionLostHook(clientSocket, address)
                    networkMap.pop(file)
                else:
                    handleData(clientSocket, address, data)


if __name__ == "__main__":
    main()
