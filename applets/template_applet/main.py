import random
import time
from matrix.matrix_display import graphics
from applets.base_applet import Applet


class TemplateApplet(Applet):
    """Template Applet Definition"""

    def __init__(self, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Template Applet", **kwargs)
        self.option_value = self.options.get("example_option")

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.offscreen_canvas.Clear()
        text = "Template"
        # Initial values
        while not self.input_handler.exit_requested:
            self.display.matrix.Clear()
            graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                18,
                32,
                graphics.Color(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
                text,
            )
            text = "Applet" if text == "Template" else "Template"
            self.display.offscreen_canvas =  self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
            time.sleep(1)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
        self.display.offscreen_canvas.Clear()
