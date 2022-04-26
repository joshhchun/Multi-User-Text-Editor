#!/usr/bin/env python3
from __future__ import annotations
import curses
from py3crdt.sequence import Sequence
import uuid
from dataclasses import dataclass
from random import uniform

# Class for the buffer that will hold the text
class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]
    
    # Method for inserting a new line
    def newLine(self, cursor):
        current = self.lines.pop(cursor.row)
        self.lines.insert(cursor.row, current[:cursor.col])
        self.lines.insert(cursor.row + 1, current[cursor.col:])
        # Need a space here in case users insert multiple newlines
        self.insert(cursor, " ")

def save_file(file_name, buffer):
    with open(file_name, 'w') as f:
        for line in buffer.text.get_seq():
            f.write(line)
    def wfile(self, fname):
        with open(fname, 'w') as f:
            for line in self.lines:
                f.write(line)
                
# Class for the buffer holding the text
@dataclass
class CRDT():
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
        if self.col < len(buffer[self.row]) - 1:
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
            
    # Scroll window to the right if the user tries to move out of the view and not end of line
    # TODO: Fix this and window scroll right
    def scrollRight(self, buffer, cursor):
        if cursor.col == (self.col + self.n_cols) and (self.col + self.n_cols) < len(buffer[cursor.row]) - 1:
            self.col += 1
    
    def scrollLeft(self, buffer, cursor):
        if cursor.col == self.col - 1 and self.col > 0:
            self.col -= 1
            
    def moveCursor(self, cursor):
        return cursor.row - self.row, cursor.col - self.col
            
# Function to move right when typing
def right(window, buffer, cursor):
    cursor.right(buffer)
    window.scrollDown(buffer, cursor)
    window.scrollRight(buffer, cursor)    

# Function to display the screen and control movements
def renderEditor(buffer, screen, window, cursor) -> None:
    # Get dimensions of the screen
    max_rows, max_cols = screen.getmaxyx()
    string = buffer.text.get_seq()
    screen.erase()
    screen.addstr(3, 0, string)

    
    """for row, line in enumerate(buffer[window.row:window.n_rows + window.row]):
        screen.addstr(row, 0, line[window.col:window.n_cols + window.col])
    screen.move(*window.moveCursor(cursor))"""
    screen.refresh()
   
 
# Input the self-made change.                                                                           
def handleKey(screen, buffer, window, cursor, key, file_name) -> bool:
    if key == "KEY_UP":
        cursor.up(buffer)
        window.scrollUp(cursor)
        return False
    elif key == "KEY_DOWN":
        cursor.down(buffer)
        window.scrollDown(buffer, cursor)
        return False
    elif key == "KEY_LEFT":
        cursor.left()
        window.scrollLeft(buffer, cursor)
        return False
    elif key == "KEY_RIGHT":
        cursor.right(buffer)
        window.scrollRight(buffer, cursor)
        return False
    elif key == "\n":
        buffer.newLine(cursor)
        right(window, buffer, cursor)
        return True
    # Get rid of weird inputs
    elif len(key) == 1:
        buffer.insert(key, cursor.col)
        return True
    elif key == "KEY_SLEFT":
        buffer.wfile(file_name)
        return True
	
