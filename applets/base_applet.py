"""Base applet definition"""
import os
import inspect

class Applet:
    """Base applet from which all others will inherit"""
    def __init__(self, name: str, **kwargs) -> None:
        self.name = name
        self.display = kwargs.get("display", None)
        self.options = kwargs.get("options", None)
        self.input_handler = kwargs.get("input_handler", None)
        self.resources_directory = os.path.join(
            os.path.dirname(
                inspect.getouterframes(inspect.currentframe())[1].filename
            ),
            "resources"
        )

    def log(self, message: str) -> None:
        """Display an identifiable logging message"""
        print(f"[LOG] [Applet: {self.name}] '{message}'")

    def start(self) -> None:
        """Start the applet"""
        raise NotImplementedError(
            "This method should not be implemented directly - implement within subclass"
        )

    def stop(self) -> None:
        """Stop the applet"""
        raise NotImplementedError(
            "This method should not be implemented directly - implement within subclass"
        )
