import time
from matrix.colours import Colours
from applets.base_applet import Applet


class SettingsApplet(Applet):
    """Template Applet Definition"""

    def __init__(self, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Settings Applet", **kwargs)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.offscreen_canvas.Clear()
        while not self.input_handler.exit_requested:
            latest_inputs = self.input_handler.get_latest_inputs()
            if latest_inputs["right_pressed"]:
                # ensure brightness never rises over 100
                self.display.matrix.brightness = min(
                    self.display.matrix.brightness + 10, 100
                )
            elif latest_inputs["left_pressed"]:
                # ensure brightness never drops under 0
                self.display.matrix.brightness = max(
                    self.display.matrix.brightness - 10, 0
                )

            # Brightness title
            self.display.draw_centered_text(
                "Brightness", Colours.WHITE_BOLD, start_y=10
            )

            # Brightness bar
            self.display.draw_progress_bar(
                self.display.matrix.brightness, Colours.YELLOW, y=14
            )

            self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
        self.display.offscreen_canvas.Clear()
