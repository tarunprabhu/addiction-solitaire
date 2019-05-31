#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import Pixbuf as GdkPixbuf

from collections import namedtuple

import os
import random

Card = namedtuple('Card', ['suit', 'face'])


class UI(Gtk.Window):
    # Appearance options
    css_selected = ('frame {'
                    '  border-width: 4px;'
                    '  border-style: solid;'
                    '  border-color: green;'
                    '}').encode('utf-8')
    css_movable = ('frame {'
                   '  border-width: 4px;'
                   '  border-style: solid;'
                   '  border-color: yellow;'
                   '}').encode('utf-8')
    css_normal = ('frame {'
                  '  border-width: 4px;'
                  '  border-style: solid;'
                  '  border-color: rgba(0, 0, 0, 0);'
                  '}').encode('utf-8')

    # Game => None
    def __init__(self, game):
        Gtk.Window.__init__(self, title='Addiction Solitaire')

        row_spacing = 0
        col_spacing = 0
        border = 0
        card_width = 60
        card_height = 90

        self._game = game

        self.cards = dict()
        for i, s in enumerate(game.suits):
            self.cards[s] = dict()
            for c in range(1, 14):
                filename = os.path.join('cards', 'png', s, '{}.png'.format(str(c)))
                self.cards[s][c] = \
                    Gtk.Image.new_from_pixbuf(
                        GdkPixbuf.new_from_file_at_scale(filename,
                                                         card_width,
                                                         card_height,
                                                         False))

        self.frames = []
        for _ in range(0, 4):
            self.frames.append([None] * 13)
            
        grid = Gtk.Grid.new()
        grid.set_row_spacing(row_spacing)
        grid.set_column_spacing(col_spacing)
        grid.set_border_width(border)
        for i, s in enumerate(game.suits):
            for j in range(0, 13):
                frame = Gtk.Frame.new()
                frame.set_size_request(card_width, card_height)
                frame.set_shadow_type(Gtk.ShadowType.NONE)

                evt = Gtk.EventBox.new()
                evt.add(frame)
                evt.connect('button-press-event', self.cb_buttonpress, (i, j))

                grid.attach(evt, j - 1, i, 1, 1)
                self.frames[i][j] = frame

        self.add(grid)
        self.refresh()

        self.connect('destroy', Gtk.main_quit)
        self.connect('key-press-event', self.cb_keypress)
        self.show_all()

    # None => None
    def refresh(self):
        for i in range(0, 4):
            for j in range(0, 13):
                child = self.frames[i][j].get_child()
                if child:
                    self.frames[i][j].remove(child)
                self.set_css_normal(i, j)
                if not self.game.is_empty(i, j):
                    s, c = self.game.get_card(i, j)
                    self.frames[i][j].add(self.cards[s][c])

        for n, (i, j) in enumerate(self.game.movable):
            if n == 0:
                self.sel_row = i
                self.sel_col = j
                self.set_css_selected(i, j)
            else:
                self.set_css_movable(i, j)
                    
    # Gtk.Widget, GdkEvent => bool
    def cb_keypress(self, widget, evt):
        key = evt.keyval
        row = self.sel_row
        col = self.sel_col
        moved = False
        if key == Gdk.KEY_Up or key == Gdk.KEY_KP_Up:
            if self.sel_row > 0:
                self.sel_row = self.sel_row - 1
                moved = True
        elif key == Gdk.KEY_Down or key == Gdk.KEY_KP_Down:
            if self.sel_row < 3:
                self.sel_row = self.sel_row + 1
                moved = True
        elif key == Gdk.KEY_Left or key == Gdk.KEY_KP_Left:
            if self.sel_col > 0:
                self.sel_col = self.sel_col - 1
                moved = True
        elif key == Gdk.KEY_Right or key == Gdk.KEY_KP_Right:
            if self.sel_col < 13:
                self.sel_col = self.sel_col + 1
                moved = True
        elif key == Gdk.KEY_q:
            Gtk.main_quit()
        elif key == Gdk.KEY_Return \
             or key == Gdk.KEY_KP_Enter \
             or key == Gdk.KEY_space:
            if (row, col) in self.game.movable:
                self.game.move(row, col)

        if moved:
            if (row, col) in self.game.movable:
                self.set_css_movable(row, col)
            else:
                self.set_css_normal(row, col)
            self.set_css_selected(self.sel_row, self.sel_col)
                
        return False

    # Gtk.Widget, Gdk.Event => bool
    def cb_buttonpress(self, widget, evt, user_data):
        i, j = user_data
        if not self.game.is_empty(i, j):
            if evt.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                if (i, j) in self.game.movable:
                    self.game.move(i, j)
            elif evt.type == Gdk.EventType.BUTTON_PRESS:
                self.set_css_selected(i, j)

        return False
    
    # int, int => None
    def set_css_selected(self, i, j):
        self.set_css(self.frames[i][j], UI.css_selected)

    # int, int => None
    def set_css_normal(self, i, j):
        self.set_css(self.frames[i][j], UI.css_normal)

    # int, int => None
    def set_css_movable(self, i, j):
        self.set_css(self.frames[i][j], UI.css_movable)
        
    # Gtk.Widget, str => None
    def set_css(self, widget, css):
        provider = Gtk.CssProvider.new()
        provider.load_from_data(css)
        widget.get_style_context() \
              .add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    # None => Game
    @property
    def game(self):
        return self._game

    
class Game:
    def __init__(self):
        self._suits = ['c', 'd', 'h', 's']
        self._movable = set([])
        self.matrix = []
        for _ in range(0, 4):
            self.matrix.append([None] * 13)

        for p, r in zip(range(0, 52), random.sample(range(0, 52), 52)):
            c = r % 13 + 1
            s = self._suits[int(r / 13)]
            i = int(p / 13)
            j = p % 13
            if c != 1:
                self.matrix[i][j] = (s, c)

        self._ui = UI(self)
                
        # This should go away
        # self.row = random.randint(0, 3)
        # self.col = random.randint(0, 12)
        # self.movable = set([])
        # self.select(self.row, self.col)
        self.refresh_movable()

    # None => None
    def refresh_movable(self):
        self._movable = set([])
        
        head = False
        for i in range(0, 4):
            if self.is_empty(i, 0):
                head = True

        if head:
            for i in range(0, 4):
                for j in range(0, 13):
                    if not self.is_empty(i, j) \
                       and self.matrix[i][j][1] == 2:
                        self._movable.add((i, j))

        prev = set([])
        for i in range(0, 4):
            for j in range(1, 13):
                if self.is_empty(i, j) and not self.is_empty(i, j-1):
                    if self.matrix[i][j-1][1] < 13:
                        prev.add((self.matrix[i][j-1][0],
                                  self.matrix[i][j-1][1] + 1))

        for i in range(0, 4):
            for j in range(0, 13):
                if not self.is_empty(i, j):
                    if self.matrix[i][j] in prev:
                        self._movable.add((i, j))

        self.ui.refresh()

    # None => None
    def move(self, i, j):
        print('Move', i, j)
        
    # int, int => bool
    def is_empty(self, i, j):
        return self.matrix[i][j] is None

    # int, int => (str, int)
    def get_card(self, i, j):
        return self.matrix[i][j]
    
    # None => {(int, int)}
    @property
    def movable(self):
        return self._movable

    # None => [str]
    @property
    def suits(self):
        return self._suits

    # None => UI
    @property
    def ui(self):
        return self._ui
    
# None => int
def main():
    win = Game()
    Gtk.main()
    
    return 0

if __name__ == '__main__':
    exit(main())

