#!/usr/bin/env python3

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
    def action_new(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_quit(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_shuffle(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_undo(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_key_press(self, *args):
        pass

    # * => *
    @abstractmethod
    def action_button_press(self, *args):
        pass

    # Point, Card => None
    @abstractmethod
    def report_cell_card_changed(self, addr, card):
        pass

    # Point, bool => None
    @abstractmethod
    def report_cell_movable_changed(self, addr, movable):
        pass

    # Point, bool => None
    @abstractmethod
    def report_cell_selected_changed(self, addr, selected):
        pass

    # int => None
    @abstractmethod
    def report_shuffles_changed(self, shuffles):
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

    # None => None
    @abstractmethod
    def report_undo_nothing(self):
        pass

    # None => None
    @abstractmethod
    def report_move(self, src, dst):
        pass

    # None => None
    @abstractmethod
    def report_shuffle(self):
        pass
    
    # None => Game
    @property
    def game(self):
        return self._game

    # None => Settings
    @property
    def settings(self):
        return self.game.settings
