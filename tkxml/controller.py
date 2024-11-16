"""
This module contains the base class for custom controllers
"""

class Controller:
    """
    Enables the creation of custom controls, which allows xml files to
    execute functions and access variables.
    """
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
