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

        self.text = urwid.Text('  ')
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
        # self.attr_text.set_attr_map({ None: ''.join(attrname) })
        
    # Card => None
    def set_card(self, card):
        self.card = card
        if card:
            # self.set_card_attr(CellFlags.Normal)
            self.text.set_text(str(card))
        else:
            self.text.set_text('  ')

    # None => None
    def set_movable(self):
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
            ('card_empty', '', ''),
            ('card_red', 'light red', ''),
            ('card_black', '', ''),
            ('card_selected_red', 'light red,bold', ''),
            ('card_selected_black', 'bold', ''),
            ('card_movable_red', 'light red,italics', ''),
            ('card_movable_black', 'italics', ''),
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

        self.header = urwid.Text('Addiction Solitaire', align='center')
        self.footer = urwid.Text("Press 'n' to start new game")
        self.board = urwid.Filler(rows)
        self.frame = urwid.Frame(self.board, self.header, self.footer)
        
    # * => *
    def main(self):
        fill = urwid.BoxAdapter(self.frame, 'top')
        loop = urwid.MainLoop(self.frame,
                              self.palette,
                              unhandled_input = self.action_key_press)
        loop.screen.set_terminal_properties(colors = 16)
        loop.run()

    # * => *
    def quit(self):
        raise urwid.ExitMainLoop()
    
    # * => None
    def action_about(self, *args):
        pass

    # * => None
    def action_preferences(self, mitm_game_preferences):
        pass

    # str => None
    def action_key_press(self, key):
        if key in ['up']:
            self.game.do_move_selected(Direction.Up)
        elif key in ['down']:
            self.game.do_move_selected(Direction.Down)
        elif key in ['left']:
            self.game.do_move_selected(Direction.Left)
        elif key in ['right']:
            self.game.do_move_selected(Direction.Right)
        elif key in ['enter']:
            if self.game.selected:
                self.game.do_move_card(self.game.selected)
        elif key in ['n']:
            self.action_new()
        elif key in ['q', 'Esc']:
            self.action_quit()
        elif key in ['z', 'u']:
            self.action_undo()
        elif key in ['r', 'f5']:
            self.action_shuffle()

    # * => None
    def action_button_press(self, *args):
        pass

    # Point, Card => None
    def report_cell_card_changed(self, addr, card):
        self.cells[addr.row][addr.col].set_card(card)

    # Point, bool => None
    def report_cell_movable_changed(self, addr, movable):
        cell = self.cells[addr.row][addr.col]
        if movable:
            cell.set_movable()
        elif self.game.is_correct(addr):
            cell.set_correct()
        else:
            cell.set_normal()

    # Point, bool => None
    def report_cell_correct_changed(self, addr, correct):
        cell = self.cells[addr.row][addr.col]
        if correct:
            cell.set_correct()
        elif self.game.is_selected(addr):
            cell.set_selected()
        elif self.game.is_movable(addr):
            cell.set_movable()
        else:
            cell.set_normal()
        
    # Point, bool => None
    def report_cell_selected_changed(self, addr, selected):
        cell = self.cells[addr.row][addr.col]
        if selected:
            cell.set_selected()
        elif self.game.is_movable(addr):
            cell.set_movable()
        elif self.game.is_correct(addr):
            cell.set_correct()
        else:
            cell.set_normal()

    # int => None
    def report_shuffles_changed(self, shuffles):
        if shuffles != Settings.Unlimited:
            self.footer.set_text('Shuffles remaining: {}'.format(shuffles))
        else:
            self.footer.set_text('Shuffles remaining: Unlimited')

    # int => None
    def report_movable_changed(self, movable):
        if movable:
            self.footer.set_text('Use arrow keys to move cursor. '
                                 'Press <Enter> to move selected card')

    # int => None
    def report_movable_zero(self):
        self.footer.set_text('No moves remaining. '
                             'Press <F5> to reshuffle')
            
    # bool => None
    def report_game_over(self, win):
        if win:
            self.footer.set_text('You win!')
        else:
            self.footer.set_text('Game over')

    # None => None
    def report_game_new(self):
        pass

    # None => None
    def report_undo_nothing(self):
        self.footer.set_text('Nothing to undo')

    # None => None
    def report_move(self, src, dst):
        pass

    # None => None
    def report_shuffle(self):
        pass
    
