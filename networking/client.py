#!/usr/bin/env python3
from select import select
from argparse import ArgumentParser
import socket
import curses
import sys
import pickle

# Class for the buffer that will hold the text
class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]
    # Method for inserting a character into the string
    def insert(self, cursor, string):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        new = current[:col] + string + current[col:]
        self.lines.insert(row, new)

# Class for the cursor
class Cursor:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
    # To move cursor up
    def up(self, buffer):
        if self.row > 0:
            self.row -= 1
            self._move_down(buffer)
    # To move cursor down
    def down(self, buffer):
        if self.row < len(buffer) - 1:
            self.row += 1
            self._move_down(buffer)
    # To move cursor left
    def left(self):
        if self.col > 0:
            self.col -= 1
    # To move cursor right
    def right(self, buffer):
        if self.col < len(buffer[self.row]):
            self.col += 1
    # To control going down movement is correct
    def _move_down(self, buffer):
        self.col = min(self.col, len(buffer[self.row]) - 1)

# Class for the curses terminal window
class Window:
    def __init__(self, n_rows, n_cols, row=0, col=0):
        # Number of rows and columns in the window
        self.n_rows = n_rows
        self.n_cols = n_cols
        # What row and col the window is currently on (top left)
        self.row = row
        self.col = col
         
    def bottom(self):
        return self.row + self.n_rows - 1
    # Scroll the window up if the user moves upwards out of view and before start of file
    def scrollUp(self, cursor):
        if cursor.row == self.row - 1 and self.row > 0:
            self.row -= 1
    # Scroll the window down if the user moves beneath the view and not at end of file
    def scrollDown(self, buffer, cursor):
        if cursor.row == self.bottom() + 1 and self.bottom() < len(buffer) - 1:
            self.row += 1
            
    def moveCursor(self, cursor):
        return cursor.row - self.row, cursor.col - self.col
    
    def horizontal_scroll(self, cursor, left_margin=5, right_margin=2):
        n_pages = cursor.col // (self.n_cols - right_margin)
        self.col = max(n_pages * self.n_cols - right_margin - left_margin, 0)

# Function to move right when typing
def right(window, buffer, cursor):
    cursor.right(buffer)
    window.scrollDown(buffer, cursor)
    window.horizontal_scroll(cursor)
    
# Parser for the command line arguments
def parser() -> ArgumentParser:
    result = ArgumentParser()
    result.add_argument("-p", "--port", type=int, default=8000)
    return result

# Function to display the screen and control movements
def renderEditor(buffer, screen, window, cursor) -> None:
    screen.erase()
    for row, line in enumerate(buffer[:window.n_rows]):
        screen.addstr(row, 0, line[:window.n_cols])
    screen.move(*window.moveCursor(cursor))
    
# Input the self-made change.                                                                           
def handleKey(screen, buffer, window, cursor, key) -> bool:
    if key == "KEY_UP":
        cursor.up(buffer)
        window.scrollUp(cursor)
        window.horizontal_scroll(cursor)
        screen.refresh()
        return False
    elif key == "KEY_DOWN":
        cursor.down(buffer)
        window.scrollDown(buffer, cursor)
        window.horizontal_scroll(cursor)
        screen.refresh()
        return False
    elif key == "KEY_LEFT":
        cursor.left()
        window.horizontal_scroll(cursor)
        screen.refresh()
        return False
    elif key == "KEY_RIGHT":
        cursor.right(buffer)
        window.horizontal_scroll(cursor)
        screen.refresh()
        return False
    else:
        buffer.insert(cursor, key)
        right(window, buffer, cursor)
        screen.refresh()
        return True


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

# Function to load in the initial file
def loadInFile(clientSocket) -> list[list]:
    dataStream = clientSocket.recv(4096)
    textData = pickle.loads(dataStream)
    return textData
    

def main(screen):
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    # Parsing the command line arguments (for port)
    args = parser().parse_args()    
    # Creating the client socket that is connected to the server
    clientSocket = createClientSocket(args.port)
    # Loading in the current text file
    buffer = Buffer(loadInFile(clientSocket))
    # Creating a window object for the terminal
    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()
    while True:
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
                handleKey(screen, buffer, window , cursor, key)
                #sendOverNetwork(makeCrdt(key))
            else:
                # This means I got something from someone else.
                crdt = receiveCrdtFromFile(file)
                commitCrdtToEditor(crdt)



if __name__ == "__main__":
    curses.wrapper(main)
