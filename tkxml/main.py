"""
This module is part of the tkxml package. It provides functionality to handle
XML transformations, parse inputs, and create tkinter windows.
"""
from tkinter import TclError, Tk
from typing import Optional

from .utils import (
    MissingControllerException, MissingAttributeException, MissingTagException, raise_
)
from .components import get_components
from .controller import Controller
from .component import Component
from .parser import parse, Node

class Tkxml:
    """
    Parses an tkxml file into a tkinter application, whilst supporting controllers and 
    custom components

    Attributes:
        master (Tk): The root of the tkinter application.
        controllers (dict): Stores the controllers used by the tkxml file.
        custom_components (dict): Stores the custom components used by the tlxml file.
        root (ET.ElementTree): The parsed TKXML element tree from the tkxml file.
    """
    def __init__(self, filename, master: Tk, controllers: list[Controller] = None,
                 custom_components: list[type] = None, verbose: bool = False) -> None:
        """
        Initializes an Tkxml object.

        Parameters:
            filename (str): The file directory for the tkxml file.
            master (Tk): The root of the tkinter application.
            controllers (dict): The controller objects used by the tkxml file.
            custom_components (list): The custom component classes used by the tkxml file.
        """
        # Tkinter 
        self.master = master
        self.controllers = dict((controller.__class__.__name__, controller)
            for controller in controllers)if controllers else {}
        self.custom_components = dict((component.element_tag, component)
                                      for component in custom_components)
        self.verbose = verbose
        self.components = get_components()

        # Read the tkxml file
        with open(filename, "r") as file:
            if file:
                contents = file.read()

        # Parse the view
        root, _ = parse(contents)

        self.create_view(root)
        self.master.mainloop()

    def get_controller(self, element: Node,
                       current_contoller: Optional[Controller]) -> Optional[Controller]:
        """
        Checks whether the current element has a controller attribute and 
        replaces the active controller if so.

        Parameters:
            element (Node): The current xml element.
            current_controller (Optional[Controller]): The current active controller.

        Returns:
            Optional[Controller]: The selected controller.
        """
        controller_key = element.attributes.get("controller")
        if controller_key:
            controller = self.controllers.get(controller_key)
            if controller:
                return controller

            raise ValueError(f"WARN: Controller {controller_key} not found | {element.name}")
        return current_contoller

    def create_view(self, root: Node) -> None:
        """
        Create the tkinter window view

        Parameters:
            view (Node): The tkxml parsed element tree.
        """
        controller = self.get_controller(root, None)
        if self.verbose:
            print("Root Children:", [child.name for child in root.children])

        for child in root.children:
            self.create_element(child, self.master, controller)

    def create_element(self, element_node: Node, parent,
                       controller: Optional[Controller]) -> None:
        """
        Creates the next element using recursion to navigate through the Element Tree.

        Parameters:
            element_tag (Node): The current element tag from the tkxml file.
            parent (Widget): The parent tkinter object of this child element.
            controller (Optional[Controller]): The current active controller.
        """
        if self.verbose:
            print("Creating Component: ", element_node.name)

        controller = self.get_controller(element_node, controller)
        attrs = dict((key, item) for key, item in element_node.attributes.items()
                     if key not in ["controller", "id"])

        element = None
        try:
            custom_element = self.custom_components.get(element_node.name)

            if custom_element:
                element = custom_element(parent, attrs, element_node.layout_manager, controller)
            else:
                element = self.components.get(element_node.name,
                    lambda x, y, z: raise_(MissingTagException(element_node.name, parent))
                )(parent, attrs, element_node.layout_manager, controller)

            element_id = element_node.attributes.get("id")
            if element_id:
                controller.set(element_id, element)

        except (MissingTagException, MissingAttributeException, MissingControllerException,
                ValueError) as e:
            print(e)
        except TclError as e:
            print(f"{e} | {element_node.name}")

        if element is not None and not isinstance(element, Component):
            parent = element

        for child in element_node.children:
            self.create_element(child, parent, controller)
