"""
This module is used to create the default tkinter components and sinc them with the controllers
"""
from tkinter import (
    BooleanVar, DoubleVar, IntVar, StringVar, Variable
)
from .custom_components import (
    Frame, Button, Label, Entry, Checkbutton, Page, Menu,
    Radiobutton, Combobox, Canvas, Listbox, Spinbox, Image, remove_params
)
from typing import Callable, Optional

from .utils import MissingAttributeException, MissingControllerException
from .controller import Controller

def process_trace(trace: str, controller) -> Callable:
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

def create_menu_option(parent: Menu, params: dict[str, str], layout_manager: str, controller: Optional[Controller]) -> None:
    """
    Adds an option to the menu

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        layout_manager (str): The layout manager for the component
        controller (Optional[Controller]): The current active controller
    """
    attr = remove_params(params, ["command"])
    parent.add_command(**attr, command=controller.get(params["command"]))

def create_variable(parent, params: dict[str, str], layout_manager: str, controller: Optional[Controller]) -> None:
    """
    Creates a variable inside the current controller

    Parameters:
        parent (Widget): The parent tkinter object
        params (dict): The parameters from the xml element
        layout_manager (str): The layout manager for the component
        controller (Optional[Controller]): The current active controller
    
    Raises:
        MissingAttributeException: Presence check for "type" and "name" attribute
        MissingControllerException: Presence check for controller
        KeyError: Presence check for variable type
    
    Returns:
        Variable: The initialised component
    """
    if not controller:
        raise MissingControllerException("variable", None)
    
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
    
    controller.set(variable_name, variable)

def get_components() -> dict[str, Callable]:
    """
    Gets the components available with their corresponding tags
    
    Returns:
        dict: A dictionary of tag keys and element creaion callables
    """
    components = COMMON_COMPONENT_TAGS.copy()

    components.update(COMPLEX_COMPONENTS)

    return components

VARIABLES = {
    "int": IntVar,
    "boo": BooleanVar,
    "str": StringVar,
    "dou": DoubleVar
}

COMMON_COMPONENT_TAGS: dict[str, type] = {
    "frame": Frame, "canvas": Canvas, "label": Label, "checkbutton": Checkbutton,
    "radiobutton": Radiobutton, "spinbox": Spinbox, "button": Button, "entry": Entry,
    "combobox": Combobox, "listbox": Listbox, "image": Image, "menu": Menu, "page": Page
}

COMPLEX_COMPONENTS = {
    "menuoption": create_menu_option,
    "variable": create_variable,
    "title": lambda parent, parameters, layout_manager, controller: parent.title(parameters["title"]),
    "options": lambda parent, parameters, layout_manager, controller:
        [parent.option_add("*"+key, value) for key, value in parameters.items()],
    "geometry": lambda parent, parameters, layout_manager, controller:
        parent.geometry(parameters["size"]+"+"+parameters["position"]),
    "configure": lambda parent, parameters, layout_manager, controller: parent.configure(parameters)
}
