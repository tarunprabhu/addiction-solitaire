#!/usr/bin/env python3

# Addiction Solitaire
#
# Copyright (C) 2019, Tarun Prabhu <tarun.prabhu@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum, IntEnum, auto, unique

@unique
class Face(IntEnum):
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13

    # None => str
    @property
    def filename(self):
        names = { Face.Ace: 'Ace',
                  Face.Jack: 'Jack',
                  Face.Queen: 'Queen',
                  Face.King: 'King' }
        if self in names:
            return '{}.svg'.format(names[self])
        else:
            return '{}.svg'.format(int(self))


@unique
class Suit(IntEnum):
    Clubs = auto()
    Diamonds = auto()
    Hearts = auto()
    Spades = auto()

    # None => str
    @property
    def dirname(self):
        return { Suit.Clubs: 'Clubs',
                 Suit.Diamonds: 'Diamonds',
                 Suit.Hearts: 'Hearts',
                 Suit.Spades: 'Spades' }[self]


@unique
class Direction(Enum):
    Up = auto()
    Down = auto()
    Left = auto()
    Right = auto()

    # None => str
    def __str__(self):
        return { self.Up: 'Up',
                 self.Down: 'Down',
                 self.Left: 'Left',
                 self.Right: 'Right' }[self]

    # None => str
    def __repr__(self):
        return str(self)


class Card:
    # Suit, Face
    def __init__(self, suit, face):
        self.suit = suit
        self.face = face

    # Card => bool
    def is_predecessor(self, other):
        if other.face == Face.Ace:
            return False
        return (self.suit == other.suit) and (self.face == other.face - 1)

    # Card => bool
    def is_successor(self, other):
        if other.face == Face.King:
            return False
        return (self.suit == other.suit) and (self.face == other.face + 1)

    # None => Card
    @property
    def successor(self):
        if self.face < Face.King:
            return Card(self.suit, Face(self.face + 1))
        return None

    # None => Card
    @property
    def predecessor(self):
        if self.face > Face.Ace:
            return Card(self.suit, Face(self.face - 1))
        return None
    
    # None => *
    def __hash__(self):
        return hash((self.suit, self.face))

    # None => bool
    def __eq__(self, other):
        return (self.suit == other.suit) and (self.face == other.face)

    # None => bool
    def __le__(self, other):
        if self.suit == other.suit:
            return self.face <= other.face
        else:
            return self.suit <= other.suit

    # None => bool
    def __lt__(self, other):
        if self.suit == other.suit:
            return self.face < other.face
        else:
            return self.suit < other.suit
    
    # None => str
    def __str__(self):
        suits = { Suit.Clubs: 'C',
                  Suit.Diamonds: 'D',
                  Suit.Hearts: 'H',
                  Suit.Spades: 'S' }
        faces = { Face.Ace: 'A',
                  Face.Jack: 'J',
                  Face.Queen: 'Q',
                  Face.King: 'K' }
        if self.face in faces:
            return '{:>2}{}'.format(faces[self.face], suits[self.suit])
        else:
            return '{:>2}{}'.format(int(self.face), suits[self.suit])

    # None => str
    def __repr__(self):
        return str(self)

    
class Point:
    # int, int
    def __init__(self, row, col):
        self.row = row
        self.col = col

    # None => Point
    @property
    def left(self):
        if self.col > 0:
            return Point(self.row, self.col - 1)
        return None

    # None => Point
    @property
    def right(self):
        if self.col < 12:
            return Point(self.row, self.col + 1)
        return None

    # None => Point
    @property
    def above(self):
        if self.row > 0:
            return Point(self.row - 1, self.col)
        return None

    # None => Point
    @property
    def below(self):
        if self.row < 3:
            return Point(self.row + 1, self.col)
        return None

    # None => *
    def __hash__(self):
        return hash((self.row, self.col))

    # None => bool
    def __eq__(self, other):
        return (self.row == other.row) and (self.col == other.col)

    # None => bool
    def __le__(self, other):
        if self.row == other.row:
            return self.col <= other.col
        else:
            return self.row <= other.row
    
    # None => bool
    def __lt__(self, other):
        if self.row == other.row:
            return self.col < other.col
        else:
            return self.row < other.row
    
    # None => str
    def __str__(self):
        return '({}, {})'.format(self.row, self.col)

    # None => str
    def __repr__(self):
        return str(self)
