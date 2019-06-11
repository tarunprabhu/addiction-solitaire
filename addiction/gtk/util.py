#!/usr/bin/env python3

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
