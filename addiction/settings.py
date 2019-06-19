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

import os
import json
import sys

from .types import Color


class SettingsEncoder(json.JSONEncoder):
    #
    def __init__(self, *args, **kwargs):
        super().__init__(indent = 2)

    # * => dict
    def default(self, obj):
        if isinstance(obj, Color):
            return { '_type': 'Color',
                     'red': obj.red,
                     'green': obj.green,
                     'blue': obj.blue,
                     'alpha': obj.alpha}
        return super().default(obj)


class SettingsDecoder(json.JSONDecoder):
    # 
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook = self.object_hook, *args, **kwargs)

    # dict => *
    def object_hook(self, obj):
        if ('_type' in obj) and (obj['_type'] == 'Color'):
            return Color(obj['red'], obj['green'], obj['blue'], obj['alpha'])
        return obj


class Settings:
    # FIXME: Make this more platform independent
    dirname = os.path.join(os.path.expanduser('~'),
                           '.config',
                           'addiction-solitaire')
    filename = os.path.join(dirname, 'settings.json')

    # Constants
    Unlimited = -1

    # Default settings
    def_color_selected = Color(164, 0, 0)
    def_color_movable = Color(252, 175, 62)
    def_color_correct = Color(115, 210, 22)
    def_color_normal = Color(210, 210, 210)
    def_border = 4
    def_radius = 4
    def_shuffles = 3
    def_highlight_movable = True
    def_highlight_correct = True

    # Game,
    def __init__(self, game, **overrides):
        self.game = game
        self.values = dict()
        self.overrides = dict(**overrides)
        self.read()

    # None => None
    def read(self):
        try:
            if os.path.exists(Settings.filename):
                with open(Settings.filename) as f:
                    self.values = json.load(f,
                                            cls = SettingsDecoder)
        except json.JSONDecodeError as err:
            print('Error reading settings file: {}'.format(err),
                  file = sys.stderr)        

        for key, val in self.overrides.items():
            self.values[key] = val
            
        for key, val in Settings.__dict__.items():
            if key.startswith('def_'):
                name = key.replace('def_', '') 
                if name not in self.values:
                    self.values[name] = val
            
    # None => None
    def write(self):
        if not os.path.exists(Settings.dirname):
            os.mkdir(Settings.dirname)
        with open(Settings.filename, 'w') as f:
            json.dump(self.values, f, cls = SettingsEncoder)

    # None => bool
    def is_unlimited_shuffles(self):
        return self.shuffles == self.Unlimited
            
    # None => Gdk.RGBA
    @property
    def color_selected(self):
        return self.values['color_selected']

    # None => Gdk.RGBA
    @property
    def color_movable(self):
        return self.values['color_movable']

    # None => Gdk.RGBA
    @property
    def color_correct(self):
        return self.values['color_correct']

    # None => Gdk.RGBA
    @property
    def color_normal(self):
        return self.values['color_normal']

    # None => int
    @property
    def border(self):
        return self.values['border']

    # None => int
    @property
    def radius(self):
        return self.values['radius']

    # None => int
    @property
    def shuffles(self):
        return self.values['shuffles']

    # None => bool
    @property
    def highlight_movable(self):
        return self.values['highlight_movable']

    # None => bool
    @property
    def highlight_correct(self):
        return self.values['highlight_correct']
    
    # * => None
    @color_selected.setter
    def color_selected(self, val):
        self.values['color_selected'] = val

    # * => None
    @color_movable.setter
    def color_movable(self, val):
        self.values['color_movable'] = val

    # * => None
    @color_correct.setter
    def color_correct(self, val):
        self.values['color_correct'] = val

    # * => None
    @color_normal.setter
    def color_normal(self, val):
        self.values['color_normal'] = val

    # int => None
    @border.setter
    def border(self, val):
        self.values['border'] = val

    # int => None
    @radius.setter
    def radius(self, val):
        self.values['radius'] = val

    # int => None
    @shuffles.setter
    def shuffles(self, val):
        self.values['shuffles'] = val

    # bool => None
    @highlight_movable.setter
    def highlight_movable(self, val):
        self.values['highlight_movable'] = val

    # bool => None
    @highlight_correct.setter
    def highlight_correct(self, val):
        self.values['highlight_correct'] = val
