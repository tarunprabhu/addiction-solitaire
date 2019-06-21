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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import random
import sys
from abc import ABC as AbstractBase, abstractmethod
from copy import deepcopy
from threading import Lock, Timer
from time import sleep

from .types import Card, Face, Suit, Direction, Point, CellFlags
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
        self.selected = deepcopy(game.selected)
        self.cards = deepcopy(game.cards)

    # None => None
    def execute(self):
        self.game.clear_board()
        for card, addr in self.cards.items():
            if addr:
                self.game.set_card(addr, card)
        self.game.shuffles_decr()
        self.game.refresh(self.selected)


class Cell:
    # Game, Point
    def __init__(self, game, addr):
        self.game = game
        self.addr = addr
        self._card = None
        self._flags = CellFlags.Normal

    # None => None
    def clear(self):
        card = self.card
        self._card = None
        self.clear_flags()
        if card:
            self.game.ui.report_cell_card_changed(self.addr, None)

    # None => None
    def clear_flags(self):
        self._flags = CellFlags.Normal
        self.game.ui.report_cell_flags_changed(self.addr, self.flags)

    # None => Card
    @property
    def card(self):
        return self._card

    # None => bool
    @property
    def movable(self):
        return bool(self._flags & CellFlags.Movable)

    # None => bool
    @property
    def correct(self):
        return bool(self._flags & CellFlags.Correct)

    # None => bool
    @property
    def selected(self):
        return bool(self._flags & CellFlags.Selected)

    # None => CellFlags
    @property
    def flags(self):
        return self._flags

    # Card => None
    def set_card(self, val):
        if (not self.card) or (self.card != val):
            self._card = val
            self.game.ui.report_cell_card_changed(self.addr, self.card)

    # None => None
    def set_selected(self):
        if not self.selected:
            self._flags = self._flags | CellFlags.Selected
            self.game.ui.report_cell_flags_changed(self.addr, self.flags)
            
    # None => None
    def set_movable(self):
        if not self.movable:
            self._flags = self._flags | CellFlags.Movable
            self.game.ui.report_cell_flags_changed(self.addr, self.flags)

    # None => None
    def set_correct(self):
        if not self.correct:
            self._flags = self._flags | CellFlags.Correct
            self.game.ui.report_cell_flags_changed(self.addr, self.flags)

    # None => None
    def reset_selected(self):
        if self.selected:
            self._flags = self._flags & ~CellFlags.Selected
            self.game.ui.report_cell_flags_changed(self.addr, self.flags)
            
class Game:
    # class, bool
    def __init__(self, GameUI, debug, **kwargs):
        self.debug = debug

        self.points = []
        for i in range(0, 4):
            self.points.append([])
            for j in range(0, 13):
                self.points[i].append(Point(self.points, i, j))

        self.all_points = set()
        for i in range(0, 4):
            for j in range(0, 13):
                self.all_points.add(self.points[i][j])

        self.board = []
        for i in range(0, 4):
            self.board.append([])
            for j in range(0, 13):
                self.board[i].append(Cell(self, self.points[i][j]))

        self.cards = dict()
        for suit in Suit:
            for face in Face:
                self.cards[Card(suit, face)] = None

        self.lock = Lock()
        self.timer = None
        self.selected = None
        self.shuffles = 0
        self.moves = 0
        self.undo = []
        self.empty = []

        self.settings = Settings(self, **kwargs)
        self.ui = GameUI(self)

    # * => None
    def dbg(self, *args):
        if self.debug:
            print(*args, file = sys.stderr)

    # None => None
    def main(self):
        self.ui.main()

    # Finds all movable cards and checks if the game is over/stuck.
    # The argument to this function is the last known cursor position.
    #
    # Point => None
    def refresh(self, curr):
        def get_nearest_movable():
            # First check for cards to the right of the current location
            # on the same row
            for col in range(curr.col, 13):
                if self.is_movable(self.points[curr.row][col]):
                    return self.points[curr.row][col]

            # Then on rows below the current row, cycling back to the row
            # above the current row. Look for the nearest card to the left of
            # the current column and then to the right
            for row in [(curr.row + i) % 4 for i in range(1, 4)]:
                for col in range(curr.col, -1, -1):
                    if self.is_movable(self.points[row][col]):
                        return self.points[row][col]
                for col in range(curr.col + 1, 13):
                    if self.is_movable(self.points[row][col]):
                        return self.points[row][col]

            # And then cards to the left of the current location on the same row
            for col in range(curr.col - 1, -1, -1):
                if self.is_movable(self.points[curr.row][col]):
                    return self.points[curr.row][col]

            # This will be called only if there is at least one movable card,
            # so we should never get here
            return None

        self.do_deselect()
        for addr in self.all_points:
            self.clear_flags(addr)

        correct = self.get_correct_points()
        self.ui.report_correct_changed(len(correct))
        for addr in correct:
            self.set_correct(addr)

        if len(correct) == 48:
            self.do_game_over(True)
        else:
            movable = self.get_movable_points()
            self.ui.report_movable_changed(len(movable))
            self.dbg('refresh')
            self.dbg('  movable: ', *movable)
            self.dbg('  empty: ', *self.empty)
            if movable:
                for addr in movable:
                    self.set_movable(addr)
                if curr:
                    self.do_select(get_nearest_movable())
                else:
                    self.do_select(movable[0])
                self.dbg('  selected:', self.selected)
            else:
                if self.shuffles >= self.settings.shuffles:
                    self.do_game_over(False)

    # Point, Point, bool => None
    def move(self, src, dst, is_undo = False):
        self.dbg('move card')
        self.dbg(' ', self.get_card(src), ':', src, '=>', dst)
        card = self.get_card(src)
        self.clear_card(src)
        self.set_card(dst, card)
        if not is_undo:
            self.undo_push(MoveAction(self, src, dst))
            self.moves_incr()
        else:
            self.moves_decr()

        self.refresh(src)

    # bool => None
    def shuffle(self, is_undo = False):
        if self.is_started() and not is_undo:
            self.undo_push(ShuffleAction(self))

        correct_points = set(self.get_correct_points())
        correct_cards = set([self.get_card(addr) for addr in correct_points])

        cards = list(self.cards.keys() - correct_cards)
        addrs = list(self.all_points - correct_points)
        random.shuffle(cards)
        random.shuffle(addrs)

        self.dbg('shuffle')
        self.dbg('  points:', *correct_points)
        self.dbg('  cards:', *correct_cards)
        for addr in addrs:
            self.clear_card(addr)
        self.empty = []
        for card, addr in zip(cards, addrs):
            if card.face != Face.Ace:
                self.set_card(addr, card)
            else:
                self.empty.append(addr)
        self.dbg('  empty:', *self.empty)

        self.refresh(self.selected)

    # None => None
    def clear_board(self):
        for addr in self.all_points:
            self.clear_card(addr)

    # None => None
    def shuffles_decr(self):
        if not self.settings.is_unlimited_shuffles():
            self.shuffles = self.shuffles - 1
        self.ui.report_shuffles_changed(self.shuffles)

    # None => None
    def shuffles_incr(self):
        if not self.settings.is_unlimited_shuffles():
            self.shuffles = self.shuffles + 1
        self.ui.report_shuffles_changed(self.shuffles)

    # None => None
    def moves_decr(self):
        self.moves = self.moves - 1
        self.ui.report_moves_changed(self.moves)

    # None => None
    def moves_incr(self):
        self.moves = self.moves + 1
        self.ui.report_moves_changed(self.moves)

    # UndoAction => None
    def undo_push(self, action):
        self.undo.append(action)
        self.ui.report_undo_changed(len(self.undo))

    # None => UndoAction
    def undo_pop(self):
        self.ui.report_undo_changed(len(self.undo) - 1)
        return self.undo.pop(-1)

    # None => None
    def do_update_settings(self):
        if self.is_started():
            if self.selected:
                self.refresh(self.selected)
            else:
                self.refresh(self.points[0][0])

    # None => None
    def do_game_new(self):
        random.seed()

        self.clear_board()
        self.selected = None
        self.undo = []
        self.shuffle()
        self.shuffles = 0
        self.timer_start()
        self.ui.report_game_new()

    # None => None
    def do_game_over(self, win):
        self.timer_stop()
        self.shuffles = 0
        self.moves = 0
        self.undo = []
        self.ui.report_game_over(win)

    # None => None
    def do_quit(self):
        self.timer_stop()
        self.ui.quit()

    # Direction => None
    def do_move_selected(self, direction):
        # int, int => Point
        def get_nearest_movable_left(row, col):
            if self.is_movable(self.points[row][col]):
                return self.points[row][col]
            for c in range(col - 1, -1, -1):
                if self.is_movable(self.points[row][c]):
                    return self.points[row][c]
            return None

        # int, int => Point
        def get_nearest_movable_right(row, col):
            if self.is_movable(self.points[row][col]):
                return self.points[row][col]
            for c in range(col + 1, 13):
                if self.is_movable(self.points[row][c]):
                    return self.points[row][c]
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
            rows = [(i + self.selected.row) % 4 for i in range(1, 4)]
            if direction == Direction.Up:
                for row in reversed(rows):
                    addr = get_nearest_movable(row, self.selected.col)
                    if addr:
                        return addr
            elif direction == Direction.Down:
                for row in rows:
                    addr = get_nearest_movable(row, self.selected.col)
                    if addr:
                        return addr
            elif direction == Direction.Left:
                for col in range(self.selected.col - 1, -1, -1):
                    if self.is_movable(self.points[self.selected.row][col]):
                        return self.points[self.selected.row][col]
                for row in reversed(rows):
                    for col in range(12, -1, -1):
                        if self.is_movable(self.points[row][col]):
                            return self.points[row][col]
                for col in range(12, self.selected.col + 1, -1):
                    if self.is_movable(self.points[self.selected.row][col]):
                        return self.points[self.selected.row][col]
            elif direction == Direction.Right:
                for col in range(self.selected.col + 1, 13):
                    if self.is_movable(self.points[self.selected.row][col]):
                        return self.points[self.selected.row][col]
                for row in rows:
                    for col in range(0, 13):
                        if self.is_movable(self.points[row][col]):
                            return self.points[row][col]
                for col in range(0, self.selected.col):
                    if self.is_movable(self.points[self.selected.row][col]):
                        return self.points[self.selected.row][col]
            return None

        addr = get_next_movable_point(direction)
        self.dbg('change selected')
        self.dbg('  ', direction, self.selected, '=>', addr)
        if addr:
            self.do_select(addr)

    # Point => None
    def do_select(self, addr):
        self.do_deselect()
        self.dbg('select:', addr)
        self.set_selected(addr, True)
        self.selected = addr
        self.ui.report_selection_changed(self.selected is not None)

    # Point => None
    def do_deselect(self):
        if self.selected:
            self.dbg('unselect:', self.selected)
            self.set_selected(self.selected, False)
        self.selected = None
        self.ui.report_selection_changed(False)

    # None => None
    def do_undo(self):
        if self.is_started():
            if len(self.undo):
                return self.undo_pop().execute()

    # Point => None
    def do_move_card(self, src):
        # None => Point
        def get_dest():
            card = self.get_card(src)
            if card.face == Face.Two:
                for i in [(src.row + i + 1) % 4 for i in range(0, 4)]:
                    if self.is_empty(self.points[i][0]):
                        return self.points[i][0]
            else:
                return self.cards[card.predecessor].right

            # This will only be called if the card is movable
            return None

        dst = get_dest()
        self.move(src, dst)

    # None => None
    def do_shuffle(self):
        if self.is_started():
            if self.settings.is_unlimited_shuffles() \
               or (self.shuffles < self.settings.shuffles):
                self.shuffle()
                self.shuffles_incr()

    # None => [Point]
    def get_correct_points(self):
        # int, Suit => int
        def get_correct_length(row, suit):
            for col in range(0, 12):
                addr = self.points[row][col]
                if self.is_empty(addr):
                    return col
                card = self.get_card(addr)
                if (card.suit != suit) or (int(card.face) != col + 2):
                    return col
            return 12

        correct = []
        for row in range(0, 4):
            addr = self.points[row][0]
            if not self.is_empty(addr):
                suit = self.get_card(addr).suit
                for col in range(0, get_correct_length(row, suit)):
                    correct.append(self.points[row][col])
        return correct

    # None => [Point]
    def get_movable_points(self):
        movable = []
        for addr in self.empty:
            if addr.col == 0:
                for suit in Suit:
                    movable.append(self.cards[Card(suit, Face.Two)])
                break

        for addr in self.empty:
            left = addr.left
            if left and not self.is_empty(left):
                succ = self.get_card(left).successor
                if succ:
                    movable.append(self.cards[succ])

        return movable

    # Point => None
    def clear_card(self, addr):
        card = self.get_card(addr)
        if card:
            self.cards[card] = None
            self.empty.append(addr)
        self.board[addr.row][addr.col].clear()

    # None => None
    def clear_flags(self, addr):
        self.board[addr.row][addr.col].clear_flags()

    # Point, Card => None
    def set_card(self, addr, card):
        if addr in self.empty:
            self.empty.remove(addr)
        self.board[addr.row][addr.col].set_card(card)
        self.cards[card] = addr

    # Point, bool => None
    def set_movable(self, addr, val = True):
        if val:
            self.board[addr.row][addr.col].set_movable()

    # Point, bool => None
    def set_correct(self, addr, val = True):
        if val:
            self.board[addr.row][addr.col].set_correct()

    # Point, bool => None
    def set_selected(self, addr, val = True):
        if val:
            self.board[addr.row][addr.col].set_selected()
        else:
            self.board[addr.row][addr.col].reset_selected()
        
    # Point => Card
    def get_card(self, addr):
        if self.board[addr.row][addr.col] is None:
            raise RuntimeError('Getting card from empty cell: {}', addr)
        return self.board[addr.row][addr.col].card

    # Point => bool
    def is_movable(self, addr):
        return self.board[addr.row][addr.col].movable

    # Point => bool
    def is_correct(self, addr):
        return self.board[addr.row][addr.col].correct

    # Point => bool
    def is_selected(self, addr):
        return self.board[addr.row][addr.col].selected

    # Point => bool
    def is_empty(self, addr):
        return self.get_card(addr) is None

    # None => bool
    def is_started(self):
        return self.timer is not None

    # None => None
    def timer_start(self):
        self.timer_tick(True)

    # None => None
    def timer_stop(self):
        if self.timer:
            self.timer.cancel()
        self.timer = None

    # bool => None
    def timer_tick(self, start = False):
        if start:
            self.ticks = 0
        else:
            self.ticks = self.ticks + 1
        self.timer = Timer(1, self.timer_tick)
        self.timer.start()
