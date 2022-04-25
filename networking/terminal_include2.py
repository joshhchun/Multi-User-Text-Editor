#!/usr/bin/env python3
import curses

# Class for the buffer that will hold the text
class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]
    
    @property
    def bottom(self):
        return len(self) - 1
    # Method for inserting a character into the string
    def insert(self, cursor, string):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        new = current[:col] + string + current[col:]
        self.lines.insert(row, new)
    # Method for inserting a new line
    def newLine(self, cursor):
        current = self.lines.pop(cursor.row)
        self.lines.insert(cursor.row, current[:cursor.col])
        self.lines.insert(cursor.row + 1, current[cursor.col:])
        # Need a space here in case users insert multiple newlines
        self.insert(cursor, " ")
        cursor.moveCursorToSpot(cursor.row + 1, 0)

    def delete(self, cursor):
        row, col = cursor.row, cursor.col
        if (row, col) < (self.bottom, len(self[row])):
            current = self.lines.pop(row)
            if col < len(self[row]):
                new = current[:col] + current[col + 1:]
                self.lines.insert(row, new)
            else:
                next = self.lines.pop(row)
                new = current + next
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
        if self.col < len(buffer[self.row]) - 1:
            self.col += 1
    # To control going down movement is correct
    def _move_down(self, buffer):
        self.col = min(self.col, len(buffer[self.row]) - 1)
    
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

def left(window, buffer, cursor):
    cursor.left()
    window.scrollUp(cursor)
    window.scrollLeft(buffer, cursor)

# Function to display the screen and control movements
def renderEditor(buffer, screen, window, cursor) -> None:
    screen.erase()
    for row, line in enumerate(buffer[window.row:window.n_rows + window.row]):
        screen.addstr(row, 0, line[window.col:window.n_cols + window.col])
    try:
        screen.move(*window.moveCursor(cursor))
    except Exception:
        row, col = window.moveCursor(cursor)
        screen.addstr("Window" + str(window.row) + ":" + str(window.col))
        screen.addstr("Cursor" + str(cursor.row) + ":" + str(cursor.col))
        screen.addstr(str(row) +  ":" + str(col))
    screen.refresh()
    
# Input the self-made change.                                                                           
def handleKey(screen, buffer, window, cursor, key) -> bool:
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
    elif key in ("KEY_DELETE", "\x04", "\x7f"):
        if (cursor.row, cursor.col) > (0, 0):
            left(window, buffer, cursor)
            buffer.delete(cursor)
    elif key == "KEY_MOUSE":
        _, col, row, _, bstate  = curses.getmouse()
        # Left click
        if bstate & curses.BUTTON1_PRESSED:
            cursor.moveCursorToSpot(row, col)
        # Scroll up
        elif bstate & curses.BUTTON4_PRESSED:
            cursor.up(buffer)
            window.scrollUp(cursor)
        # Scroll down   
        elif bstate & curses.BUTTON2_PRESSED or bstate == 0x8000000:
            cursor.down(buffer)
            window.scrollDown(buffer, cursor)
        
        
    # Get rid of weird inputs
    elif len(key) == 1:
        buffer.insert(cursor, key)
        right(window, buffer, cursor)
        return True