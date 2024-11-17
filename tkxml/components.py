"""
This module is used to create the default tkinter components and sinc them with the controllerss
"""
from tkinter.ttk import Combobox
from tkinter import (
    Button, Canvas, Checkbutton, Entry, Label, Listbox,
    Menu, PhotoImage, Radiobutton, Spinbox, Widget, Frame
)

from typing import Callable, Optional

from .utils import MissingAttributeException, MissingControllerException
from .controller import Controller

CONFIG_PARAMETER_PARSERS = {
    "textvariable": lambda config, controller: controller.get(config["textvariable"]),
    "variable":     lambda config, controller: controller.get(config["variable"]),
    "command":      lambda config, controller: controller.get(config["command"]),
    "values":       lambda config, controller: ''.join(config["values"]).split('|')
}

COMMON_COMPONENT_TAGS: dict[str, type] = {
    "frame": Frame, "canvas": Canvas, "label": Label, "checkbutton": Checkbutton,
    "radiobutton": Radiobutton, "spinbox": Spinbox, "button": Button, "entry": Entry,
    "combobox": Combobox
}

COMPLEX_COMPONENTS = {
    "page": lambda parent, parameters, controller: create_page(parameters, parent, controller),
    "menu": lambda parent, parameters, controller: create_menu(parameters, parent),
    "menuoption": lambda parent, parameters, controller:
        create_menu_option(parameters, parent, controller),
    "image": lambda parent, parameters, controller:
        create_photo_image(parameters, parent, controller),
    "listbox": lambda parent, parameters, controller:
        create_listbox(parameters, parent, controller),
    "title": lambda parent, parameters, controller: parent.title(parameters["title"]),
    "options": lambda parent, parameters, controller:
        [parent.option_add("*"+key, value) for key, value in parameters.items()],
    "geometry": lambda parent, parameters, controller:
        parent.geometry(parameters["size"]+"+"+parameters["position"]),
    "configure": lambda parent, parameters, controller: parent.configure(parameters)
}

def create_object(object_type: type, parent: Widget, params: dict,
                  controller: Optional[Controller]):
    """
    Default function for creating the tkinter component

    Parameters:
        object_type (type): The tkinter object to be created
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The active controller for the component

    Returns:
        Widget: The initialised component
    """
    pack, config = split_params(params, controller)
    element = object_type(parent, **config)
    element.pack(pack)

    return element

def split_params(params: dict, controller: Optional[Controller]) -> tuple [dict, dict]:
    """
    Splits the component parmeters into pack, config and exculsive (widget specific parameters)

    Parameters:
        params (dict): The parameters from the xml element
        exclude (dict): The parameters specific to the widget

    Returns:
           tuple: Tuple of pack and processed config parameters
    """
    pack = {}
    config = {}

    for key, item in params.items():
        if key in ["after", "anchor", "before", "expand", "fill",
                   "in", "ipadx", "ipady", "padx","pady", "side"]:
            pack[key] = item
        else:
            config[key] = CONFIG_PARAMETER_PARSERS.get(key,
                            lambda x, y, value=item: value)(params, controller)

    return pack, config

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

def create_photo_image(params: dict, parent: Widget, controller: Optional[Controller]) -> Label:
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

    pack, config = split_params(params, controller)
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
    listbox: Listbox = create_object(Listbox, parent, params, controller)

    for i, item in enumerate(''.join(params["values"]).split('|')):
        listbox.insert(i + 1, item)

    return listbox

def create_menu(params: dict, parent: Widget) -> Menu:
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

    if isinstance(parent, Menu):
        parent.config(menu = menu)
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
    _, config = split_params(params, controller)
    page_name = config.pop("name")

    page = Frame(parent)
    page.config(**config)

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

def get_components() -> dict[str, Callable]:
    """
    Gets the components available with their corresponding tags

    Returns:
        dict: A dictionary of tag keys and element creaion callables
    """
    components = {}
    for tag, component in COMMON_COMPONENT_TAGS.items():
        components[tag] = lambda parent, parameters, controller, value=component: create_object(
            value, parent, parameters, controller)

    components.update(COMPLEX_COMPONENTS)

    return components
