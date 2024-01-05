import os

from kivy.config import Config

Config.set("graphics", "position", "custom")  
Config.set("graphics", "left", 610)  
Config.set("graphics", "top", 190)
Config.set("graphics", "borderless", "1")  

import kivy
from kivy.app import App
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    SlideTransition,
    SwapTransition,
)
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
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


)

class Board(GridLayout):
    LENGTH = 3
    # Default difficult level is "hard"
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

        if self.new_game_starting:  # If the sound of new game is exist
            self.new_game_starting.play()  # So, play it

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
