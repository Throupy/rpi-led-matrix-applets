import os
from typing import Dict
from matrix.matrix_display import MatrixDisplay


class Applet:
    def __init__(self, name: str, display: MatrixDisplay, options: Dict[str, str] = {}) -> None:
        self.name = name
        self.display = display
        self.options = options

    def log(self, message: str) -> None:
        """Display an identifiable logging message"""
        print(f"[LOG] [Applet: {self.name}] '{message}'")

    def start(self) -> None:
        raise NotImplementedError(
            "This method should not be implemented directly - implement within subclass"
        )

    def stop(self) -> None:
        raise NotImplementedError(
            "This method should not be implemented directly - implement within subclass"
        )
