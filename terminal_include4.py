#!/usr/bin/env python3
from __future__ import annotations
import curses
import sys
from py3crdt.sequence import Sequence
import uuid
from dataclasses import dataclass, field
from random import uniform

DELETE = ("KEY_DELETE", "\x04", "\x7f")
                
# Class for the buffer holding the text
@dataclass
class CRDT():
    text: Sequence() = Sequence(uuid.uuid4())
    split_text: list[list] = field(default_factory=list)
    pos: int = 0
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
        with open("hm.txt", "w") as f:
            f.write("Positions : " + str(self.positions) + "\n")
            f.write("Index: " + str(index) + "\n")
            f.write("Length: " + str(self.length))

        if index < self.length:
            if index == 0:
                # If user wants to add character to beginning of text, give it an ID of prev first char / 2
                index = self.positions[0] / 2.00
            else:
                # If user wants to add a character in between 2 chars, give it an ID in between the 2 chars
                index = (self.positions[index - 1] + self.positions[index]) / 2
            self.text.add(letter, index)
        # If user wants to append to file
        else:
            # Assign first character in the text 0.5. If an ID of 0.5 has already been taken, then increment the ID by a little bit
            if index == 0:
                index = 0.5 + 0.0005 if index in self.removed_list else 0.5
                #index = 0.5
            else:
                index = index + 0.0005 if index in self.removed_list else index
                #index = index
            self.text.add(letter, index)
        self.split_text = self.text.get_seq().splitlines()
            
    # Method to remove a character by index
    def remove(self, index):
        if index <= self.length and index - 1 >= 0:
            id = self.text.id_seq[index - 1]
            self.text.remove(id)
        else:
            pass
        self.split_text = self.text.get_seq().splitlines()

    def save_file(self, file_name):
        with open(file_name, 'w') as f:
            f.write(self.text.get_seq())

        
# Class for the cursor
class Cursor:
    def __init__(self, row=3, col=0):
        self.row = row
        self.col = col
    # To move cursor up
    def up(self, buffer):
        if self.row - 3 > 0:
            self.row -= 1
            self._move_down(buffer)

    def new_line(self, buffer):
        self.row += 1
        self.col = 0
    # To move cursor down
    def down(self, buffer):
        if self.row - 3 < len(buffer) - 1:
            self.row += 1
            self._move_down(buffer)
    # To move cursor left
    def left(self):
        if self.col > 0:
            self.col -= 1
        
    # To move cursor right
    def right(self, buffer):
        if self.col < len(buffer[self.row - 3]):
            self.col += 1
    # To control going down movement is correct
    def _move_down(self, buffer):
        self.col = min(self.col, len(buffer[self.row - 3]))
    
    def moveCursorToSpot(self, row, col):
        self.row = row
        self.col = col

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
        return_col = cursor.col - self.col
        if cursor.col < self.col:
            return_col = cursor.col - 5
            if return_col < 0:
                return_col = 0
                self.col = 0
            else:
                self.col = return_col
        return cursor.row - self.row, return_col
            
# Function to move right when typing
def right(window, buffer, cursor):
    cursor.right(buffer)
    window.scrollDown(buffer, cursor)
    window.scrollRight(buffer, cursor)    

# Function to display the screen and control movements
def renderEditor(buffer, screen, window, cursor, file_name, users) -> None:
    # Get dimensions of the screen
    max_rows, max_cols = screen.getmaxyx()
    screen.erase()
    curses.init_pair(1, curses.COLOR_CYAN, 0)
    curses.init_pair(2, curses.COLOR_MAGENTA, 0)
    screen.addstr(0, 0, "Number of users: " + str(users), curses.color_pair(2) | curses.A_BOLD | curses.A_UNDERLINE)
    screen.addstr(0, max_cols // 2 - (len(file_name)//2), file_name, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE)
    for row_i, line in enumerate(buffer.split_text, start = 3):
        screen.addstr(row_i, 0, line)
    screen.move(cursor.row, cursor.col)
    screen.refresh()
        
   
# Input the self-made change.                                                                           
def handleKey(screen, buffer, window, cursor, key, file_name) -> bool:
    max_row, max_col = screen.getmaxyx()
    if key == "KEY_UP":
        if cursor.row -3 > 0:
            buffer.pos -= len(buffer.split_text[cursor.row - 3][:cursor.col]) + len(buffer.split_text[cursor.row-1 - 3][cursor.col:]) + 1
        cursor.up(buffer.split_text)
        window.scrollUp(cursor)
        return False
    elif key == "KEY_DOWN":
        if cursor.row - 3 < len(buffer.split_text) - 1:
            buffer.pos += len(buffer.split_text[cursor.row - 3][cursor.col:]) + len(buffer.split_text[cursor.row+1 - 3][:cursor.col]) + 1
        cursor.down(buffer.split_text)
        window.scrollDown(buffer, cursor)
        return False
    elif key == "KEY_LEFT":
        cursor.left()
        window.scrollLeft(buffer.split_text, cursor)
        if cursor.col > 0:
            buffer.pos -= 1
        return False
    elif key == "KEY_RIGHT":
        if cursor.col < len(buffer.split_text[cursor.row - 3]):
            buffer.pos += 1
        cursor.right(buffer.split_text)
        window.scrollRight(buffer.split_text, cursor)
        return False
    elif key == "\n":
        buffer.insert(key, buffer.pos)
        # Cursor down
        cursor.new_line(buffer.split_text)
        x = buffer.pos
        buffer.pos += 1
        return x
    elif key in DELETE:
        cursor.left()
        buffer.remove(buffer.pos)
        window.scrollLeft(buffer.split_text, cursor)
        x = buffer.pos
        if cursor.col > 0:
            buffer.pos -= 1
        return x
    elif len(key) == 1:
        buffer.insert(key, buffer.pos)
        cursor.right(buffer.split_text)
        x = buffer.pos
        buffer.pos += 1
        return x
    elif key == "KEY_SLEFT":
        buffer.save_file(file_name)
        return False
    elif key == 27:
        sys.exit()



    
