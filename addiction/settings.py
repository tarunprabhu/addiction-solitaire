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
from gi.repository import GObject, Gtk, Gdk, GLib

import os
import sys

class Settings:
    dirname = os.path.join(GLib.get_user_config_dir(), 'addiction-solitaire')
    filename = os.path.join(dirname, 'settings.conf')
    group = 'solitaire'

    # Default settings
    def_color_selected = Gdk.RGBA(78/255, 154/255, 6/255, 1.0)
    def_color_movable = Gdk.RGBA(252/255, 175/255, 62/255, 1.0)
    def_color_fixed = Gdk.RGBA(255, 0, 0, 1.0)
    def_color_normal = Gdk.RGBA(230/255, 230/255, 230/255, 1.0)
    def_border = 4
    def_radius = 8
    def_shuffles = 3
    def_highlight_movable = True
    def_highlight_fixed = False

    # Game, class
    def __init__(self, game, SettingsUI):
        self.game = game

        self.keyfile = GLib.KeyFile.new()
        self.read()
        self.ui = None
        if SettingsUI:
            self.ui = SettingsUI(self.game)

    # None => None
    def read(self):
        if not os.path.exists(Settings.dirname):
            os.mkdir(Settings.dirname)
        if not os.path.exists(Settings.filename):
            with open(Settings.filename, 'w'):
                pass
                
        try:
            self.keyfile.load_from_file(Settings.filename,
                                        GLib.KeyFileFlags.KEEP_COMMENTS \
                                        | GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except GLib.Error:
            print('Error reading settings file: {}'.format(Settings.filename),
                  file = sys.stderr)

        keys = set()
        if self.keyfile.has_group(Settings.group):
            keys = set(self.keyfile.get_keys(Settings.group)[0])

        if 'color_selected' not in keys:
            self.color_selected = Settings.def_color_selected
        if 'color_movable' not in keys:
            self.color_movable = Settings.def_color_movable
        if 'color_normal' not in keys:
            self.color_normal = Settings.def_color_normal
        if 'border' not in keys:
            self.border = Settings.def_border
        if 'radius' not in keys:
            self.radius = Settings.def_radius
        if 'shuffles' not in keys:
            self.shuffles = Settings.def_shuffles
        if 'highlight_movable' not in keys:
            self.highlight_movable = Settings.def_highlight_movable
        if 'highlight_fixed' not in keys:
            self.highlight_fixed = Settings.def_highlight_fixed
        
    # None => None
    def write(self):
        self.keyfile.save_to_file(Settings.filename)
        
    # None => Gdk.RGBA
    @property
    def color_selected(self):
        color = Gdk.RGBA()
        color.parse(self.keyfile.get_string(Settings.group, 'color_selected'))
        return color

    # None => Gdk.RGBA
    @property
    def color_movable(self):
        color = Gdk.RGBA()
        color.parse(self.keyfile.get_string(Settings.group, 'color_movable'))
        return color

    # None => Gdk.RGBA
    @property
    def color_fixed(self):
        color = Gdk.RGBA()
        color.parse(self.keyfile.get_string(Settings.group, 'color_fixed'))
        return color
    
    # None => Gdk.RGBA
    @property
    def color_normal(self):
        color = Gdk.RGBA()
        color.parse(self.keyfile.get_string(Settings.group, 'color_normal'))
        return color
    
    # None => int
    @property
    def border(self):
        return self.keyfile.get_integer(Settings.group, 'border')

    # None => int
    @property
    def radius(self):
        return self.keyfile.get_integer(Settings.group, 'radius')
    
    # None => int
    @property
    def shuffles(self):
        return self.keyfile.get_integer(Settings.group, 'shuffles')

    # None => bool
    @property
    def highlight_movable(self):
        return self.keyfile.get_boolean(Settings.group, 'highlight_movable')

    # None => bool
    @property
    def highlight_fixed(self):
        return self.keyfile.get_boolean(Settings.group, 'highlight_fixed')
    
    # * => None
    @color_selected.setter
    def color_selected(self, val):
        color = Gdk.RGBA()
        if isinstance(val, Gdk.RGBA):
            color = Gdk.RGBA.copy(val)
        elif not color.parse(val):
            raise RuntimeError('Could not set color from "{}"'.format(val))
        self.keyfile.set_string(Settings.group, 'color_selected',
                                color.to_string())

    # * => None
    @color_movable.setter
    def color_movable(self, val):
        color = Gdk.RGBA()
        if isinstance(val, Gdk.RGBA):
            color = Gdk.RGBA.copy(val)
        elif not color.parse(val):
            raise RuntimeError('Could not set color from "{}"'.format(val))
        self.keyfile.set_string(Settings.group, 'color_movable',
                                color.to_string())

    # * => None
    @color_fixed.setter
    def color_fixed(self, val):
        color = Gdk.RGBA()
        if isinstance(val, Gdk.RGBA):
            color = Gdk.RGBA.copy(val)
        elif not color.parse(val):
            raise RuntimeError('Could not set color from "{}"'.format(val))
        self.keyfile.set_string(Settings.group, 'color_fixed',
                                color.to_string())
        
    # * => None
    @color_normal.setter
    def color_normal(self, val):
        color = Gdk.RGBA()
        if isinstance(val, Gdk.RGBA):
            color = Gdk.RGBA.copy(val)
        elif not color.parse(val):
            raise RuntimeError('Could not set color from "{}"'.format(val))
        self.keyfile.set_string(Settings.group, 'color_normal',
                                color.to_string())
        
    # int => None
    @border.setter
    def border(self, val):
        self.keyfile.set_integer(Settings.group, 'border', val)

    # int => None
    @radius.setter
    def radius(self, val):
        self.keyfile.set_integer(Settings.group, 'radius', val)
        
    # int => None
    @shuffles.setter
    def shuffles(self, val):
        self.keyfile.set_integer(Settings.group, 'shuffles', val)

    # bool => None
    @highlight_movable.setter
    def highlight_movable(self, val):
        self.keyfile.set_boolean(Settings.group, 'highlight_movable', val)

    # bool => None
    @highlight_fixed.setter
    def highlight_fixed(self, val):
        self.keyfile.set_boolean(Settings.group, 'highlight_fixed', val)
