"""
This module is used to create the default tkinter components and sinc them with the controllers
"""
from tkinter.ttk import Combobox
from tkinter import (
    BooleanVar, Button, Canvas, Checkbutton, DoubleVar, Entry, IntVar, Label, Listbox,
    Menu, PhotoImage, Radiobutton, Spinbox, StringVar, Variable, Widget, Frame
)

from typing import Callable, Optional

from .utils import MissingAttributeException, MissingControllerException
from .controller import Controller

def process_command(command: str, controller: Optional[Controller]) -> Callable:
    """
    Processess commands; $ signifies a python expresion, else accesses a fucntion inside the
    current controller

    Args:
        command (str): The parameter value of the command
        controller (Optional[Controller]): The current active controller

    Returns:
        Callable: The function from the parsed command parameter
    """
    if command[0] == "$":
        return lambda controller=controller: exec(command[1:], {"controller": controller})
    return controller.get(command)

def process_trace(trace: str, controller: Optional[Controller]) -> Callable:
    """
    Processess variable traces; $ signifies a python expresion, else accesses a fucntion
    inside the current controller

    Args:
        trace (str): The parameter value of the trace
        controller (Optional[Controller]): The current active controller

    Returns:
        Callable: The function from the parsed trace parameter
    """
    if trace[0] == "$":
        return lambda var, index, mode, controller=controller: exec(trace[1:],
            {"controller": controller})
    return controller.get(trace)

def create_object(object_type: type, parent: Widget, params: dict[str, str],
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

def split_params(params: dict[str, str], controller: Optional[Controller]) -> tuple [dict, dict]:
    """
    Splits the component parmeters into pack, config and exculsive (widget specific parameters)

    Parameters:
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The current active controller

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

def create_photo_image(parent: Widget, params: dict[str, str], controller: Optional[Controller]) -> Label:
    """
    Creates a photo image component

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The current active controller

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

def create_listbox(parent, params: dict[str, str], controller: Optional[Controller]) -> Listbox:
    """
    Creates a listbox component

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The current active controller

    Returns:
        Widget: The initialised component
    """
    listbox: Listbox = create_object(Listbox, parent, params, controller)

    for i, item in enumerate(''.join(params["values"]).split('|')):
        listbox.insert(i + 1, item)

    return listbox

def create_menu(parent: Widget, params: dict[str, str], _=None) -> Menu:
    """
    Creates a menu component

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element

    Returns:
        Widget: The initialised component
    """
    menu = Menu(parent, **remove_params(params, ["label"]))

    if isinstance(parent, Menu):
        parent.config(menu = menu)
    else:
        parent.add_cascade(menu = menu, **remove_params(params, ["tearoff"]))

    return menu

def create_menu_option(parent: Menu, params: dict[str, str], controller: Optional[Controller]) -> None:
    """
    Adds an option to the menu

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The current active controller
    """
    attr = remove_params(params, ["command"])
    parent.add_command(**attr, command=controller.get(params["command"]))

def create_page(parent: Frame, params: dict[str, str], controller: Optional[Controller]) -> Frame:
    """
    Creates a page inside the current controller

    Parameters:
        parent (Frame): The parent tkinter object
        params (dict): The parameters from the xml element
        controller (Optional[Controller]): The current active controller

    Raises:
        MissingAttributeException: Presence check for "name" and "section" attribute
        MissingControllerException: Presence check for controller
        ValueError: Presence check if page already exists in controller

    Returns:
        Frame: The initialised component
    """
    _, config = split_params(params, controller)
    page_name = config.pop("name", None)
    page_section = config.pop("section", None)

    page = Frame(parent)
    page.config(**config)

    if not page_name:
        raise MissingAttributeException("page", page, "name")

    if not page_section:
        raise MissingAttributeException("page", page, "section")

    if controller is None:
        raise MissingControllerException("page", page)

    if page_section not in controller.pages:
        controller.pages[page_section] = {}
        controller.active_pages[page_section] = None

    if page_name in controller.pages[page_section]:
        raise ValueError(f"{page_name} page already exists.")

    controller.pages[page_section][page_name] = page

    selected = params.get("selected")
    if selected and selected == "True" or not controller.active_pages[page_section]:
        controller.set_page(page_section, page_name)

    return page

def create_variable(parent: Widget, params: dict[str, str], controller: Optional[Controller]) -> None:
    variable_type_key = params.get("type")
    if not variable_type_key:
        raise MissingAttributeException("variable", None, "type")

    variable_name = params.get("name")
    if not variable_name:
        raise MissingAttributeException("variable", None, "name")

    variable_type = VARIABLES.get(variable_type_key.lower()[:3])
    if not variable_type:
        raise KeyError(f"WARN: Variable type {variable_type} could not be found!")

    # TODO: Check if variable already exists

    value = params.get("value")
    variable: Variable = variable_type(parent, value) if params.get("value") else variable_type(parent)

    for mode in ["array", "read", "write", "unset"]:
        trace = params.get(mode)
        if trace:
            variable.trace_add(mode, process_trace(trace, controller))

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

VARIABLES = {
    "int": IntVar,
    "boo": BooleanVar,
    "str": StringVar,
    "dou": DoubleVar
}

CONFIG_PARAMETER_PARSERS = {
    "textvariable": lambda config, controller: controller.get(config["textvariable"]),
    "variable":     lambda config, controller: controller.get(config["variable"]),
    "command":      lambda config, controller: process_command(config["command"], controller),
    "values":       lambda config, controller: ''.join(config["values"]).split('|')
}

COMMON_COMPONENT_TAGS: dict[str, type] = {
    "frame": Frame, "canvas": Canvas, "label": Label, "checkbutton": Checkbutton,
    "radiobutton": Radiobutton, "spinbox": Spinbox, "button": Button, "entry": Entry,
    "combobox": Combobox
}

COMPLEX_COMPONENTS = {
    "page": create_page,
    "menu": create_menu,
    "menuoption": create_menu_option,
    "image": create_photo_image,
    "listbox": create_listbox,
    "variable": create_variable,
    "title": lambda parent, parameters, controller: parent.title(parameters["title"]),
    "options": lambda parent, parameters, controller:
        [parent.option_add("*"+key, value) for key, value in parameters.items()],
    "geometry": lambda parent, parameters, controller:
        parent.geometry(parameters["size"]+"+"+parameters["position"]),
    "configure": lambda parent, parameters, controller: parent.configure(parameters)
}
