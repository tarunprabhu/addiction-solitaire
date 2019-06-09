#!/usr/bin/env python3

import os

from ..game_ui import GameUI
from ..settings_ui import SettingsUI

class GameQt(GameUI):
    # Game
    def __init__(self, game):
        super().__init__(game)
