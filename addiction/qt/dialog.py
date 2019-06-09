#!/usr/bin/env python3

import os

from ..settings_ui import SettingsUI

class SettingsQt(SettingsUI):
    # Game
    def __init__(self, game):
        super().__init__(game)
