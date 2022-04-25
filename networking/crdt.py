from __future__ import annotations
from py3crdt.sequence import Sequence
import uuid
from dataclasses import dataclass
from random import uniform

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
                index = index + uniform(0.05, 0.30) if index in self.removed_list else index
            self.text.add(letter, index)
            
    # Method to remove a character by index
    def remove(self, index):
        if index <= self.length and index - 1 >= 0:
            id = self.text.id_seq[index - 1]
            self.text.remove(id)
        else:
            pass


buf = CRDT()
buf.insert('a', 1)
buf.insert('b', 2)
print(buf.text.elem_list)
print(buf.text.get_seq())