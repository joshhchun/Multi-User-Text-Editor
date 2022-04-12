#!/usr/bin/env python3
from argparse import ArgumentParser
from select import select
import socket
import json
import sys
import pickle

# Globals
nextClientId = 2
lamportClock = 0.0

def openfile(args) -> list[list]:
    try:
         buffer = [*open(args.fpath).readlines()]
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    return buffer

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
            
def loadFile(clientSocket, textData) -> None:
    data_bytes = pickle.dumps(textData)
    try:
        clientSocket.sendall(data_bytes)
    except InterruptedError as e:
        print(str(e))
    
    
    
def newConnectionHook(clientSocket, address, textData) -> None:
    # Note: You need a unique identifier for each client. Each character in the buffer / file
    # is a pair: the character itself, and the user who added it.
    # Generate a unique identifier for this client; we will tell them that this is their ID.
    clientId = getNextClientId()
    loadFile(clientSocket, textData)

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
                newConnectionHook(clientSocket, address, buffer)
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
