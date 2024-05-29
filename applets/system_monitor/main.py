import time
import psutil
from typing import Dict
from matrix.matrix_display import graphics
from matrix.colours import Colours
from applets.base_applet import Applet


class SystemMonitor(Applet):
    """System Monitor Applet Definition"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("System Monitor", *args, **kwargs)

    @staticmethod
    def fetch_stats() -> Dict[str, str]:
        """Fetch various system statistics"""
        stats = {
            "CPU": f"{psutil.cpu_percent()}%",
            "RAM": f"{psutil.virtual_memory().percent}%",
            "Disk": f"{psutil.disk_usage('/').percent}%",
            "Uptime": f"{time.time() - psutil.boot_time():.0f}s",
            "Procs.": f"{len(psutil.pids())}",
        }
        return stats

    @staticmethod
    def get_color_from_usage(usage_percent: float) -> graphics.Color:
        """Calculate colour based on usage percentage"""
        # Usage 0 -> Green, 100 -> Red
        green = int((100 - usage_percent) * 2.55)
        red = int(usage_percent * 2.55)
        return graphics.Color(red, green, 0)

    def display_stats(self, stats: Dict[str, str]) -> None:
        """Display system statistics on the matrix"""
        self.display.clear()

        y_offset = 10  # lil bit down from the top
        label_colour = Colours.WHITE_NORMAL

        # Find longest key - display values inline with the end of longest line
        longest_key = max(stats.keys(), key=len)
        key_offset = self.display.get_text_width(longest_key) + 5  # 5 padding

        for stat_name, stat_value in stats.items():
            if "%" in stat_value:
                cpu_percent = float(stat_value.strip("%"))
                value_colour = self.get_color_from_usage(cpu_percent)
            else:
                value_colour = Colours.WHITE_MUTED

            # draw stat name
            self.display.draw_text(1, y_offset, stat_name, label_colour)

            # draw stat value
            self.display.draw_text(key_offset, y_offset, stat_value, value_colour)
            y_offset += 10  # line height

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
            self.display.offscreen_canvas
        )
        time.sleep(1)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.clear()
        while not self.input_handler.exit_requested:
            stats = self.fetch_stats()
            self.display_stats(stats)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.clear()
