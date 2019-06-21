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

from abc import ABC as AbstractBase, abstractmethod

# The action_* functions are callbacks from the user. They are triggered as
# a result of a user action (key press, mouse click etc). The report_*
# functions are called by the game itself. They cause the UI to be updated,
# either the board itself or the status bar which has information about the
# state of the game
class GameUI(AbstractBase):
    # Game
    def __init__(self, game):
        self._game = game

    # * => *
    @abstractmethod
    def main(self):
        pass

    # * => *
    @abstractmethod
    def quit(self):
        pass
    
    # * => *
    @abstractmethod
    def action_key_press(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_button_press(self, *args):
        pass

    # * => None
    @abstractmethod
    def action_new(self, *args):
        pass

    # * => None
    @abstractmethod
    def action_quit(self, *args):
        pass

    # Point, Card => None
    @abstractmethod
    def report_cell_card_changed(self, addr, card):
        pass

    # Point, IntFlag => None
    @abstractmethod
    def report_cell_flags_changed(self, addr, flags):
        pass

    # bool => None
    @abstractmethod
    def report_selection_changed(self, selected):
        pass

    # int => None
    @abstractmethod
    def report_undo_changed(self, undos):
        pass
    
    # int => None
    @abstractmethod
    def report_shuffles_changed(self, shuffles):
        pass

    # int => None
    @abstractmethod
    def report_moves_changed(self, moves):
        pass

    # int => None
    @abstractmethod
    def report_correct_changed(self, correct):
        pass
    
    # int => None
    @abstractmethod
    def report_movable_changed(self, movable):
        pass
    
    # bool => None
    @abstractmethod
    def report_game_over(self, win):
        pass

    # None => None
    @abstractmethod
    def report_game_new(self):
        pass

    # * => None
    def action_shuffle(self, *args):
        self.game.do_shuffle()

    # * => None
    def action_undo(self, *args):
        self.game.do_undo()

    # * => None
    def action_move(self, *args):
        if self.game.selected:
            self.game.do_move_card(self.game.selected)
        
    # None => Game
    @property
    def game(self):
        return self._game

    # None => Settings
    @property
    def settings(self):
        return self.game.settings
