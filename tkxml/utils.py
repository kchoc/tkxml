"""
Utils for raising errors when parsing xml elements
"""

class MissingTagException(BaseException):
    """
    Unknown tag.
    """
    def __init__(self, tag, parent):
        super().__init__(f"WARN: Could not find {tag} tag | Parent: {parent} ")

class MissingAttributeException(BaseException):
    """
    Missing tag attribute.
    """
    def __init__(self, tag, component, attribute):
        super().__init__(f"WARN: {attribute} attribute is missing for {tag} | {component}")

class MissingControllerException(BaseException):
    """
    No avtive controller.
    """
    def __init__(self, tag, component):
        super().__init__(f"WARN: Missing controller for {tag} | {component}")
