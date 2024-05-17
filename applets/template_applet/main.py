import random
import time
import os
from typing import Dict
from matrix.matrix_display import MatrixDisplay, graphics
from applets.base_applet import Applet


class TemplateApplet(Applet):
    """Template Applet Definition"""

    def __init__(self, display: MatrixDisplay, options: Dict[str, str]) -> None:
        """Initialisation function"""
        super().__init__("Helldivers Kill Counter", display)
        self.option_value = options.get("example_option")
        # Get resource file
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # assume a dir called 'resources' exists in the same dir as implementation
        self.resources_directory = os.path.join(current_directory, "resources")

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        text = "Template"
        # Initial values
        while True:
            self.display.matrix.Clear()
            graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                18,
                32,
                graphics.Color(
                    random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                ),
                text,
            )
            text = "Applet" if text == "Template" else "Template"
            self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
            time.sleep(1)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
