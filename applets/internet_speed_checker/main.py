import urllib.request
import time
import threading
from rgbmatrix import graphics
from matrix.colours import Colours
from applets.base_applet import Applet
import signal


class SpeedCheck(Applet):
    """SpeedCheck applet definition"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Internet Speed", *args, **kwargs)

        self.test_running = False  # Initialize to False
        # URL to download test file (choose a file that is reasonably sized for the test)
        self.test_url = "http://speedtest.ftp.otenet.gr/files/test100Mb.db"
        self.update_interval = 0.5  # update every 0.5 seconds
        self.download_speed = 0.0
        self.upload_speed = 0.0

        # Create a thread to download the file
        self.download_thread = None

        # Placeholder for the original signal handler
        self.original_signal_handler = None

    def signal_handler(self):
        """Handle SIGINT (CTRL+C) for graceful shutdown"""
        self.log("Caught SIGINT, stopping applet gracefully (terminating threads)...")
        raise KeyboardInterrupt

    def download_file(self):
        """Download the given file and calculate the download speed"""
        start_time = time.time()
        bytes_downloaded = 0

        while self.test_running:
            with urllib.request.urlopen(self.test_url) as response:
                while self.test_running:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    bytes_downloaded += len(chunk)
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= self.update_interval:
                        self.download_speed = bytes_downloaded / elapsed_time
                        start_time = time.time()
                        bytes_downloaded = 0

    @staticmethod
    def get_speed_color(speed: float) -> graphics.Color:
        """Calculate color based on download speed"""
        # red - 0, green - 50, green - 50+
        if speed > 50:
            return graphics.Color(0, 255, 0)
        red = int((50 - speed) * 2.55)
        green = int(speed * 2.55)
        return graphics.Color(red, green, 0)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.test_running = True

        # Save the original signal handler and set the new one
        self.original_signal_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Create a thread to download the file
        self.download_thread = threading.Thread(target=self.download_file)

        # Start the threads
        self.download_thread.start()

        self.display.offscreen_canvas.Clear()

        while self.test_running and not self.input_handler.exit_requested:
            # Calculate speed in megabits per second
            speed_mbps = (self.download_speed / (1024 * 1024)) * 8
            text = f"{speed_mbps:.2f} Mb/s"
            self.display.offscreen_canvas.Clear()
            # Calculate colour based on speed
            colour = self.get_speed_color(speed_mbps)
            text_width = graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                0,
                0,
                Colours.WHITE_NORMAL,
                text,
            )

            text_x = (self.display.matrix.width - text_width) // 2
            text_y = self.display.matrix.height / 2

            graphics.DrawText(
                self.display.offscreen_canvas,
                self.display.font,
                text_x,
                text_y,
                colour,
                text,
            )

            self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
                self.display.offscreen_canvas
            )

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.test_running = False

        # Restore the original signal handler
        if self.original_signal_handler:
            signal.signal(signal.SIGINT, self.original_signal_handler)

        # Wait for the threads to finish
        if self.download_thread:
            self.download_thread.join()

        self.display.matrix.Clear()
        self.display.offscreen_canvas.Clear()
