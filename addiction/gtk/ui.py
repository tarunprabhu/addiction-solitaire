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
from gi.repository.GdkPixbuf import Pixbuf as GdkPixbuf

import os

from ..game_ui import GameUI
from ..types import Suit, Face, Direction, Point

class GameGtk(GameUI):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'game.glade')
    
    # Game
    def __init__(self, game):
        super().__init__(game)

        self.board = []
        for _ in range(0, 4):
            self.board.append([None] * 13)

        self.builder = Gtk.Builder.new()
        self.builder.add_objects_from_file(GameGtk.filename,
                                           ['win_main', 'dlg_about'])
        self.builder.connect_signals(self)

        self.win_main = self.builder.get_object('win_main')
        self.grd_board = self.builder.get_object('grd_board')
        self.dlg_about = self.builder.get_object('dlg_about')
        self.lbl_shuffles = self.builder.get_object('lbl_shuffles')
        self.lbl_movable = self.builder.get_object('lbl_movable')
        self.lbl_message = self.builder.get_object('lbl_message')
        for i in range(0, 4):
            for j in range(0, 13):
                suffix = '{}_{}'.format(i, j)
                evt = self.builder.get_object('evt_{}'.format(suffix))
                frm = self.builder.get_object('frm_{}'.format(suffix))
                evt.connect('button-press-event',
                            self.action_button_press,
                            Point(i, j))
                self.board[i][j] = frm
        self.win_main.show_all()

        card_width = self.board[0][0].get_allocation().width
        card_height = self.board[0][0].get_allocation().height
        self.cards = dict()
        for s in Suit:
            self.cards[s] = dict()
            for c in Face:
                filename = os.path.join('cards', s.dirname, c.filename)
                self.cards[s][c] = \
                    Gtk.Image.new_from_pixbuf(
                        GdkPixbuf.new_from_file_at_scale(filename,
                                                         card_width,
                                                         card_height,
                                                         False))
        self.fg = \
            self.lbl_message.get_style_context().get_color(Gtk.StateFlags.NORMAL)

    # None => None
    def main(self):
        Gtk.main()

    # None => None
    def quit(self):
        Gtk.main_quit()
        
    # * => None
    def action_about(self, *args):
        self.dlg_about.run()

    # * => None
    def action_new(self, *args):
        self.grd_board.show()
        self.game.do_game_new()

    # * => None
    def action_preferences(self, mitm_game_preferences):
        self.settings.ui.run_dialog()

    # * => None
    def action_quit(self, *args):
        self.game.do_quit()

    # * => None
    def action_shuffle(self, *args):
        if self.game.started:
            self.game.do_shuffle()

    # * => None
    def action_undo(self, *args):
        if self.game.started:
            self.game.do_undo()
    
    # Gtk.Window, Gdk.Event => bool
    def action_key_press(self, win_main, evt):
        if self.game.cursor:
            key = evt.keyval
            if key in [Gdk.KEY_Up, Gdk.KEY_KP_Up]:
                self.game.do_move_cursor(Direction.Up)
            elif key in [Gdk.KEY_Down, Gdk.KEY_KP_Down]:
                self.game.do_move_cursor(Direction.Down)
            elif key in [Gdk.KEY_Left, Gdk.KEY_KP_Left]:
                self.game.do_move_cursor(Direction.Left)
            elif key in [Gdk.KEY_Right, Gdk.KEY_KP_Down]:
                self.game.do_move_cursor(Direction.Right)
            elif key in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
                self.game.do_move_card(self.game.cursor)
            
        return False
        
    # Gtk.EventBox, Gdk.Event, Point => bool
    def action_button_press(self, widget, evt, addr):
        button = evt.type
        if not self.game.is_empty(addr):
            if button == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                if self.game.is_movable(addr):
                    self.game.do_move_card(addr)
            elif button == Gdk.EventType.BUTTON_PRESS:
                if self.game.is_movable(addr):
                    self.game.do_select(addr)
                
        return False
    
    # Point, Card => None
    def report_cell_card_changed(self, addr, card):
        child = self.get_frame(addr).get_child()
        if child:
            self.get_frame(addr).remove(child)
        if card:
            self.get_frame(addr).add(self.cards[card.suit][card.face])
            self.get_frame(addr).show_all()

    # Point, bool => None
    def report_cell_movable_changed(self, addr, movable):
        if movable and self.settings.highlight_movable:
            self.set_widget_css(self.get_frame(addr), self.get_css_movable())
        else:
            self.set_widget_css(self.get_frame(addr), self.get_css_normal())

    # Point, bool => None
    def report_cell_selected_changed(self, addr, selected):
        if selected:
            self.set_widget_css(self.get_frame(addr), self.get_css_cursor())
        elif self.game.is_movable(addr):
            self.set_widget_css(self.get_frame(addr), self.get_css_movable())
        else:
            self.set_widget_css(self.get_frame(addr), self.get_css_normal())
        self.lbl_message.set_text('')

    # int => None
    def report_shuffles_changed(self, shuffles):
        self.lbl_shuffles.set_text(str(shuffles))
        self.lbl_message.set_text('')

    # int => None
    def report_movable_changed(self, movable):
        self.lbl_movable.set_text(str(movable))
        self.lbl_message.set_text('')

    # None => None
    def report_movable_zero(self):
        self.lbl_message.set_text('No moves available. Press F5 to reshuffle')
            
    # bool => None
    def report_game_over(self, win):
        color = None
        text = None
        if win:
            color = Gdk.RGBA(0x33/255, 0xCC/255, 0x33/255, 1.0)
            text = 'You win!'
        else:
            color = Gdk.RGBA(0xCC/255, 0x33/255, 0x33/255, 1.0)
            text = 'Game over'

        css = []
        css.append('label {')
        css.append('  background-color: {};'.format(
            self.format_css_color(color)))
        css.append('  color: {};'.format(
            self.format_css_color(Gdk.RGBA(255, 255, 255, 1.0))))
        css.append('  font-weight: bold;')
        css.append('}')
        
        self.set_widget_css(self.lbl_message, '\n'.join(css))
        self.lbl_message.set_text(text)

    # None => None
    def report_game_new(self):
        css = []
        css.append('label {')
        css.append('  background-color: {};'.format(
            self.format_css_color(Gdk.RGBA(0, 0, 0, 0))))
        css.append('  color: {};'.format(self.format_css_color(self.fg)))
        css.append('  font-weight: normal;')
        css.append('}')

        self.set_widget_css(self.lbl_message, '\n'.join(css))
        self.lbl_shuffles.set_text(str(self.game.shuffles))
        self.lbl_message.set_text('')

    # None => None
    def report_undo_nothing(self):
        self.lbl_message.set_text('Nothing to undo')

    # None => None
    def report_move(self, src, dst):
        self.lbl_message.set_text('')

    # None => None
    def report_shuffle(self):
        self.lbl_message.set_text('')

    # Point => Gtk.Frame
    def get_frame(self, addr):
        return self.board[addr.row][addr.col]
        
    # Gdk.RGBA => str
    def format_css_color(self, color):
        return 'rgba({},{},{},{})'.format(
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255),
            color.alpha)
    
    # Gdk.RGBA => str
    def get_border_css(self, color):
        css = []
        css.append('frame {')
        css.append('  border-style: solid;')
        css.append('  border-radius: {}px;'.format(self.settings.radius))
        css.append('  border-width: {}px;'.format(self.settings.border))
        css.append('  border-color: {};'.format(self.format_css_color(color)))
        css.append('}')

        return '\n'.join(css)
    
    # None => str
    def get_css_cursor(self):
        return self.get_border_css(self.settings.color_cursor)

    # None => str
    def get_css_movable(self):
        if self.settings.highlight_movable:
            return self.get_border_css(self.settings.color_movable)
        else:
            return self.get_css_normal()

    # None => str
    def get_css_normal(self):
        return self.get_border_css(self.settings.color_normal)
        
    # Gtk.Widget, str => None
    def set_widget_css(self, widget, css):
        provider = Gtk.CssProvider.new()
        provider.load_from_data(css.encode('utf-8'))
        widget.get_style_context() \
              .add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
