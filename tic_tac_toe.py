import os 

from kivy.config import Config # ใช้เพื่อปรับเปลี่ยน attributes ของ Object

Config.set("graphics", "position", "custom") 
Config.set("graphics", "left", 610) 
Config.set("graphics", "top", 190) 
Config.set("graphics", "borderless", "1")  

import kivy
from kivy.app import App # เรียกใช้เพื่อสร้าง Kivy application
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    SlideTransition,
    SwapTransition,
) # เมื่อมีหลาย screen เรียกใช้เพื่อจัดการการเปลี่ยน screen ของ application
from kivy.uix.modalview import ModalView # เรียกใช้เพื่อสร้าง modal views
from kivy.core.window import Window # สร้าง Default window สำหรับ application
from kivy.uix.boxlayout import BoxLayout # เรียกใช้เพื่อสร้าง BoxLayout widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button # เรียกใช้เพื่อสร้างปุ่มกด
from kivy.uix.label import Label # เรียกใช้เพื่อสร้าง Label widget สำหรับใส่ข้อความ
from kivy.core.audio import SoundLoader 
from kivy.uix.popup import Popup
from kivy.clock import Clock
from copy import deepcopy
from enum import Enum
from math import inf
from functools import partial
from kivy.lang import Builder
from kivy.core.window import Window


Builder.load_string(
    """
<Cell@Button>:
    background_color: 102 / 255, 102 / 255, 102 / 255, 0.5
    font_size: 144
    background_normal: ''
    background_down: ''

<MainMenu@Screen>:
    name: 'home'
    canvas:
        Color:
            rgba: 0, 153 / 255, 102 / 255, 0.7
        Rectangle:
            size: root.size
            pos: root.pos
    Label:
        size_hint: None, None
        text: "[color=075951]Welcome to my Tic-Tac-Toe game![/color]\\n\\n           [color=2040a3]Let's have some FUN[/color] [color=b79a00]:)[/color]"
        markup: True
        bold: True
        #color: 0, 0, 0, 1
        font_size: 43
        size: self.texture_size
        pos: ((root.width / 2) - (self.width/ 2)), ((root.height / 2) - (self.height / 2)) + 100

    GridLayout:
        size_hint: None, None
        size: root.width * 0.9, 100
        pos: ((root.width / 2) - (self.width/ 2)), 175
        spacing: 10
        cols: 3
        
        Button:
            text: 'Two Players'
            background_normal: ""
            background_color: 0,61/255,153/255, 1
            font_size: 35
            markup: True
            bold: True
            color: 1, 1, 1, 1
            outline_color: (0, 0, 0)
            outline_width: 4
            on_release: app.root.current = 'mp'
        
        Button:
            text: 'One Player'
            background_normal: ""
            background_color: 0,61/255,153/255, 1
            font_size: 35
            markup: True
            bold: True
            color: 1, 1, 1, 1
            outline_color: (0, 0, 0)
            outline_width: 4
            #color: 0, 153 / 255, 102 / 255, 0.7
            on_release: app.root.current = 'sp'
        
        Button:
            text: 'Exit'
            background_normal: ""
            background_color: 0,61/255,153/255, 1
            font_size: 35
            markup: True
            bold: True
            color: 1, 1, 1, 1
            outline_color: (0, 0, 0)
            outline_width: 4
            on_release: quit()

"""
)

class MainMenu(Screen):
    pass


class PlayMenu(Screen):
    pass

class Player(Enum):
    COMPUTER = "O"
    HUMAN = "X"
    EMPTY = ""

class SimpleBoard:

    MAX_SCORE = 10000

    def __init__(self, board):
        self.__board = [[button.text for button in row] for row in board]

    def __getitem__(self, index):
        return self.__board[index]

    def __len__(self):
        return len(self.__board)

    def __iter__(self):
        return iter(self.__board)

    def is_full(self):
        return not any(
            [symbol == Player.EMPTY.value for row in self.__board for symbol in row]
        )

    def has_won(self):
        return abs(evaluate(self)) == SimpleBoard.MAX_SCORE

def evaluate(board):
    """
    :param board:   The board to evaluate
    :return:        :board:'s score based on the number of 2 in a rows
    """ 
    lines = check_rows(board) + check_cols(board) + check_diags(board)
    two_in_row = [0, 0]
    for line in lines:
        for i in range(len(line)):
            if line[i] == len(board):
                return SimpleBoard.MAX_SCORE * (-1 if i == 1 else 1)
            if line[i] == len(board) - 1 and line[1 - i] == 0:
                two_in_row[i] += 1
    comp_score = 10 * two_in_row[0]
    player_score = 1.5 * 10 * two_in_row[1]
    return comp_score - player_score

def check_rows(board):
    """
    :param board:   The game board or a list of rows
    :return:        A list containing how many of each symbol is in each row in :board:
    """
    out = []
    for row in board:
        out.append((row.count(Player.COMPUTER.value), row.count(Player.HUMAN.value)))
    return out

def check_cols(board):
    """
    :param board:   The game board
    :return:        A list containing how many of each symbol is in each column in :board:
    """
    transpose = [[row[i] for row in board] for i in range(len(board))]
    return check_rows(transpose)

class Board(GridLayout):
    LENGTH = 3
    DIFFICULTY = {
        "baby": 0,
        "easy": 2,
        "medium": 4,
        "hard": 6,
        "impossible": LENGTH ** 2,
    }

    def __init__(self, **kwargs):
        super().__init__()

        self.cols = self.rows = Board.LENGTH
        self.spacing = 2, 2
        self.click_sound = SoundLoader.load(os.path.join("assets", "click.wav"))
        self.game_start = SoundLoader.load(os.path.join("assets", "app_start.wav"))
        self.new_game_starting = SoundLoader.load(os.path.join("assets", "start.wav"))
        self.win_game = SoundLoader.load(os.path.join("assets", "win.mp3"))
        self.lose_game = SoundLoader.load(os.path.join("assets", "lose.wav"))

        self.first_player = self.current_player = kwargs.get(
            "first_player", Player.HUMAN
        )
        self.game_mode = kwargs.get("game_mode", GameMode.SINGLE_PLAYER)
        self.depth = Board.DIFFICULTY[kwargs.get("difficulty")]
        self.button_list = [
            [Cell() for _ in range(Board.LENGTH)] for _ in range(Board.LENGTH)
        ]
        self.popup = None
        if self.game_start:
            self.game_start.play()
        self.init_buttons()
        self.first_move()

    def init_buttons(self, reset=False):

        if self.new_game_starting:  
            self.new_game_starting.play()  

        board = BoxLayout(orientation="vertical")
        grid = GridLayout(cols=3, rows=3, spacing=2)
        for row in self.button_list:
            for button in row:
                button.bind(on_release=self.on_click)
                if reset:
                    button.text = ""
                    button.background_color = 102 / 255, 102 / 255, 102 / 255, 0.5
                else:
                    grid.add_widget(button)

        grid.pos_hint = {"x": 0.003, "y": 0}

def exitPopup(self, obj):  # The exit popup and its buttons
        self.box_popup = BoxLayout(
            orientation="horizontal"
        )  # Create a box layout fot the exit popup

        self.popup_exit = Popup(
            title="Confirmation",
            title_align="justify",
            title_size=30,
            content=self.box_popup,
            size_hint=(0.5, 0.4),
            auto_dismiss=True,
        )

        # Add for it text and design and reposition it
        self.box_popup.add_widget(
            Label(
                text="                               Are you sure you want to exit?",
                font_size=22,
                pos_hint={"x": 0, "y": 0.1},
            )
        )

        self.box_popup.add_widget(
            Button(
                text="Yes",
                on_release=self.bye,
                size_hint=(0.45, 0.2),
                background_color=(1, 0, 0, 1),
            )
        )

        self.box_popup.add_widget(
            Button(
                text="No",
                on_press=lambda *args: self.popup_exit.dismiss(),
                size_hint=(0.45, 0.2),
                background_color=(0.2, 0.8, 0.4, 1),
            )
        )

        self.popup_exit.open()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=kwargs["name"])
        board = BoxLayout(orientation="vertical")

        self.grid = Board(
            game_mode=kwargs.get("game_mode", GameMode.SINGLE_PLAYER),
            first_player=kwargs.get("first_player", Player.HUMAN),
            difficulty=kwargs.get("difficulty", "hard"),
        )

        board.add_widget(self.grid)
        self.add_widget(board)