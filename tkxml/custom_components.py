import tkinter as tk
from tkinter import ttk
from typing import Literal

from .utils import MissingAttributeException, MissingControllerException
from .widget_mixin import WidgetMixin

def remove_params(params: dict[str, str], keys: list) -> dict[str, str]:
    """
    Removes parameters which are present in the keys list

    Parameters:
        params (dict): The parameters from the xml element
        keys (list): The keys to exclude

    Returns:
        dict: The parameters without the excluded keys
    """
    return dict((key, item) for key, item in params.items() if key not in keys)

def create_widget(init):
    def widget_init(self: WidgetMixin, parent, params: dict[str, str], 
                    layout_manager: Literal["pack", "grid", "place"], controller):
        WidgetMixin.__init__(self, parent, params, layout_manager, controller)
        init(self)
        self.activate()
    return widget_init

class Frame(tk.Frame, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Frame.__init__(self, self.parent, **self.config_parameters)

class Button(tk.Button, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Button.__init__(self, self.parent, **self.config_parameters)

class Label(tk.Label, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Label.__init__(self, self.parent, **self.config_parameters)

class Entry(tk.Entry, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Entry.__init__(self, self.parent, **self.config_parameters)

class Checkbutton(tk.Checkbutton, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Checkbutton.__init__(self, self.parent, **self.config_parameters)

class Radiobutton(tk.Radiobutton, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Radiobutton.__init__(self, self.parent, **self.config_parameters)

class Combobox(ttk.Combobox, WidgetMixin):
    @create_widget
    def __init__(self):
        ttk.Combobox.__init__(self, self.parent, **self.config_parameters)

class Canvas(tk.Canvas, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Canvas.__init__(self, self.parent, **self.config_parameters)

class Listbox(tk.Listbox, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Listbox.__init__(self, self.parent, **self.config_parameters)

class Spinbox(ttk.Spinbox, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Spinbox.__init__(self, self.parent, **self.config_parameters)

class Image(tk.Label, WidgetMixin):
    @create_widget
    def __init__(self):
        icon = tk.PhotoImage(file = self.config_parameters["file"])
        tk.Label.__init__(self, self.parent, image = icon, **self.config_parameters)
        self.image = icon

class Menu(tk.Menu, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Menu.__init__(self, self.parent, **remove_params(self.config_parameters, ["label"]))
        if isinstance(self.parent, tk.Menu):
            self.parent.config(menu=self)
        else:
            self.parent.add_cascade(menu=self, **remove_params(self.config_parameters, ["tearoff"]))

class Page(tk.Frame, WidgetMixin):
    def __init__(self, parent, params, layout_manager, controller):
        WidgetMixin.__init__(self, parent, params, layout_manager, controller)
        tk.Frame.__init__(self, self.parent)
        
        if (page_name := self.config_parameters.pop("name", None)) is None:
            raise MissingAttributeException("page", self, "name")

        if (page_section := self.config_parameters.pop("section", None)) is None:
            raise MissingAttributeException("page", self, "section")

        if self.controller is None:
            raise MissingControllerException("page", self)

        if page_section not in self.controller.pages:
            self.controller.pages[page_section] = {}
            self.controller.active_pages[page_section] = None

        if page_name in self.controller.pages[page_section]:
            raise ValueError(f"{page_name} page already exists.")

        self.controller.pages[page_section][page_name] = self

        if self.config_parameters.pop("selected", False) or not self.controller.active_pages[page_section]:
            self.controller.set_page(page_section, page_name)
        
        self.config(**self.config_parameters)

class Container(tk.Frame, WidgetMixin):
    @create_widget
    def __init__(self):
        tk.Frame.__init__(self, self.parent, **remove_params(self.config_parameters, ["rowweight", "columnweight"]))
        if (row_weight := self.config_parameters.pop("rowweight", None)) is not None:
            self.grid_rowconfigure(0, weight=row_weight)

        if (column_weight := self.config_parameters.pop("columnweight", None)) is not None:
            self.grid_columnconfigure(0, weight=column_weight)
