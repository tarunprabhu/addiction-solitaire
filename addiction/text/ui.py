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

import urwid
from enum import Enum, unique, auto

from ..game_ui import GameUI
from ..settings import Settings
from ..types import Suit, Direction, CellFlags


class Cell:
    # Game, int, int
    def __init__(self, game, row, col):
        self.game = game
        self.row = row
        self.col = col
        self.card = None

        self.text = urwid.Text('  ', align = 'center')
        self.attr_text = urwid.AttrMap(self.text, None)

        self.box = urwid.LineBox(self.attr_text)
        self.attr_box = urwid.AttrMap(self.box, None)

        self.contents = self.attr_box

    # CellFlags => None
    def get_card_attr(self, flags):
        attrname = ['card_']
        if self.card:
            if flags & CellFlags.Selected:
                attrname.append('selected_')
            elif flags & CellFlags.Movable:
                attrname.append('movable_')

            if self.card.is_black():
                attrname.append('black')
            else:
                attrname.append('red')
        else:
            attrname.append('empty')

        return ''.join(attrname)
        
    # Card => None
    def set_card(self, card):
        self.card = card
        if card:
            self.text.set_text(str(card))
        else:
            self.text.set_text('  ')

    # None => None
    def set_movable(self):
        if self.game.settings.highlight_movable:
            self.attr_box.set_attr_map({None: 'box_movable'})
        self.text.set_text((self.get_card_attr(CellFlags.Movable),
                            str(self.card)))

    # None => None
    def set_selected(self):
        self.attr_box.set_attr_map({None: 'box_selected'})
        self.text.set_text((self.get_card_attr(CellFlags.Selected),
                            str(self.card)))

    # None => None
    def set_correct(self):
        if self.game.settings.highlight_correct:
            self.attr_box.set_attr_map({None: 'box_correct'})
        self.text.set_text((self.get_card_attr(CellFlags.Correct),
                            str(self.card)))

    # None => None
    def set_normal(self):
        self.attr_box.set_attr_map({None: 'box_normal'})
        if self.card:
            self.text.set_text((self.get_card_attr(CellFlags.Normal),
                                str(self.card)))
            

class GameText(GameUI):
    # Game
    def __init__(self, game):
        super().__init__(game)

        self.palette = [
            ('default', '', ''),
            ('bold', 'bold', ''),
            ('win', 'white,bold', 'dark green'),
            ('lose', 'white,bold', 'dark red'),
            ('stuck', 'brown,bold', ''),
            ('card_empty', '', ''),
            ('card_red', 'light red,bold', ''),
            ('card_black', 'bold', ''),
            ('card_selected_red', 'light red,bold,italics,underline', ''),
            ('card_selected_black', 'bold,italics,underline', ''),
            ('card_movable_red', 'light red,bold,italics', ''),
            ('card_movable_black', 'bold,italics', ''),
            ('box_movable', 'dark blue', ''),
            ('box_selected', 'yellow', ''),
            ('box_correct', 'light green', ''),
            ('box_normal', 'light gray', '')]
        
        self.cells = []
        for i in range(0, 4):
            self.cells.append([])
            for j in range(0, 13):
                self.cells[i].append(Cell(self.game, i, j))
        cols = []
        for i in range(0, 4):
            cols.append(urwid.Columns([cell.contents for cell in self.cells[i]],
                                      dividechars = 1,
                                      min_width = 2))
        rows = urwid.Pile(cols)
        self.board = urwid.Filler(rows)

        header = urwid.Text(('bold', 'Addiction Solitaire'), align = 'center')

        lbl_time = urwid.Text(('bold', ' Time'))
        lbl_shuffles = urwid.Text(('bold', ' Shuffles'))
        lbl_moves = urwid.Text(('bold', 'Moves'), align = 'right')
        lbl_correct = urwid.Text(('bold', 'Sequence'), align = 'right')

        self.lbl_time = urwid.Text('')
        self.lbl_shuffles = urwid.Text('')
        self.lbl_moves = urwid.Text('')
        self.lbl_correct = urwid.Text('')

        self.lbl_message = urwid.Text('', align = 'center')

        status = urwid.Columns(
            [(9, urwid.Pile([lbl_time, lbl_shuffles])),
             (10, urwid.Pile([self.lbl_time, self.lbl_shuffles])),
             self.lbl_message,
             (14, urwid.Pile([lbl_moves, lbl_correct])),
             (5, urwid.Pile([self.lbl_moves, self.lbl_correct]))
            ],
            dividechars = 2)
        
        key_arrow = urwid.Text(('bold', '<Arrow keys>'))
        key_enter = urwid.Text(('bold', '<Enter>'))
        
        key_arrow_do = urwid.Text('Change\nselection')
        key_enter_do = urwid.Text('Move\nselected')
        
        key_shuffle = urwid.Text(('bold', 'r'))
        key_undo = urwid.Text(('bold', 'u'))
        key_new = urwid.Text(('bold', 'n'))
        key_quit = urwid.Text(('bold', '<Esc>'))
        
        key_shuffle_do = urwid.Text('Shuffle')
        key_undo_do = urwid.Text('Undo')
        key_new_do = urwid.Text('New game')
        key_quit_do = urwid.Text('Quit game')
        
        helpbox = urwid.LineBox(urwid.Columns(
            [\
             (12, urwid.Pile([key_arrow])),
             urwid.Pile([key_arrow_do]),
             (7, urwid.Pile([key_enter])),
             urwid.Pile([key_enter_do]),
             (1, urwid.Pile([key_shuffle, key_undo])),
             urwid.Pile([key_shuffle_do, key_undo_do]),
             (5, urwid.Pile([key_new, key_quit])),
             urwid.Pile([key_new_do, key_quit_do])\
            ],
            dividechars = 2))
        
        footer = urwid.Pile(
            [status,
             helpbox])

        self.frame = urwid.Frame(self.board, header, footer)
        self.loop = None
        self.timer = None
        
    # * => *
    def main(self):
        self.loop = urwid.MainLoop(self.frame,
                                   self.palette,
                                   unhandled_input = self.action_key_press,
                                   handle_mouse = False)
        self.loop.screen.set_terminal_properties(colors = 16)
        self.loop.run()

    # urwid.MainLoop, * => None
    def tick(self, loop, data = None):
        ticks = self.game.ticks
        secs = ticks % 60
        mins = int((ticks / 60)) % 60
        hrs = int(ticks / 3600)
        if hrs:
            self.lbl_time.set_text('{}:{:02}:{:02}'.format(hrs, mins, secs))
        else:
            self.lbl_time.set_text('{:02}:{:02}'.format(mins, secs))

        self.timer = self.loop.set_alarm_in(1, self.tick)
        
    # * => *
    def quit(self):
        if self.timer:
            self.loop.remove_alarm(self.timer)
            timer = None
        raise urwid.ExitMainLoop()
    
    # * => None
    def action_about(self, *args):
        pass

    # * => None
    def action_preferences(self, mitm_game_preferences):
        pass

    # * => None
    def action_new(self):
        self.game.do_game_new()

    # * => None
    def action_quit(self):
        self.game.do_quit()
    
    # str => None
    def action_key_press(self, key):
        with self.game.lock:
            if key in ['up']:
                if self.game.selected:
                    self.game.do_move_selected(Direction.Up)
            elif key in ['down']:
                if self.game.selected:
                    self.game.do_move_selected(Direction.Down)
            elif key in ['left']:
                if self.game.selected:
                    self.game.do_move_selected(Direction.Left)
            elif key in ['right']:
                if self.game.selected:
                    self.game.do_move_selected(Direction.Right)
            elif key in ['enter']:
                if self.game.selected:
                    self.game.do_move_card(self.game.selected)
            elif key in ['n']:
                self.action_new()
            elif key in ['esc']:
                self.action_quit()
            elif key in ['u']:
                self.action_undo()
            elif key in ['r']:
                self.action_shuffle()
        return True

    # * => None
    def action_button_press(self, *args):
        pass
    
    # int => None
    def report_undo_changed(self, undos):
        pass

    # Point, Card => None
    def report_cell_card_changed(self, addr, card):
        self.cells[addr.row][addr.col].set_card(card)

    # Point, Flags => None
    def report_cell_flags_changed(self, addr, flags):
        cell = self.cells[addr.row][addr.col]
        if self.game.is_selected(addr):
            cell.set_selected()
        elif self.game.is_movable(addr):
            cell.set_movable()
        elif self.game.is_correct(addr):
            cell.set_correct()
        else:
            cell.set_normal()

    # bool => None
    def report_selection_changed(self, selected):
        pass
            
    # int => None
    def report_shuffles_changed(self, shuffles):
        if self.settings.is_unlimited_shuffles():
            self.lbl_shuffles.set_text('Unlimited')
        else:
            self.lbl_shuffles.set_text('{} of {}'.format(shuffles,
                                                         self.settings.shuffles))

    # int => None
    def report_moves_changed(self, moves):
        self.lbl_moves.set_text('{} '.format(moves))
        
    # int => None
    def report_movable_changed(self, movable):
        if movable:
            self.lbl_message.set_text('{} moves possible'.format(movable))
        else:
            self.lbl_message.set_text(('stuck', 'No moves possible'))

    # int => None
    def report_correct_changed(self, correct):
        self.lbl_correct.set_text('{} '.format(correct))
        
    # bool => None
    def report_game_over(self, win):
        if self.timer:
            self.loop.remove_alarm(self.timer)
            self.timer = None
            
        if win:
            self.lbl_message.set_text(('win', ' You win! '))
        else:
            self.lbl_message.set_text(('lose', ' Game over '))

    # None => None
    def report_game_new(self):
        self.report_moves_changed(0)
        self.report_shuffles_changed(0)
        self.tick(self.loop)
