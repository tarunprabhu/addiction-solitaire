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

from collections import namedtuple


Author = namedtuple('Author', ['name', 'email'])


name = 'Addiction Solitaire'

description = """
Simple addiction solitaire game with text and GUI modes
"""

licence = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

copyright = 'Copyright (C) 2019, Tarun Prabhu'

version = '1.0'

website = 'https://www.github.com/tarunprabhu/addiction-solitaire'

authors = [
    Author('Tarun Prabhu', 'tarun.prabhu@gmail.com')
]

cur_dir = os.path.dirname(os.path.abspath(__file__))
icon_dir = os.path.join(cur_dir, 'icons')
card_dir = os.path.join(cur_dir, 'cards')
