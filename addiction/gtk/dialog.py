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
from gi.repository import Gtk, Gdk, GObject

import os

from .util import as_color, as_rgba
from ..settings import Settings
from ..settings_ui import SettingsUI
from ..types import Color

class SettingsGtk(SettingsUI):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'game.glade')
    
    # Game
    def __init__(self, game):
        super().__init__(game)

        # Initializes preferences dialog. 
        self.builder = Gtk.Builder.new()
        self.builder.add_objects_from_file(SettingsGtk.filename,
                                           ['dlg_preferences',
                                            'adj_shuffle'])
        self.builder.connect_signals(self)

        self.chk_shuffles = self.builder.get_object('chk_shuffles')
        self.frm_shuffles = self.builder.get_object('frm_shuffles')
        self.spn_shuffles = self.builder.get_object('spn_shuffles')
        self.cbtn_selected = self.builder.get_object('cbtn_selected')
        self.chk_movable = self.builder.get_object('chk_movable')
        self.frm_movable = self.builder.get_object('frm_movable')
        self.cbtn_movable = self.builder.get_object('cbtn_movable')
        self.chk_correct = self.builder.get_object('chk_correct')
        self.cbtn_correct = self.builder.get_object('cbtn_correct')
        self.frm_correct = self.builder.get_object('frm_correct')
        self.dlg_preferences = self.builder.get_object('dlg_preferences')

        binding_flags = \
            GObject.BindingFlags.BIDIRECTIONAL \
            | GObject.BindingFlags.SYNC_CREATE
        self.chk_movable.bind_property('active', self.frm_movable, 'sensitive',
                                       binding_flags)
        self.chk_correct.bind_property('active', self.frm_correct, 'sensitive',
                                       binding_flags)
        self.chk_shuffles.bind_property('active', self.frm_shuffles, 'sensitive',
                                        binding_flags \
                                        | GObject.BindingFlags.INVERT_BOOLEAN)

        self.chk_shuffles.set_active(self.settings.shuffles == Settings.Unlimited)
        self.spn_shuffles.set_value(self.settings.shuffles)
        self.cbtn_selected.set_rgba(as_rgba(self.settings.color_selected))
        self.cbtn_movable.set_rgba(as_rgba(self.settings.color_movable))
        self.cbtn_correct.set_rgba(as_rgba(self.settings.color_correct))
        self.chk_movable.set_active(self.settings.highlight_movable)
        self.chk_correct.set_active(self.settings.highlight_correct)
        self.dlg_preferences.set_transient_for(self.game.ui.win_main)
        
    # None => None
    def run(self):
        response = self.dlg_preferences.run()
        if response == Gtk.ResponseType.OK:
            self.settings.write()
            if self.game.started:
                self.game.do_game_new()
        elif response == Gtk.ResponseType.CANCEL \
             or response == Gtk.ResponseType.DELETE_EVENT:
            self.settings.read()
        else:
            raise RuntimeError('Unknown response from preferences dialog')
        self.dlg_preferences.hide()
    
    # Gtk.ToggleButton => None
    def cb_chk_movable_toggled(self, chk_movable):
        self.settings.highlight_movable = chk_movable.get_active()

    # Gtk.ToggleButton => None
    def cb_chk_correct_toggled(self, chk_correct):
        self.settings.highlight_correct = chk_correct.get_active()
        
    # Gtk.ColorButton => None
    def cb_cbtn_selected_color_set(self, cbtn_selected):
        self.settings.color_selected = as_color(cbtn_selected.get_rgba())

    # Gtk.ColorButton => None
    def cb_cbtn_movable_color_set(self, cbtn_movable):
        self.settings.color_movable = as_color(cbtn_movable.get_rgba())

    # Gtk.ColorButton => None
    def cb_cbtn_correct_color_set(self, cbtn_correct):
        self.settings.color_correct = as_color(cbtn_correct.get_rgba())

    # Gtk.ToggleButton => None
    def cb_chk_shuffles_toggled(self, chk_shuffles):
        self.settings.shuffles = Settings.Unlimited
        
    # Gtk.SpinButton => None
    def cb_spn_shuffles_value_changed(self, spn_shuffles):
        self.settings.shuffles = spn_shuffles.get_value()
        
