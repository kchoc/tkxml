import tkinter as tk
from tkinter import Widget
from typing import Optional

from .components import split_params
from .controller import Controller

class Frame(tk.Frame):
    def __init__(self, parent: Widget, parameters: dict):
        pack, config = split_params(parameters)
        super().__init__(parent, config)
        self.pack(pack)

class Canvas(tk.Canvas):
    def __init__(self, parent: Widget, parameters: dict):
        pack, config = split_params(parameters)
        super().__init__(parent, config)
        self.pack(pack)

class Label(tk.Label):
    def __init__(self, parent: Widget, parameters: dict, controller: Optional[Controller]):
        pack, config, exc = split_params(parameters, exclude=["textvariable"])

        if "textvariable" in exc:
            config["textvariable"] = controller.get(parameters["textvariable"])

        super().__init__(parent, config)
        self.pack(pack)

class Checkbutton(tk.Checkbutton):
    def __init__(self, parent: Widget, parameters: dict, controller: Optional[Controller]):
        pack, config, exc = split_params(parameters, exclude=["variable"])

        if "variable" in exc:
            config["variable"] = controller.get(parameters["variable"])

        super().__init__(parent, config)
        self.pack(pack)

class Radiobutton(tk.Radiobutton):
    def __init__(self, parent: Widget, parameters: dict, controller: Optional[Controller]):
        pack, config, exc = split_params(parameters, exclude=["variable"])

        if "variable" in exc:
            config["variable"] = controller.get(parameters["variable"])

        super().__init__(parent, config)
        self.pack(pack)

class Spinbox(tk.Spinbox):
    def __init__(self, parent: Widget, parameters: dict, controller: Optional[Controller]):
        pack, config, exc = split_params(parameters, exclude=["textvariable"])

        if "textvariable" in exc:
            config["textvariable"] = controller.get(parameters["textvariable"])

        super().__init__(parent, config)
        self.pack(pack)

class Button(tk.Button):
    def __init__(self, parent: Widget, parameters: dict, controller: Optional[Controller]):
        pack, config, exc = split_params(parameters, exclude=["command"])

        if "command" in exc:
            config["textvariable"] = controller.get(parameters["textvariable"])

        super().__init__(parent, config)
        self.pack(pack)
