"""
This module is part of the tkxml package. It provides functionality to handle
XML transformations, parse inputs, and create tkinter windows.
"""
from tkinter import Tk
from typing import Optional
import xml.etree.ElementTree as ET

from .utils import MissingControllerException, MissingAttributeException, MissingTagException
from .components import create_component
from .controller import Controller
from .component import Component

class Tkxml:
    """
    Parses an xml file into a tkinter application, whilst supporting controllers and 
    custom components

    Attributes:
        master (Tk): The root of the tkinter application.
        controllers (dict): Stores the controllers used by the xml file.
        custom_components (dict): Stores the custom components used by the xml file.
        view (ET.ElementTree): The parsed XML element tree from the xml file.
    """
    def __init__(self, filename, master: Tk, controllers: dict = None,
                 custom_components: list[type] = None) -> None:
        """
        Initializes an Tkxml object.

        Parameters:
            filename (str): The file directory for the xml file.
            master (Tk): The root of the tkinter application.
            controllers (dict): The controller objects used by the xml file.
            custom_components (list): The custom component classes used by the xml file.
        """
        # Tkinter setup
        self.master = master
        self.controllers = controllers
        self.custom_components = dict((component.element_tag, component)
                                      for component in custom_components)

        # Parse the view
        view = ET.parse(filename)

        self.create_view(view)
        self.master.mainloop()

    def get_controller(self, element: ET.Element,
                       current_contoller: Optional[Controller]) -> Optional[Controller]:
        """
        Checks whether the current element has a controller attribute and 
        replaces the active controller if so.

        Parameters:
            element (ET.Element): The current xml element.
            current_controller (Optional[Controller]): The current active controller.

        Returns:
            Optional[Controller]: The selected controller.
        """
        controller_key = element.attrib.get("controller")
        if controller_key:
            controller = self.controllers.get(controller_key)
            if controller:
                return controller

            print(f"WARN: Controller {controller_key} not found | {element.tag}")
        return current_contoller

    def create_view(self, view: ET.ElementTree) -> None:
        """
        Create the tkinter window view

        Parameters:
            view (ET.ElementTree): The xml parsed element tree.
        """
        root = view.getroot()
        controller = self.get_controller(root, None)
        for child in root:
            self.create_element(child, self.master, controller)

    def create_element(self, element_tag: ET.Element, parent,
                       controller: Optional[Controller]) -> None:
        """
        Creates the next element using recursion to navigate through the Element Tree.

        Parameters:
            element_tag (ET.Element): The current element tag from the xml file.
            parent (Widget): The parent tkinter object of this child element.
            controller (Optional[Controller]): The current active controller.
        """
        controller = self.get_controller(element_tag, controller)
        attrs = dict((key, item) for key, item in element_tag.attrib.items()
                     if key not in ["controller", "id"])

        element = None
        try:
            custom_element = self.custom_components.get(element_tag.tag)

            if custom_element:
                element = custom_element(parent, attrs, controller)
            else:
                element = create_component(element_tag.tag, attrs, parent, controller, self)

            element_id = element_tag.attrib.get("id")
            if element_id:
                controller.set(element_id, element)
        except (MissingTagException, MissingAttributeException, MissingControllerException,
                ValueError) as e:
            print(e)

        if element is not None and not isinstance(element, Component):
            parent = element

        for child in element_tag:
            self.create_element(child, parent, controller)
