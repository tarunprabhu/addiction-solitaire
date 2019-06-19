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

@unique
class Blocked(Enum):
    Clear = auto()
    New = auto()
    Quit = auto()

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
            ('title', 'bold', ''),
            ('win', 'white,bold', 'dark green'),
            ('lose', 'white,bold', 'dark red'),
            ('dialog', 'bold', ''),
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
                                      1, min_width = 2))
        rows = urwid.Pile(cols)
        self.board = urwid.Filler(rows)

        header = urwid.Text(('title', 'Addiction Solitaire'), align = 'center')

        lbl_time = urwid.Text(('bold', 'Time'))
        lbl_shuffles = urwid.Text(('bold', 'Shuffles'))
        lbl_moves = urwid.Text(('bold', 'Moves'))
        lbl_movable = urwid.Text(('bold', ''))

        self.lbl_time = urwid.Text('')
        self.lbl_shuffles = urwid.Text('')
        self.lbl_moves = urwid.Text('')
        self.lbl_movable = urwid.Text('')

        key_arrow = urwid.Text(('bold', 'Arrow\nkeys'))
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

        self.lbl_message = urwid.Text('', align = 'center')
        
        # footer = urwid.Pile(
        #     self.lbl_message,
        #     urwid.Columns(
        #         urwid.Pile([(1, lbl_time),
        #                     (1, lbl_shuffles),
        #                     (1, lbl_moves),
        #                     (1, lbl_movable)]),
        #         urwid.Pile([(1, self.lbl_time),
        #                     (1, self.lbl_shuffles),
        #                     (1, self.lbl_moves),
        #                     (1, self.lbl_movable)])))
        
        # footer = urwid.BoxAdapter(urwid.Frame(self.lbl_time, self.lbl_message),
        #                           'bottom')
        # footer = urwid.BoxAdapter(urwid.Frame(
        #     urwid.Filler(
        #         urwid.Pile(
        #     self.lbl_message), 'bottom')
        
        self.frame = urwid.Frame(self.board, header, self.lbl_message)

        self.blocked = Blocked.Clear
        
    # * => *
    def main(self):
        # fill = urwid.BoxAdapter(self.frame)
        loop = urwid.MainLoop(self.frame,
                              self.palette,
                              unhandled_input = self.action_key_press,
                              handle_mouse = False)
        loop.screen.set_terminal_properties(colors = 16)
        loop.set_alarm_in(5, self.tick, 0)
        loop.run()

    def tick(self, loop, secs):
        pass
        
    # * => *
    def quit(self):
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
            if self.blocked == Blocked.Clear:
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
                    if self.game.is_started():
                        self.blocked = Blocked.New
                        self.lbl_message.set_text(('bold',
                                                   'Really quit game [y/n]: '))
                    else:
                        self.action_new()
                elif key in ['esc']:
                    if self.game.is_started():
                        self.blocked = Blocked.Quit
                        self.lbl_message.set_text(('bold',
                                                   'Really quit game [y/n]: '))
                    else:
                        self.action_quit()
                elif key in ['u']:
                    self.action_undo()
                elif key in ['r']:
                    self.action_shuffle()
            else:
                if key in ['y']:
                    if self.blocked == Blocked.New:
                        self.action_new()
                    elif self.blocked == Blocked.Quit:
                        self.action_quit()
                elif key in ['n']:
                    self.blocked = Blocked.Clear
                    self.lbl_message.set_text('')
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
        self.lbl_shuffles.set_text(str(shuffles))

    # int => None
    def report_moves_changed(self, moves):
        self.lbl_moves.set_text(str(moves))
        
    # int => None
    def report_movable_changed(self, movable):
        self.lbl_movable.set_text('({} available)'.format(movable))

    # int => None
    def report_correct_changed(self, correct):
        pass
        
    # bool => None
    def report_game_over(self, win):
        if win:
            self.lbl_message.set_text(('win', ' You win! '))
        else:
            self.lbl_message.set_text(('lose', ' Game over '))

    # None => None
    def report_game_new(self):
        self.lbl_message.set_text('')
    
