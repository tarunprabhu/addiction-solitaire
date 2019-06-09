#!/usr/bin/env python3

from .settings import Settings

class SettingsUI:
    # Game
    def __init__(self, game):
        self.game = game

    # None => Setting
    @property
    def settings(self):
        return self.game.settings
