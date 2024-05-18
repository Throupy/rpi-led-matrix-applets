"""Base applet definition"""

from typing import Dict
from matrix.matrix_display import MatrixDisplay


class Applet:
    """Base applet from which all others will inherit"""
    def __init__(self, name: str, display: MatrixDisplay, options: Dict[str, str] = None) -> None:
        self.name = name
        self.display = display
        self.options = options

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
