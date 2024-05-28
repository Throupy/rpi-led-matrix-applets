import time
import psutil
from matrix.matrix_display import MatrixDisplay
from matrix.colours import Colours
from applets.base_applet import Applet


class IdleApplet(Applet):
    def __init__(self, display: MatrixDisplay, **kwargs) -> None:
        super().__init__("IdleApplet", **kwargs)
        self.display = display

    def draw_digital_clock(self):
        # Get the current time
        current_time = time.localtime()
        h, m, s = current_time.tm_hour, current_time.tm_min, current_time.tm_sec
        self.display.clear()
        time_string = f"{h:02}:{m:02}:{s:02}"

        self.display.draw_centered_text(time_string, Colours.WHITE_MUTED, start_y=16)
        # Swap the offscreen canvas to display the drawn clock
        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)

    def start(self) -> None:
        self.log("Starting IdleApplet")
        self.display.clear()
        # More resource-friendly to call psutil.boot_time() once and increment rather than
        # calling the method every second.
        self.uptime_seconds = time.time() - psutil.boot_time()
        while not self.input_handler.exit_requested:
            latest_inputs = self.input_handler.get_latest_inputs()
            if any(latest_inputs.values()):
                self.input_handler.exit_requested = True
            # draw a clock
            self.draw_digital_clock()
            # draw the system uptime
            self.display.draw_centered_text(
                f"System Uptime: {self.uptime_seconds:.0f}s", Colours.WHITE_MUTED
            )

            self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
            self.uptime_seconds += 1
            time.sleep(1)

    def stop(self) -> None:
        self.log("Stopping IdleApplet")
        self.display.clear()

