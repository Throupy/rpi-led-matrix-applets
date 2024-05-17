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

    def display_stats(self, stats: Dict[str, str]) -> None:
        """Display system statistics on the matrix"""
        self.display.matrix.Clear()
        y_offset = 10  # lil bit down from the top
        colour = graphics.Color(200, 200, 200)

        for stat_name, stat_value in stats.items():
            text = f" {stat_name}:{stat_value}"
            graphics.DrawText(
                self.display.offscreen_canvas, self.display.font, 1, y_offset, colour, text
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
