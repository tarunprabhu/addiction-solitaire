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
            ('win', 'white,bold', 'dark green'),
            ('lose', 'white,bold', 'dark red'),
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
        self.footer = urwid.Text("Press 'n' to start new game", align='center')
        self.board = urwid.Filler(rows)
        self.frame = urwid.Frame(self.board, self.header, self.footer)

        self.blocked = Blocked.Clear
        self.msgs = []
        self.msg_default = '. '.join(['Arrow keys to change selection',
                                      '<Enter> to moves selected card',
                                      '<F5> to reshuffle'])
        
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

    # * => None
    def action_new(self):
        self.game.do_game_new()

    # * => None
    def action_quit(self):
        self.game.do_quit()
    
    # str => None
    def action_key_press(self, key):
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
                if self.game.started:
                    self.blocked = Blocked.New
                    self.msgs.append(self.footer.get_text()[0])
                    self.footer.set_text('Really quit game [y/n]: ')
                else:
                    self.action_new()
            elif key in ['q', 'Esc']:
                if self.game.started:
                    self.blocked = Blocked.Quit
                    self.msgs.append(self.footer.get_text()[0])
                    self.footer.set_text('Really quit game [y/n]: ')
                else:
                    self.action_quit()
            elif key in ['z', 'u']:
                self.action_undo()
            elif key in ['r', 'f5']:
                self.action_shuffle()
        else:
            if key in ['y']:
                if self.blocked == Blocked.New:
                    self.action_new()
                elif self.blocked == Blocked.Quit:
                    self.action_quit()
            elif key in ['n']:
                self.blocked = Blocked.Clear
                self.footer.set_text(('default', self.msgs.pop(-1)))

    # * => None
    def action_button_press(self, *args):
        pass
    
    # int => None
    def report_undo_changed(self, undos):
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
        self.footer.set_text(('default', self.msg_default))

    # int => None
    def report_movable_changed(self, movable):
        if movable:
            self.footer.set_text(('default', self.msg_default))

    # int => None
    def report_movable_zero(self):
        msg = []
        msg.append('No moves possible.')
        msg.append('<F5> to reshuffle')
        if self.settings.shuffles == self.settings.Unlimited:
            msg.append('(Unlimited shuffles)')
        elif self.game.shuffles == 1:
            msg.append('(1 shuffle remaining)')
        elif self.game.shuffles > 1:
            msg.append('({} shuffles remaining)'.format(self.game.shuffles))
        self.footer.set_text(('default', ' '.join(msg)))
            
    # bool => None
    def report_game_over(self, win):
        if win:
            self.footer.set_text(('win', ' You win! '))
        else:
            self.footer.set_text(('lose', ' Game over '))

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
    
