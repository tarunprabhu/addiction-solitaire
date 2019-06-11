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
from gi.repository import Gdk

from ..types import Color

# Color => Gdk.RGBA
def as_rgba(color):
    return Gdk.RGBA(color.red / 255,
                    color.blue / 255,
                    color.green / 255,
                    color.alpha)
    
# Gdk.RGBA => Color
def as_color(rgba):
    return Color(int(rgba.red * 255),
                 int(rgba.blue * 255),
                 int(rgba.green * 255),
                 rgba.alpha)
