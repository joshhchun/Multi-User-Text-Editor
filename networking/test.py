#!/usr/bin/env python3
import curses
import sys
import pickle
import sys


def main(stdscr):
    with open('hello.txt') as f:
        buffer = f.readlines()

    while True:
        stdscr.erase()
        for row, line in enumerate(buffer):
            stdscr.addstr(row, 0, line)
        
        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)