"""
This module is used to create the default tkinter components and sinc them with the controllerss
"""
from tkinter.ttk import Combobox
from tkinter import (
    PhotoImage, Frame, Label, Listbox, Menu, Canvas,
    Checkbutton, Radiobutton, Spinbox, Button, Entry, Widget
)
from typing import Optional

from .utils import MissingAttributeException, MissingControllerException, MissingTagException
from .controller import Controller


def create_object(object_type: type, parent: Widget, params: dict, controller,
                  init_params: dict = None):
    """
    Default function for creating the tkinter component

    Parameters:
        object_type (type): The tkinter object to be created
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The active controller for the component
        init_params (dict): The parameters specific to the type of widget as well as format

    Returns:
        Widget: The initialised component
    """
    pack, config, exc = split_params(params, init_params)
    element = object_type(parent,
                            **dict((key, init_params[key](params, controller)) for key in exc))
    element.config(**config)
    element.pack(**pack)
    return element

def split_params(params: dict, exclude: dict = None) -> tuple[dict, dict, list]:
    """
    Splits the component parmeters into pack, config and exculsive (widget specific parameters)

    Parameters:
        params (dict): The parameters from the xml element
        exclude (dict): The parameters specific to the widget

    Returns:
        tuple[dict, dict, list]: Tuple of pack, config and exculsive parameters
    """
    pack = {}
    config = {}
    exc = []
    for key, item in params.items():
        if key in ["after", "anchor", "before", "expand", "fill",
                   "in", "ipadx", "ipady", "padx","pady", "side"]:
            pack[key] = item
        elif exclude is None or key not in exclude:
            config[key] = item
        else:
            exc.append(key)

    return pack, config, exc

def remove_params(params: dict, keys: list) -> dict:
    """
    Removes parameters which are present in the keys list

    Parameters:
        params (dict): The parameters from the xml element
        keys (list): The keys to exclude

    Returns:
        dict: The parameters without the excluded keys
    """
    return dict((key, item) for key, item in params.items() if key not in keys)

def create_photo_image(params: dict, parent) -> Label:
    """
    Creates a photo image component

    Parameters:
        params (dict): The parameters from the xml element
        parent (Widget): The parent tkinter object

    Returns:
        Widget: The initialised component
    """
    icon = PhotoImage(file = params["file"])
    label_icon = Label(parent)

    pack, config, _ = split_params(params, exclude = ["file"])
    label_icon.config(image = icon, **config)
    label_icon.image = icon
    label_icon.pack(**pack)

    return label_icon

def create_listbox(params: dict, parent, controller: Optional[Controller]) -> Listbox:
    """
    Creates a listbox component

    Parameters:
        params (dict): The parameters from the xml element
        parent (Widget): The parent tkinter object
        controller (Optional[Controller]): The current active controller

    Returns:
        Widget: The initialised component
    """
    listbox: Listbox = create_object(Listbox, parent, params, controller,
                                     init_params={"values": lambda x, y: None})

    for i, item in enumerate(''.join(params["values"]).split('|')):
        listbox.insert(i + 1, item)

    return listbox

def create_menu(params: dict, parent: Menu, self) -> Menu:
    """
    Creates a menu component

    Parameters:
        params (dict): The parameters from the xml element
        parent (Widget): The parent tkinter object
        self (Tkxml): The Tkxml main object

    Returns:
        Widget: The initialised component
    """
    menu = Menu(parent, **remove_params(params, ["label"]))

    if parent == self.master:
        self.master.config(menu = menu)
    else:
        parent.add_cascade(menu = menu, **remove_params(params, ["tearoff"]))

    return menu

def create_menu_option(params: dict, parent: Menu, controller: Optional[Controller]) -> None:
    """
    Creates a photo image component

    Parameters:
        params (dict): The parameters from the xml element
        parent (Widget): The parent tkinter object
        controller (Optional[Controller]): The current active controller
    """
    attr = remove_params(params, ["command"])
    parent.add_command(**attr, command=controller.get(params["command"]))

def create_page(params: dict, parent: Frame, controller: Optional[Controller]) -> Frame:
    """
    Creates a page inside the current controller

    Parameters:
        params (dict): The parameters from the xml element
        parent (Frame): The parent tkinter object
        controller (Optional[Controller]): The current active controller

    Raises:
        MissingAttributeException: Presence check for "name" attribute
        MissingControllerException: Presence check for controller
        ValueError: Presence check if page already exists in controller

    Returns:
        Frame: The initialised component
    """
    _, config, _ = split_params(params, exclude = ["name", "selected"])
    page = Frame(parent)
    page.config(**config)
    page_name = params.get("name")

    if not page_name:
        raise MissingAttributeException("page", page, "name")

    if controller is None:
        raise MissingControllerException("page", page)

    if page_name in controller.pages:
        raise ValueError(f"{page_name} page already exists.")

    controller.pages[page_name] = page

    selected = params.get("selected")
    if selected and selected == "True" or not controller.active_page:
        controller.set_page(page_name)

    return page

def create_component(component: str, params: dict, parent, controller: Optional[Controller], self):
    """
    Selects and creates the default tkinter components using the params based off the
    component tag name.
    
    Parameters:
        component(str): The component name
        params (dict): The parameters from the xml element
        parent (Widget): The parent tkinter component
        controller (Optional[Controller]): The current active controller
        self (Tkxml): The Tkxml main object
    
    Returns:
        Optional[Widget]: The initialized component if created

    Raises:
        MissingTagException: If the component could not be found
    """
    component_object = None
    match component:
        case "frame":
            component_object = create_object(Frame,       parent, params, controller)

        case "canvas":
            component_object = create_object(Canvas,      parent, params, controller)

        case "label":
            component_object = create_object(Label,       parent, params, controller, {
        "textvariable":    lambda params, controller: controller.get(params["textvariable"])})

        case "checkbutton":
            component_object = create_object(Checkbutton, parent, params, controller, {
        "variable":        lambda params, controller: controller.get(params["variable"])})

        case "radiobutton":
            component_object = create_object(Radiobutton, parent, params, controller, {
        "variable":        lambda params, controller: controller.get(params["variable"])})

        case "spinbox":
            component_object = create_object(Spinbox,     parent, params, controller, {
        "textvariable":    lambda params, controller: controller.get(params["textvariable"])})

        case "button":
            component_object = create_object(Button,      parent, params, controller, {
        "command":         lambda params, controller: controller.get(params["command"])})

        case "entry":
            component_object = create_object(Entry,       parent, params, controller, {
        "textvariable":    lambda params, controller: controller.get(params["textvariable"])})

        case "combobox":
            component_object = create_object(Combobox,       parent, params, controller, {
        "values":          lambda params, controller: ''.join(params["values"]).split('|'),
        "textvariable":    lambda params, controller: controller.get(params["textvariable"])})

        case "page":
            component_object = create_page(params, parent, controller)

        case "menu": component_object = create_menu(params, parent, self)
        case "menuoption": create_menu_option(params, parent, controller)
        case "image": component_object = create_photo_image(params, parent)
        case "listbox": component_object = create_listbox(params, parent, controller)

        case "title":
            self.master.title(params["title"])

        case "options":
            for key, value in params.items():
                self.master.option_add("*"+key, value)

        case "geometry":
            self.master.geometry(params["size"]+ "+" + params["position"])

        case "configure":
            self.master.configure(params)

        case _:
            raise MissingTagException(component, parent)

    return component_object
