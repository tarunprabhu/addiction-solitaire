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

from .css import CSS
from .dialog import SettingsGtk
from .util import as_rgba, as_color
from ..game_ui import GameUI
from ..settings import Settings
from ..types import Suit, Face, Direction, Point, Color
        

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
                                           ['win_main',
                                            'dlg_about',
                                            'dlg_quit',
                                            'dlg_result'])
        self.builder.connect_signals(self)

        self.win_main = self.builder.get_object('win_main')
        self.grd_board = self.builder.get_object('grd_board')
        self.dlg_about = self.builder.get_object('dlg_about')
        self.dlg_quit = self.builder.get_object('dlg_quit')
        self.dlg_result = self.builder.get_object('dlg_result')
        self.lbl_time = self.builder.get_object('lbl_time')
        self.lbl_moves = self.builder.get_object('lbl_moves')
        self.lbl_shuffles = self.builder.get_object('lbl_shuffles')
        self.lbl_movable = self.builder.get_object('lbl_movable')
        self.mitm_undo = self.builder.get_object('mitm_undo')
        self.mitm_shuffle = self.builder.get_object('mitm_shuffle')
        self.btn_undo = self.builder.get_object('btn_undo')
        self.btn_shuffle = self.builder.get_object('btn_shuffle')
        self.lbl_result = self.builder.get_object('lbl_result')
        self.grd_sidebar = self.builder.get_object('grd_sidebar')
        self.grd_buttons = self.builder.get_object('grd_buttons')

        self.win_main.show_all()
        for i in range(0, 4):
            for j in range(0, 13):
                evt = self.builder.get_object('evt_{}_{}'.format(i, j))
                frm = self.builder.get_object('frm_{}_{}'.format(i, j))
                evt.connect('button-press-event',
                            self.action_button_press,
                            self.game.points[i][j])
                self.board[i][j] = frm

        cards_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'cards')
        card_width = self.board[0][0].get_allocation().width
        card_height = self.board[0][0].get_allocation().height
        self.cards = dict()
        for s in Suit:
            self.cards[s] = dict()
            for c in Face:
                filename = os.path.join(cards_dir, s.dirname, c.filename)
                self.cards[s][c] = \
                    Gtk.Image.new_from_pixbuf(
                        GdkPixbuf.new_from_file_at_scale(filename,
                                                         card_width,
                                                         card_height,
                                                         False))

        self.css_border_normal = None
        self.css_border_selected = None
        self.css_border_movable = None
        self.css_border_correct = None
        self.report_update_settings()
                
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
        if self.game.started:
            response = self.dlg_quit.run()
            self.dlg_quit.hide()
            if response in [Gtk.ResponseType.YES]:
                self.game.do_game_new()
        else:
            self.game.do_game_new()

    # * => None
    def action_quit(self, *args):
        if self.game.started:
            response = self.dlg_quit.run()
            self.dlg_quit.hide()
            if response in [Gtk.ResponseType.YES]:
                self.game.do_quit()
        else:
            self.game.do_quit()

    # Gtk.Window => None
    def action_force_quit(self, win_main):
        self.game.do_quit()
            
    # * => None
    def action_preferences(self, mitm_game_preferences):
        SettingsGtk(self.game).run()

    # Gtk.Window, Gdk.Event => bool
    def action_key_press(self, win_main, evt):
        key = evt.keyval
        if key in [Gdk.KEY_Up, Gdk.KEY_KP_Up]:
            if self.game.selected:
                self.game.do_move_selected(Direction.Up)
        elif key in [Gdk.KEY_Down, Gdk.KEY_KP_Down]:
            if self.game.selected:
                self.game.do_move_selected(Direction.Down)
        elif key in [Gdk.KEY_Left, Gdk.KEY_KP_Left]:
            if self.game.selected:
                self.game.do_move_selected(Direction.Left)
        elif key in [Gdk.KEY_Right, Gdk.KEY_KP_Down]:
            if self.game.selected:
                self.game.do_move_selected(Direction.Right)
        elif key in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            if self.game.selected:
                self.game.do_move_card(self.game.selected)
        elif key in [Gdk.KEY_Escape]:
            self.action_quit()
        elif key in [Gdk.KEY_n]:
            self.action_new()
        elif key in [Gdk.KEY_r]:
            self.action_shuffle()
        elif key in [Gdk.KEY_u]:
            self.action_undo()
            
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

    # None => None
    def report_update_settings(self):
        self.grd_sidebar.set_visible(self.settings.show_sidebar)
        self.grd_buttons.set_visible(self.settings.show_buttons)

        self.css_border_normal = self.get_border_css(self.settings.color_normal)
        self.css_border_movable = self.get_border_css(self.settings.color_movable)
        self.css_border_selected = self.get_border_css(self.settings.color_selected)
        self.css_border_correct = self.get_border_css(self.settings.color_correct)
    
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
        if movable:
            self.set_border_style(self.get_frame(addr), self.get_css_movable())
        elif self.game.is_correct(addr):
            self.set_border_style(self.get_frame(addr), self.get_css_correct())
        else:
            self.set_border_style(self.get_frame(addr), self.get_css_normal())

    # Point, bool => None
    def report_cell_selected_changed(self, addr, selected):
        if selected:
            self.set_border_style(self.get_frame(addr), self.get_css_selected())
        elif self.game.is_movable(addr):
            self.set_border_style(self.get_frame(addr), self.get_css_movable())
        elif self.game.is_correct(addr):
            self.set_border_style(self.get_frame(addr), self.get_css_correct())
        else:
            self.set_border_style(self.get_frame(addr), self.get_css_normal())

    # Point, bool => None
    def report_cell_correct_changed(self, addr, correct):
        if correct:
            self.set_border_style(self.get_frame(addr), self.get_css_correct())
        elif self.game.is_selected(addr):
            self.set_border_style(self.get_frame(addr), self.get_css_selected())
        elif self.game.is_movable(addr):
            self.set_border_style(self.get_frame(addr), self.get_css_movable())
        else:
            self.set_border_style(self.get_frame(addr), self.get_css_normal())

    # int, int, int => None
    def report_time_changed(self, hrs, mins, secs):
        components = []
        if hrs:
            components.append(str(hrs))
        components.append('{:02}'.format(mins))
        components.append('{:02}'.format(secs))
        self.lbl_time.set_text(':'.join(components))
            
    # int => None
    def report_undo_changed(self, undos):
        self.mitm_undo.set_sensitive(undos)
        self.btn_undo.set_sensitive(undos)
        
    # int => None
    def report_shuffles_changed(self, shuffles):
        if self.settings.is_unlimited_shuffles():
            self.lbl_shuffles.set_text('{} (Unlimited)'.format(shuffles))
        else:
            self.lbl_shuffles.set_text('{} (of {})'.format(shuffles,
                                                           self.settings.shuffles))
            self.mitm_shuffle.set_sensitive(shuffles < self.settings.shuffles)
            self.btn_shuffle.set_sensitive(shuffles < self.settings.shuffles)

    # int => None
    def report_moves_changed(self, moves):
        self.lbl_moves.set_text(str(moves))
                
    # int => None
    def report_movable_changed(self, movable):
        self.lbl_moves.set_text(str(self.game.moves))
        self.lbl_movable.set_text('({} available)'.format(movable))
            
    # bool => None
    def report_game_over(self, win):
        if win:
            self.lbl_result.set_text('You win!')
        else:
            self.lbl_result.set_text('Game over!')
        response = self.dlg_result.run()
        if response in [Gtk.ResponseType.YES]:
            self.game.do_game_new()
            self.dlg_result.hide()
        else:
            self.game.do_quit()
        
    # None => None
    def report_game_new(self):
        self.report_undo_changed(0)
        self.report_moves_changed(0)
        self.report_shuffles_changed(0)
        self.report_time_changed(0, 0, 0)

    # Point => Gtk.Frame
    def get_frame(self, addr):
        return self.board[addr.row][addr.col]
    
    # Color => Gtk.CssProvider
    def get_border_css(self, color):
        return CSS('frame',
                   { 'border-style': 'solid',
                     'border-radius': (self.settings.radius, 'px'),
                     'border-width': (self.settings.border, 'px'),
                     'border-color': color}).get_provider()
    
    # None => str
    def get_css_selected(self):
        return self.css_border_selected 

    # None => str
    def get_css_movable(self):
        if self.settings.highlight_movable:
            return self.css_border_movable
        else:
            return self.css_border_normal

    # None => str
    def get_css_correct(self):
        if self.settings.highlight_correct:
            return self.css_border_correct
        else:
            return self.css_border_normal
        
    # None => str
    def get_css_normal(self):
        return self.css_border_normal
        
    # Gtk.Widget, Gtk.CssProvider => None
    def set_border_style(self, widget, css):
        style = widget.get_style_context()

        style.remove_provider(self.css_border_normal)
        style.remove_provider(self.css_border_selected)
        style.remove_provider(self.css_border_movable)
        style.remove_provider(self.css_border_correct)

        style.add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
