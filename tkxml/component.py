"""
Contains the base class for making custom components
"""

class Component:
    """
    Base class for making custom components
    """
    def __init__(self, parent, params, controller):
        """
        Initialises the base component with the default parameters

        Parameters:
            params (dict): The parameters from the xml element
            parent (Widget): The parent tkinter component
            controller (Optional[Controller]): The current active controller
        """
        self.parent = parent
        self.params = params
        self.controller = controller
        self.element_tag = "custom"
