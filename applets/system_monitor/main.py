import time
import os
import requests
import json
import psutil
from typing import Tuple, Optional, Dict
from PIL import Image
from matrix.matrix_display import MatrixDisplay, graphics
from applets.base_applet import Applet


class SystemMonitor(Applet):
    """System Monitor Applet Definition"""

    def __init__(self, display: MatrixDisplay) -> None:
        """Initialisation function"""
        super().__init__("System Monitor", display)

    def fetch_stats(self) -> Dict[str, str]:
        """Fetch various system statistics"""
        stats = {
            "CPU": f"{psutil.cpu_percent()}%",
            "RAM": f"{psutil.virtual_memory().percent}%",
            "Disk": f"{psutil.disk_usage('/').percent}%",
            "Uptime": f"{time.time() - psutil.boot_time():.0f}s",
            "Processes": f"{len(psutil.pids())}",
        }
        return stats

    def get_color_from_usage(self, usage_percent: float) -> graphics.Color:
        """Calculate colour based on usage percentage"""
        # Usage 0 -> Green, 100 -> Red
        green = int((100 - usage_percent) * 2.55)
        red = int(usage_percent * 2.55)
        return graphics.Color(red, green, 0)

    def get_text_width(self, text: str) -> int:
        """Calculate the width of the text in pixels"""
        return graphics.DrawText(
            self.display.offscreen_canvas,
            self.display.font,
            0,
            0,
            graphics.Color(0, 0, 0),
            text,
        )

    def display_stats(self, stats: Dict[str, str]) -> None:
        """Display system statistics on the matrix"""
        self.display.matrix.Clear()
        y_offset = 10  # lil bit down from the top
        label_colour = graphics.Color(200, 200, 200)

        # Find longest key - display values inline with the end of longest line
        longest_key = max(stats.keys(), key=len)
        key_offset = self.get_text_width(longest_key) + 5  # Add 5 padding

        for stat_name, stat_value in stats.items():
            if "%" in stat_value:
                cpu_percent = float(stat_value.strip("%"))
                value_color = self.get_color_from_usage(cpu_percent)
            else:
                value_color = graphics.Color(120, 120, 120)

            # draw stat name
            graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                1,
                y_offset,
                label_colour,
                stat_name,
            )
            # draw stat value
            graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                key_offset,
                y_offset,
                value_color,
                stat_value,
            )
            y_offset += 10  # line height

        self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
        time.sleep(1)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        while True:
            stats = self.fetch_stats()
            self.display_stats(stats)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
