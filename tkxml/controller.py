"""
This module contains the base class for custom controllers
"""
from typing import Optional

class Controller:
    """
    Enables the creation of custom controls, which allows xml files to
    execute functions and access variables.
    """

    def __init__(self):
        self.pages: dict[str, dict[str, object]] = {}
        self.active_pages: dict[str, Optional[str]] = {}

    def set_page(self, section_name: str, page_name: str):
        """
        Sets the active page for the controller

        Args:
            page_name (str): The name of the page to set active

        Raises:
            ValueError: Checks if the page name exists
        """
        selected_section = self.pages.get(section_name)
        if not selected_section:
            raise KeyError(f"Cannot find {section_name} page section.")

        selected_page = selected_section.get(page_name)
        if not selected_page:
            raise KeyError(f"Cannot find {page_name} page.")

        for page in selected_section.values():
            page.deactivate()

        selected_page.activate()
        self.active_pages[section_name] = page_name

    def get(self, variable_name: str):
        """
        Gets a function/variable attribute based from a string name

        Parameters:
            variable_name (str): The name of the variable

        Returns:
            Any: The variable of given name
        """
        return getattr(self, variable_name, "")

    def set(self, variable_name: str, value) -> None:
        """
        Sets a function/variable attribute based from a string name and
        value

        Parameters:
            variable_name (str): The name of the variable
            value (Any): The set value
        """
        return setattr(self, variable_name, value)
