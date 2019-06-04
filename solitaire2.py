#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from gi.repository.GdkPixbuf import Pixbuf as GdkPixbuf

from abc import ABC, abstractmethod
from enum import Enum, IntEnum, unique, auto
from collections import namedtuple, deque

import os
import random

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
        return '{}.png'.format(int(self))

    # None => str
    def __str__(self):
        return str(int(self))
    
@unique
class Suit(Enum):
    Clubs = 'c'
    Diamonds = 'd'
    Hearts = 'h'
    Spades = 's'

    # None => str
    @property
    def dirname(self):
        return { self.Clubs: 'c',
                 self.Diamonds: 'd',
                 self.Hearts: 'h',
                 self.Spades: 's' }[self]

    # None => str
    def __str__(self):
        return { self.Clubs: 'C',
                 self.Diamonds: 'D',
                 self.Hearts: 'H',
                 self.Spades: 'S' }[self]
    
@unique
class Direction(Enum):
    Up = auto()
    Down = auto()
    Left = auto()
    Right = auto()

class Card:
    def __init__(self, suit, face):
        self._suit = suit
        self._face = face

    # None => Suit
    @property
    def suit(self):
        return self._suit

    # None => Face
    @property
    def face(self):
        return self._face

    # None => str
    def __str__(self):
        return '{}{}'.format(str(self.suit), str(self.face))

    # None => str
    def __repr__(self):
        return str(self)
    
class Cell:
    # None
    def __init__(self):
        self.card = None
        self.movable = False

    # None => str
    def __str__(self):
        if self.movable:
            return '[{}]'.format(self.card)
        else:
            return '{}'.format(self.card)

    # None => str
    def __repr__(self):
        return str(self)
    
        
class View(Gtk.Window):
    # Appearance options
    css_selected = ('frame {'
                    '  border-width: 4px;'
                    '  border-style: solid;'
                    '  border-color: green;'
                    '}').encode('utf-8')
    css_movable = ('frame {'
                   '  border-width: 4px;'
                   '  border-style: solid;'
                   '  border-color: yellow;'
                   '}').encode('utf-8')
    css_normal = ('frame {'
                  '  border-width: 4px;'
                  '  border-style: solid;'
                  '  border-color: rgba(0, 0, 0, 0);'
                  '}').encode('utf-8')

    # Game => None
    def __init__(self, game):
        Gtk.Window.__init__(self, title='Addiction Solitaire')

        row_spacing = 0
        col_spacing = 0
        border = 0
        card_width = 60
        card_height = 90

        self.game = game
        self.cards = dict()
        for i, s in enumerate(Suit):
            self.cards[s] = dict()
            for c in Face:
                filename = os.path.join('cards',
                                        'png',
                                        s.dirname,
                                        c.filename)
                self.cards[s][c] = \
                    Gtk.Image.new_from_pixbuf(
                        GdkPixbuf.new_from_file_at_scale(filename,
                                                         card_width,
                                                         card_height,
                                                         False))

        self.frames = []
        for _ in range(0, 4):
            self.frames.append([None] * 13)
            
        grid = Gtk.Grid.new()
        grid.set_row_spacing(row_spacing)
        grid.set_column_spacing(col_spacing)
        grid.set_border_width(border)
        for i, s in enumerate(Suit):
            for j in Face:
                frame = Gtk.Frame.new()
                frame.set_size_request(card_width, card_height)
                frame.set_shadow_type(Gtk.ShadowType.NONE)

                evt = Gtk.EventBox.new()
                evt.add(frame)
                evt.connect('button-press-event',
                            self.controller.cb_buttonpress,
                            (int(i), int(j)))

                grid.attach(evt, j - 1, i, 1, 1)
                self.frames[i][j-1] = frame

        self.add(grid)

        self.connect('destroy', Gtk.main_quit)
        self.connect('key-press-event', self.controller.cb_keypress)
        self.show_all()

    # None => None
    def refresh(self):
        print(self.model.board)
        for i in range(0, 4):
            for j in range(0, 13):
                child = self.frames[i][j].get_child()
                if child:
                    self.frames[i][j].remove(child)
                self.set_css_normal(i, j)
                if not self.model.is_empty(i, j):
                    card = self.model.board[i][j].card
                    print(card, self.cards[card.suit][card.face])
                    self.frames[i][j].add(self.cards[card.suit][card.face])

        self.show_all()
        self.set_css_cursor(*self.model.cursor)
    
    # int, int => None
    def set_css_cursor(self, i, j):
        self.set_css(self.frames[i][j], View.css_selected)

    # int, int => None
    def set_css_normal(self, i, j):
        self.set_css(self.frames[i][j], View.css_normal)
        
    # Gtk.Widget, str => None
    def set_css(self, widget, css):
        provider = Gtk.CssProvider.new()
        provider.load_from_data(css)
        widget.get_style_context() \
              .add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    # None => Controller
    @property
    def controller(self):
        return self.game.controller

    # None => Model
    @property
    def model(self):
        return self.game.model

class KeyPress:
    # int, Gdk.ModifierType, *
    def __init__(self, key, state = 0):
        self.key = key
        self.state = state

    def __hash__(self):
        return hash((self.key, self.state))
        
    def __eq__(self, other):
        return (self.key == other.key) and (self.state & other.state)


class Command(ABC):
    # Game
    def __init__(self, game):
        self.model = game.model
        self.view = game.view
        
    # None => None
    @abstractmethod
    def execute(self):
        pass
    
# This initiates a "move". The point is the currently selected location.
# The cell will always contain a movable card.
# If the movable card is not a 2, it will have at most one destination.
# If the movable card is a 2, it may have more than one destination if there
# is more than one empty cell in the first column. If there is more than one
# empty cell in the first column, the card will be moved to the cell below the
# current row. If there is no empty destination below the current row, it will
# be moved to the first empty row above the current row
#
class MoveCommand(Command):
    # Game, Point
    def __init__(self, game, point):
        super().__init__(game)
        self._point = point

    # None => None
    def execute(self):
        self.model.move(self._point)
        self.view.refresh()
    
class SelectCommand(Command):
    # Game, Point
    def __init__(self, game, point):
        super().__init__(game)
        self._point = point

    # None => None
    def execute(self):
        self.model.select(self._point)
        self.view.refresh()
        
class ShuffleCommand(Command):
    # Game
    def __init__(self, game):
        super().__init__(game)
        self._snapshot = deepcopy(self.model.board)

    # None => None
    def execute(self):
        self.model.shuffle()
        self.view.refresh()
        
class NewGameCommand(Command):
    # Game
    def __init__(self, game):
        super().__init__(game)

    # None => None
    def execute(self):
        self.model.start()
        self.view.refresh()

class QuitGameCommand(Command):
    # Game
    def __init__(self, game):
        super().__init__(game)

    # None => None
    def execute(self):
        self.model.stop()
        
class Controller:
    def __init__(self, game):
        self.game = game
        
        self.directions = {
            KeyPress(Gdk.KEY_Up): Direction.Up,
            KeyPress(Gdk.KEY_KP_Up): Direction.Up,
            KeyPress(Gdk.KEY_Down): Direction.Down,
            KeyPress(Gdk.KEY_KP_Down): Direction.Down,
            KeyPress(Gdk.KEY_Left): Direction.Left,
            KeyPress(Gdk.KEY_KP_Left):  Direction.Left,
            KeyPress(Gdk.KEY_Right): Direction.Right,
            KeyPress(Gdk.KEY_KP_Right): Direction.Right}

        self.activators = set([
            KeyPress(Gdk.KEY_Return),
            KeyPress(Gdk.KEY_KP_Enter)])

        self.quitters = set([
            KeyPress(Gdk.KEY_q, Gdk.ModifierType.CONTROL_MASK)])

        self.undoers = set([
            KeyPress(Gdk.KEY_z, Gdk.ModifierType.CONTROL_MASK)])

        self.newers = set([
            KeyPress(Gdk.KEY_n, Gdk.ModifierType.CONTROL_MASK),
            KeyPress(Gdk.KEY_F2)])

        self.shufflers = set([
            KeyPress(Gdk.KEY_F5)])
        
        self.commands = deque()
        
    # Gtk.Widget, GdkEvent => bool
    def cb_keypress(self, widget, evt):
        keypress = KeyPress(evt.keyval, evt.state)
        cmd = None
        if keypress in self.directions:
            point = self.model.get_next_movable(self.directions[keypress])
            if point:
                cmd = SelectCommand(point)
        elif keypress in self.activators:
            cmd = MoveCommand(self.cursor)
            self.commands.append(cmd)
        # q or Esc quits
        elif keypress in self.quitters:
            cmd = QuitGameCommand(self.game)
            self.commands.clear()
        elif keypress in self.newers:
            cmd = NewGameCommand(self.game)
            self.commands.clear()
        elif keypress in self.undoers:
            if self.commands:
                cmd = self.commands.pop()
        elif keypress in self.shufflers:
            if self.model.can_shuffle():
                cmd = ShuffleCommand(self.game)
                self.commands.append(cmd)

        if cmd:
            cmd.execute()
                
        return False

    # Gtk.Widget, Gdk.Event, Point => bool
    def cb_buttonpress(self, widget, evt, point):
        cmd = None
        if not self.model.is_empty(point):
            if evt.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                if self.model.is_movable(point):
                    cmd = MoveCommand(point)
                    self.commands.append(cmd)
            elif evt.type == Gdk.EventType.BUTTON_PRESS:
                if self.model.is_movable(point):
                    cmd = SelectCommand(point)
                    self.commands.append(cmd)

        if cmd:
            self.model.execute(cmd)
            self.view.execute(cmd)

        return False
    
class Model:
    def __init__(self, game):
        self.game = game

        # The cards that will be used in the game. None is used to represent
        # the aces that are removed
        self.cards = set()
        for suit in Suit:
            for face in Face:
                self.cards.add(Card(suit, face))

        self.points = set()
        for i in range(0, 4):
            for j in range(0, 13):
                self.points.add((i, j))
                
        self.board = []
        for _ in Suit:
            row = []
            for _ in Face:
                row.append(Cell())
            self.board.append(row)
            
        self.cursor = None
        self.shuffles = self.preferences.shuffles
        
    # None => None
    def start(self):
        self.shuffles = self.preferences.shuffles
        self.shuffle(False)
        self.refresh_movable()

    # None => None
    def stop(self):
        Gtk.main_quit()

    # int, int => None
    def move(self, row, col):
        card = self.board[row][col].card
        # if card.face 
        # for i in range(0, 4):
        #     for j in range(0, 13):
        #         if self.is_empty(i, j):
        #             if 

    # Point => None
    def select(self, point):
        self._cursor = point

    # bool => None
    def shuffle(self, decr = True):
        fixed_cards = set()
        fixed_points = set()
        for i in range(0, 4):
            card0 = self.board[i][0].card
            if card0:
                for j in range(0, 13):
                    card = self.board[i][j].card
                    if card \
                       and card.suit == card0.suit \
                       and int(card.face) == j + 2:
                        fixed_cards.add(card)
                        fixed_points.add((i, j))

        cards = list(self.cards - fixed_cards)
        slots = list(self.points - fixed_points)
        for i in random.sample(range(0, len(cards)), len(cards)):
            row, col = slots[i]
            card = cards[i]
            if card.face != Face.Ace:
                self.board[row][col].card = card
            else:
                self.board[row][col].card = None

        if decr:
            self.shuffles = self.shuffles - 1
            
    # None => None
    def clear_movable(self):
        for i in range(0, 4):
            for j in range(0, 13):
                self.board[i][j].movable = False

    # Direction => Point
    def get_next_movable(self, direction):
        if direction == Direction.Up:
            for row in range(self.cursor.row - 1, -1, -1):
                for col in range(0, 13):
                    if self.board[row][col].movable:
                        return (row, col)
        elif direction == Direction.Down:
            for row in range(self.cursor.row + 1, 4):
                for col in range(0, 13):
                    if self.board[row][col].movable:
                        return (row, col)
        elif direction == Direction.Left:
            for col in range(0, self.cursor.col):
                if self.board[self.cursor.row][col].movable:
                    return (self.cursor.row, col)
        elif direction == Direction.Right:
            for col in range(self.cursor.col + 1, 13):
                if self.board[self.cursor.row][col].movable:
                    return (self.cursor.row, col)
        return None
            
    # None => None
    def refresh_movable(self):
        self.clear_movable()
        self.cursor = None
        
        cards = set()
        for i in range(0, 4):
            if self.is_empty(i, 0):
                for suit in Suit:
                    cards.add(Card(suit, Face.Two))
                break

        for i in range(0, 4):
            for j in range(0, 13):
                if self.is_empty(i, j) and not self.is_empty(i, j-1):
                    card = self.board[i][j-1].card
                    if card.face > Face.Two \
                       and card.face < Face.King:
                        cards.add(Card(card.suit,
                                       Face(card.face + 1)))

        for i in range(0, 4):
            for j in range(0, 13):
                if not self.is_empty(i, j) \
                   and self.board[i][j].card in cards:
                    self.board[i][j].movable = True

        for i in range(0, 4):
            for j in range(0, 13):
                self.cursor = (i, j)
                break
                        
    # None => bool
    def can_shuffle(self):
        return self.shuffles > 0

    # int, int => bool
    def is_empty(self, row, col):
        return self.board[row][col].card is None

    # int, int => bool
    def is_movable(self, row, col):
        return self.board[row][col].movable

    # None => Preferences
    @property
    def preferences(self):
        return self.game.preferences

    
class Preferences(GObject.Object):
    g_shuffles = GObject.Property(
        type = int,
        default = 4,
        nick = 'Max. shuffles',
        blurb = 'Maximum number of shuffles')

    # Game
    def __init__(self, game):
        super().__init__()

        self.game = game

    # None => int
    @property
    def shuffles(self):
        return self.g_shuffles
    
class Game:
    def __init__(self):
        self.preferences = Preferences(self)
        self.controller = Controller(self)
        self.model = Model(self)
        self.view = View(self)
    
# None => int
def main():
    win = Game()
    Gtk.main()
    
    return 0

if __name__ == '__main__':
    exit(main())

