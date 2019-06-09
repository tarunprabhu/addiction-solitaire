#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import random
from abc import ABC as AbstractBase, abstractmethod
from copy import deepcopy

from .types import Card, Face, Suit, Direction, Point
from .settings import Settings


class UndoAction(AbstractBase):
    # Game
    def __init__(self, game):
        self.game = game

    # None => None
    @abstractmethod
    def execute(self):
        pass


class MoveAction(UndoAction):
    # Game, Point, Point
    def __init__(self, game, src, dst):
        super().__init__(game)
        self.src = src
        self.dst = dst

    # None => None
    def execute(self):
        self.game.move(self.dst, self.src, True)
        

class ShuffleAction(UndoAction):
    # Game
    def __init__(self, game):
        super().__init__(game)
        self.cursor = deepcopy(game.cursor)
        self.snapshot = deepcopy(game.cards)

    # None => None
    def execute(self):
        self.game.clear_board()
        for card, addr in self.snapshot.items():
            if addr:
                self.game.set_card(addr, card)
        self.game.refresh(self.cursor)
        self.game.shuffles_incr()


class Cell:
    # Game, Point
    def __init__(self, game, addr):
        self.game = game
        self.addr = addr
        self._card = None
        self._movable = None

    # None => Card
    @property
    def card(self):
        return self._card

    # None => bool
    @property
    def movable(self):
        return self._movable

    # Card => None
    @card.setter
    def card(self, val):
        if (not self.card) or (not val) or (self.card != val):
            self._card = val
            self.game.ui.report_cell_card_changed(self.addr, self.card)
        if not val:
            self.movable = False

    # bool => None
    @movable.setter
    def movable(self, val):
        if self.movable != val:
            self._movable = val
            self.game.ui.report_cell_movable_changed(self.addr, self.movable)


class Game:
    # class, class
    def __init__(self, GameUI, SettingsUI):
        self.settings = Settings(self, SettingsUI)
        self.ui = GameUI(self)
        
        self.points = set()
        for i in range(0, 4):
            for j in range(0, 13):
                self.points.add(Point(i, j))

        self.board = []
        for i in range(0, 4):
            self.board.append([])
            for j in range(0, 13):
                self.board[i].append(Cell(self, Point(i, j)))

        self.cards = dict()
        for suit in Suit:
            for face in Face:
                self.cards[Card(suit, face)] = None

        self.started = False
        self.cursor = None
        self.undo = []
        self.shuffles = self.settings.shuffles

    # None => None
    def main(self):
        self.ui.main()

    # Point => None
    def refresh(self, curr):
        def get_nearest_movable():
            for row in [(curr.row + i) % 4 for i in range(0, 4)]:
                for col in range(curr.col, -1, -1):
                    if self.is_movable(Point(row, col)):
                        return Point(row, col)
                for col in range(curr.col + 1, 13):
                    if self.is_movable(Point(row, col)):
                        return Point(row, col)
            return None
        
        self.do_deselect()
        for addr in self.points:
            self.set_movable(addr, False)
                
        movable = self.get_movable_points()
        self.ui.report_movable_changed(len(movable))
        if movable:
            for addr in movable:
                self.set_movable(addr)
            if curr:
                self.do_select(get_nearest_movable())
            else:
                self.do_select(movable[0])
        else:
            if len(self.get_fixed_points()) == 48:
                self.do_game_over(True)
            elif self.shuffles == 0:
                self.do_game_over(False)

    # Point, Point, bool => None
    def move(self, src, dst, is_undo = False):
        card = self.get_card(src)
        self.clear_card(src)
        self.set_card(dst, card)
        if not is_undo:
            self.undo.append(MoveAction(self, src, dst))

        self.ui.report_move(src, dst)
        self.refresh(src)

    # bool => None
    def shuffle(self, is_undo = False):
        if self.started and not is_undo:
            self.undo.append(ShuffleAction(self))
        
        fixed_points = set(self.get_fixed_points())
        fixed_cards = set([self.get_card(addr) for addr in fixed_points])

        cards = list(self.cards.keys() - fixed_cards)
        slots = list(self.points - fixed_points)
        random.shuffle(cards)
        random.shuffle(slots)
        
        for addr in slots:
            self.clear_card(addr)
        for i in range(0, len(cards)):
            if cards[i].face != Face.Ace:
                self.set_card(slots[i], cards[i])

        self.refresh(self.cursor)

    # None => None
    def clear_board(self):
        for addr in self.points:
            self.clear_card(addr)

    # None => None
    def shuffles_decr(self):
        self.shuffles = self.shuffles - 1
        self.ui.report_shuffles_changed(self.shuffles)

    # None => None
    def shuffles_incr(self):
        self.shuffles = self.shuffles + 1
        self.ui.report_shuffles_changed(self.shuffles)
            
    # None => None
    def do_game_new(self):
        random.seed()

        self.clear_board()
        self.shuffle()
        self.shuffles = self.settings.shuffles
        self.started = True
        self.ui.report_game_new()

    # None => None
    def do_game_over(self, win):
        self.started = False
        self.ui.report_game_over(win)
        
    # None => None
    def do_quit(self):
        self.settings.write()
        self.ui.quit()

    # Direction => None
    def do_move_cursor(self, direction):
        # int, int => Point
        def get_nearest_movable_left(row, col):
            if self.is_movable(Point(row, col)):
                return Point(row, col)
            for c in range(col - 1, -1, -1):
                if self.is_movable(Point(row, c)):
                    return Point(row, c)
            return None

        # int, int => Point
        def get_nearest_movable_right(row, col):
            if self.is_movable(Point(row, col)):
                return Point(row, col)
            for c in range(col + 1, 13):
                if self.is_movable(Point(row, c)):
                    return Point(row, c)
            return None

        # int, int => Point
        def get_nearest_movable(row, col):
            left = get_nearest_movable_left(row, col)
            right = get_nearest_movable_right(row, col)
            if left and right:
                if (col - left.col) <= (right.col - col):
                    return left
                else:
                    return right
            elif left:
                return left
            elif right:
                return right
            return None
            
        # Direction => Point
        def get_next_movable_point(direction):
            rows = [(i + self.cursor.row) % 4 for i in range(1, 4)]
            if direction == Direction.Up:
                for row in reversed(rows):
                    addr = get_nearest_movable(row, self.cursor.col)
                    if addr:
                        return addr
            elif direction == Direction.Down:
                for row in rows:
                    addr = get_nearest_movable(row, self.cursor.col)
                    if addr:
                        return addr
            elif direction == Direction.Left:
                for col in range(self.cursor.col - 1, -1, -1):
                    if self.is_movable(Point(self.cursor.row, col)):
                        return Point(self.cursor.row, col)
                for row in reversed(rows):
                    for col in range(12, -1, -1):
                        if self.is_movable(Point(row, col)):
                            return Point(row, col)
                for col in range(12, self.cursor.col + 1, -1):
                    if self.is_movable(Point(self.cursor.row, col)):
                        return Point(self.cursor.row, col)
            elif direction == Direction.Right:
                for col in range(self.cursor.col + 1, 13):
                    if self.is_movable(Point(self.cursor.row, col)):
                        return Point(self.cursor.row, col)
                for row in rows:
                    for col in range(0, 13):
                        if self.is_movable(Point(row, col)):
                            return Point(row, col)
                for col in range(0, self.cursor.col):
                    if self.is_movable(Point(self.cursor.row, col)):
                        return Point(self.cursor.row, col)
            return None

        addr = get_next_movable_point(direction)
        if addr:
            self.do_select(addr)

    # Point => None
    def do_select(self, addr):
        self.do_deselect()
        self.cursor = addr
        self.ui.report_cell_selected_changed(self.cursor, True)

    # Point => None
    def do_deselect(self):
        if self.cursor:
            self.ui.report_cell_selected_changed(self.cursor, False)
        self.cursor = None

    # None => None
    def do_undo(self):
        if len(self.undo):
            self.undo.pop(-1).execute()
        else:
            self.ui.report_undo_nothing()
        
    # Point => None
    def do_move_card(self, src):
        # None => Point
        def get_dest():
            card = self.get_card(src)
            if card.face == Face.Two:
                for i in [(src.row + i + 1) % 4 for i in range(0, 4)]:
                    if self.is_empty(Point(i, 0)):
                        return Point(i, 0)
            else:
                pred = card.predecessor
                for curr in self.points:
                    left = curr.left
                    if left and self.is_empty(curr) \
                       and (not self.is_empty(left)) \
                       and (self.get_card(left).is_predecessor(card)):
                        return curr
            # This will only be called if the card is movable
            return None

        dst = get_dest()
        self.move(src, dst)
        
    # None => None
    def do_shuffle(self):
        self.shuffle()
        self.shuffles_decr()

    # None => [Point]
    def get_fixed_points(self):
        # int, Suit => int
        def get_fixed_length(row, suit):
            for col in range(0, 12):
                addr = Point(row, col)
                if self.is_empty(addr):
                    return col
                card = self.get_card(addr)
                if (card.suit != suit) or (int(card.face) != col + 2):
                    return col
            return 12

        fixed = []
        for row in range(0, 4):
            addr = Point(row, 0)
            if not self.is_empty(addr):
                suit = self.get_card(addr).suit
                for col in range(0, get_fixed_length(row, suit)):
                    fixed.append(Point(row, col))
        return fixed
        
    # None => [Point]
    def get_movable_points(self):
        def is_head_empty():
            for i in range(0, 4):
                if self.is_empty(Point(i, 0)):
                    return True
            return False
        
        movable = []
        if is_head_empty():
            for suit in Suit:
                movable.append(self.cards[Card(suit, Face.Two)])
        for curr in self.points:
            right = curr.right
            if right and (not self.is_empty(curr)) and self.is_empty(right):
                succ = self.get_card(curr).successor
                if succ:
                    movable.append(self.cards[succ])
        return movable

    # Point, bool => None
    def set_movable(self, addr, movable = True):
        self.board[addr.row][addr.col].movable = movable

    # Point => bool
    def is_movable(self, addr):
        return self.board[addr.row][addr.col].movable
        
    # Point, Card => None
    def set_card(self, addr, card):
        self.board[addr.row][addr.col].card = card
        self.cards[card] = addr

    # Point => None
    def clear_card(self, addr):
        card = self.get_card(addr)
        self.board[addr.row][addr.col].card = None
        self.board[addr.row][addr.col].movable = None
        if card:
            self.cards[card] = None
        
    # Point => Card
    def get_card(self, addr):
        if self.board[addr.row][addr.col] is None:
            raise RuntimeError('Getting card from empty cell: {}', addr)
        return self.board[addr.row][addr.col].card

    # Point => bool
    def is_empty(self, addr):
        return self.get_card(addr) is None
    