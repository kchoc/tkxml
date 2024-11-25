from typing import Optional, Literal, Callable

LAYOUT_ATTRIBUTES = {
    "pack": ["after", "anchor", "before", "expand", "fill", "in", "ipadx", "ipady",
                   "padx", "pady", "side"],
    "grid": ["column", "columnspan", "row", "rowspan", "sticky", "ipadx", "ipady",
                   "padx", "pady"],
    "place": ["relx", "rely", "relheight", "relwidth", "height", "width", "x", "y",
                    "anchor", "bordermode"]
}

CONFIG_PARAMETER_PARSERS = {
    "textvariable": lambda config, controller: controller.get(config["textvariable"]),
    "variable":     lambda config, controller: controller.get(config["variable"]),
    "command":      lambda config, controller: process_command(config["command"], controller),
    "values":       lambda config, controller: ''.join(config["values"]).split('|')
}

def process_command(command: str, controller) -> Callable:
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

def split_params(params: dict[str, str], controller, exclude_attributes: list) -> tuple [dict, dict]:
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
        if key in exclude_attributes:
            pack[key] = item
        else:
            config[key] = CONFIG_PARAMETER_PARSERS.get(key,
                            lambda x, y, value=item: value)(params, controller)

    return pack, config

class WidgetMixin:
    """
    A mixin class for Tkinter widgets to handle layout management and activation/deactivation.
    Attributes:
        parent: The parent widget.
        layout_manager: The layout manager to use ("pack", "grid", or "place").
        layout_attributes: The attributes for the layout manager.
        config_parameters: The configuration parameters for the widget.
        controller: An optional controller for additional functionality.
    Methods:
        __init__(parent, params, layout_manager, controller):
            Initializes the WidgetMixin with the given parameters.
        activate():
            Activates the widget using the specified layout manager.
        deactivate():
            Deactivates the widget using the specified layout manager.
    """
    def __init__(self, parent, params: dict[str, str], layout_manager: Literal["pack", "grid", "place"],
                controller):
        self.parent = parent
        self.layout_manager = layout_manager
        self.layout_attributes, self.config_parameters = split_params(params, controller, LAYOUT_ATTRIBUTES[layout_manager])
        self.controller = controller

    def activate(self):
        """
        Activates the widget
        """
        match self.layout_manager:
            case "pack":
                self.pack(**self.layout_attributes)
            case "grid":
                self.grid(**self.layout_attributes)
            case "place":
                self.place(**self.layout_attributes)

    def deactivate(self):
        """
        Deactivates the widget
        """
        match self.layout_manager:
            case "pack":
                self.pack_forget()
            case "grid":
                self.grid_forget()
            case "place":
                self.place_forget()
