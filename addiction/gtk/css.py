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

from ..types import Color

class CSS:
    # str, { str: (*, str) } => Gtk.CssProvider
    def __init__(self, selector, properties):
        css = []
        for key, val in properties.items():
            if isinstance(val, Color):
                css.append('{}: rgba({},{},{},{})'.format(
                    key,
                    val.red,
                    val.green,
                    val.blue,
                    val.alpha))
            elif isinstance(val, tuple):
                css.append('{}: {}{}'.format(key, val[0], val[1]))
            elif isinstance(val, int) \
                 or isinstance(val, str) \
                 or isinstance(val, float):
                css.append('{}: {}'.format(key, str(val)))
            else:
                raise RuntimeError(
                    'Unsupported CSS property type: {}'.format(type(val)))

        self.css = '{} {{\n{}}}'.format(selector,
                                        ';\n  '.join(css))
                

    # None => Gtk.CssProvider
    def get_provider(self):
        provider = Gtk.CssProvider.new()

        provider.load_from_data(self.css.encode('utf-8'))
        return provider

    # None => str
    def get_css(self):
        return self.css

