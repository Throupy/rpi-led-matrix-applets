"""AppletInformationViewer implementation"""

import time

from applets.base_applet import Applet
from matrix.colours import Colours


class AppletInformationViewer(Applet):
    """Template Applet Definition"""

    def __init__(self, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Applet Information Viewer", **kwargs)
        self.applet_config = kwargs.get("applet_config", {})
        self.current_index = 0
        self.last_switch_time = time.time() - 5
        self.keys_to_show = ["name", "description", "version", "author"]

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.clear()

        # Filter the keys and values based on keys_to_show
        keys = [key for key in self.keys_to_show if key in self.applet_config]
        values = [self.applet_config[key] for key in keys]

        while not self.input_handler.exit_requested:
            current_time = time.time()
            latest_inputs = self.input_handler.get_latest_inputs()
            if current_time - self.last_switch_time >= 5 or latest_inputs.get(
                "select_pressed"
            ):
                self.display.clear()
                current_key = keys[self.current_index % len(keys)]
                current_value = values[self.current_index % len(values)]
                # Draw Title
                self.display.draw_centered_text(
                    current_key.title(), Colours.RED, start_y=7
                )

                # Draw Value
                self.display.draw_centered_text(current_value, Colours.WHITE_MUTED)
                self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
                self.current_index += 1
                self.last_switch_time = current_time

            time.sleep(0.1)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.clear()
