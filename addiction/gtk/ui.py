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

import math
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

        self.timer = None
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
        self.lbl_time = self.builder.get_object('lbl_time')
        self.lbl_shuffles = self.builder.get_object('lbl_shuffles')
        self.lbl_moves = self.builder.get_object('lbl_moves')
        self.lbl_sequence = self.builder.get_object('lbl_sequence')
        self.lbl_status = self.builder.get_object('lbl_status')
        self.lbl_result = self.builder.get_object('lbl_result')
        self.img_result_1 = self.builder.get_object('img_result_1')
        self.img_result_2 = self.builder.get_object('img_result_2')

        self.mitm_move = self.builder.get_object('mitm_move')
        self.mitm_undo = self.builder.get_object('mitm_undo')
        self.mitm_shuffle = self.builder.get_object('mitm_shuffle')
        self.btn_undo = self.builder.get_object('btn_undo')
        self.btn_shuffle = self.builder.get_object('btn_shuffle')

        self.dlg_about = self.builder.get_object('dlg_about')
        self.dlg_quit = self.builder.get_object('dlg_quit')
        self.dlg_result = self.builder.get_object('dlg_result')
        
        self.win_main.show_all()
        for i in range(0, 4):
            for j in range(0, 13):
                drw = self.builder.get_object('drw_{}_{}'.format(i, j))
                drw.connect('button-press-event',
                            self.action_button_press,
                            self.game.points[i][j])
                drw.connect('draw', self.draw_card, self.game.points[i][j])

                self.board[i][j] = drw

        cards_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'cards')
        allocation = self.board[0][0].get_allocation()
        self.card_width = allocation.width - 2 * self.settings.border
        self.card_height = allocation.height - 2 * self.settings.border
        self.cards = dict()
        for s in Suit:
            self.cards[s] = dict()
            for c in Face:
                filename = os.path.join(cards_dir, s.dirname, c.filename)
                self.cards[s][c] = \
                    GdkPixbuf.new_from_file_at_scale(filename,
                                                     self.card_width,
                                                     self.card_height,
                                                     False)
        self.css_win = CSS('label',
                           {'font-weight': 'bold',
                            'color': 'green'}).get_provider()
        self.css_lose = CSS('label',
                            {'font-weight': 'bold',
                             'color': 'red'}).get_provider()
        self.css_stuck = CSS('label',
                             {'font-weight': 'bold',
                              'color': 'orange'}).get_provider()

    # None => None
    def main(self):
        Gtk.main()

    # None => None
    def quit(self):
        if self.timer:
            GLib.source_remove(self.timer)
            self.timer = None
        Gtk.main_quit()

    # * => None
    def action_about(self, *args):
        self.dlg_about.run()

    # * => None
    def action_new(self, *args):
        if self.game.is_started():
            response = self.dlg_quit.run()
            self.dlg_quit.hide()
            if response in [Gtk.ResponseType.YES]:
                self.game.do_game_new()
        else:
            self.game.do_game_new()

    # * => None
    def action_quit(self, *args):
        if self.game.is_started():
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

    # * => None
    def action_move(self, mitm_actions_move):
        if self.game.selected:
            self.game.do_move_card(self.game.selected)
        
    # Gtk.Window, Gdk.Event => bool
    def action_key_press(self, win_main, evt):
        key = evt.keyval
        self.game.dbg('Acquiring lock')
        with self.game.lock:
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
            elif key in [Gdk.KEY_Escape]:
                self.action_quit()
            elif key in [Gdk.KEY_n]:
                self.action_new()
            elif key in [Gdk.KEY_r]:
                self.action_shuffle()
            elif key in [Gdk.KEY_u]:
                self.action_undo()
        self.game.dbg('Released lock')
        return False
        
    # Gtk.EventBox, Gdk.Event, Point => bool
    def action_button_press(self, widget, evt, addr):
        button = evt.type
        with self.game.lock:
            if not self.game.is_empty(addr):
                if button == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                    if self.game.is_movable(addr):
                        self.game.do_move_card(addr)
                elif button == Gdk.EventType.BUTTON_PRESS:
                    if self.game.is_movable(addr):
                        self.game.do_select(addr)
        return False

    # Gtk.Widget, Cairo.Context, Point => bool
    def draw_card(self, drw, cr, addr):
        # float => float
        def radians(angle):
            return angle * math.pi / 180

        color = None
        if self.game.is_selected(addr):
            color = self.settings.color_selected
        elif self.game.is_movable(addr) and self.settings.highlight_movable:
            color = self.settings.color_movable
        elif self.game.is_correct(addr) and self.settings.highlight_correct:
            color = self.settings.color_correct
        else:
            color = self.settings.color_normal


        if not self.game.is_empty(addr):
            card = self.game.get_card(addr)
            Gdk.cairo_set_source_pixbuf(cr,
                                        self.cards[card.suit][card.face],
                                        self.settings.border,
                                        self.settings.border)
            cr.paint()

        x = 0.5 * self.settings.border
        y = 0.5 * self.settings.border
        w = self.card_width + self.settings.border
        h = self.card_height + self.settings.border
        r = self.settings.radius

        cr.new_sub_path()
        cr.arc(x + w - r, y + r, r, radians(-90), radians(0))
        cr.arc(x + w - r, y + h - r, r, radians(0), radians(90))
        cr.arc(x + r, y + h - r, r, radians(90), radians(180))
        cr.arc(x + r, y + r, r, radians(180), radians(270))
        cr.close_path()
        cr.set_source_rgba(color.red(float),
                           color.green(float),
                           color.blue(float),
                           color.alpha(float))
        cr.set_line_width(self.settings.border)
        cr.stroke()
        
    # Point, Card => None
    def report_cell_card_changed(self, addr, card):
        self.board[addr.row][addr.col].queue_draw()

    # Point, bool => None
    def report_cell_flags_changed(self, addr, flags):
        self.board[addr.row][addr.col].queue_draw()

    # bool => None
    def report_selection_changed(self, selected):
        self.mitm_move.set_sensitive(selected)
            
    # int => None
    def report_undo_changed(self, undos):
        self.mitm_undo.set_sensitive(undos)
        self.btn_undo.set_sensitive(undos)
        
    # int => None
    def report_shuffles_changed(self, shuffles):
        if self.settings.is_unlimited_shuffles():
            self.lbl_shuffles.set_text('Unlimited')
        else:
            self.lbl_shuffles.set_text('{} of {}'.format(shuffles,
                                                           self.settings.shuffles))
            self.mitm_shuffle.set_sensitive(shuffles < self.settings.shuffles)
            self.btn_shuffle.set_sensitive(shuffles < self.settings.shuffles)

    # int => None
    def report_moves_changed(self, moves):
        self.lbl_moves.set_text(str(moves))
                
    # int => None
    def report_movable_changed(self, movable):
        self.lbl_status.get_style_context().remove_provider(self.css_stuck)
        if not movable:
            self.lbl_status.get_style_context().add_provider(
                self.css_stuck, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.lbl_status.set_text('No moves possible')
        else:
            self.lbl_status.set_text('{} moves possible'.format(movable))

    # int => None
    def report_correct_changed(self, correct):
        self.lbl_sequence.set_text(str(correct))
            
    # bool => None
    def report_game_over(self, win):
        if self.timer:
            GLib.source_remove(self.timer)
            self.timer = None

        style_result = self.lbl_result.get_style_context()
        style_status = self.lbl_status.get_style_context()
        if win:
            self.img_result_1.set_from_icon_name('emblem-generic',
                                                 Gtk.IconSize.LARGE_TOOLBAR)
            self.img_result_2.set_from_icon_name('emblem-generic',
                                                 Gtk.IconSize.LARGE_TOOLBAR)
            self.lbl_result.set_text('You won')
            self.lbl_status.set_text('You won')
            style_result.add_provider(
                self.css_win, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            style_status.add_provider(
                self.css_win, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        else:
            self.img_result_1.set_from_icon_name('dialog-error',
                                                 Gtk.IconSize.LARGE_TOOLBAR)
            self.img_result_2.set_from_icon_name('dialog-error',
                                                 Gtk.IconSize.LARGE_TOOLBAR)
            self.lbl_result.set_text('You lost')
            self.lbl_status.set_text('You lost')
            style_result.add_provider(
                self.css_lose, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            style_status.add_provider(
                self.css_lose, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
        response = self.dlg_result.run()
        if response in [Gtk.ResponseType.YES]:
            self.game.do_game_new()
            self.dlg_result.hide()
        else:
            self.game.do_quit()
        
    # None => None
    def report_game_new(self):
        self.report_undo_changed(0)
        self.report_shuffles_changed(0)
        self.report_moves_changed(0)
        self.lbl_status.set_text('')
        self.lbl_status.get_style_context().remove_provider(self.css_win)
        self.lbl_status.get_style_context().remove_provider(self.css_lose)
        self.lbl_result.get_style_context().remove_provider(self.css_win)
        self.lbl_result.get_style_context().remove_provider(self.css_lose)
        self.lbl_time.set_text('00:00')
        self.timer = GLib.timeout_add_seconds(1, self.tick)

    # None => None
    def tick(self):
        ticks = self.game.ticks
        secs = ticks % 60
        mins = int(ticks / 60) % 60
        hrs = int(ticks / 3600)
        if hrs:
            self.lbl_time.set_text('{}:{:02}:{:02}'.format(hrs, mins, secs))
        else:
            self.lbl_time.set_text('{:02}:{:02}'.format(mins, secs))

        return True
