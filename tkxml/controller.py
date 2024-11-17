"""
This module contains the base class for custom controllers
"""
from typing import Optional
from tkinter import Frame

class Controller:
    """
    Enables the creation of custom controls, which allows xml files to
    execute functions and access variables.
    """

    def __init__(self):
        self.pages: dict[str, Frame] = {}
        self.active_page: Optional[Frame] = None

    def set_page(self, page_name: str):
        """
        Sets the active page for the controller

        Args:
            page_name (str): The name of the page to set active

        Raises:
            ValueError: Checks if the page name exists
        """
        selected_page = self.pages.get(page_name)
        if not selected_page:
            raise ValueError(f"Cannot find {page_name} page.")

        for page in self.pages.values():
            page.pack_forget()  # Hide all pages

        selected_page.pack(fill="both", expand=True)
        self.active_page = page_name

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
