import time
import requests
import json
from typing import Tuple, Optional
from PIL import Image
from matrix.matrix_display import MatrixDisplay, graphics
from applets.base_applet import Applet


class HelldiversKillCounter(Applet):
    """Helldivers Kill Counter Definition"""
    def __init__(self, display: MatrixDisplay) -> None:
        """Initialisation function"""
        super().__init__("Helldivers Kill Counter", display)
        self.image_bugs = self.load_and_convert_image('resources/images/bugs.png')
        self.image_bots = self.load_and_convert_image('resources/images/bots.png')
        # start displaying terminid kill count
        self.current_image = self.image_bugs
        self.last_switch_time = time.time()
        self.last_fetch_time = time.time()
        # fetch initial values at build time
        self.bugs, self.bots = self.fetch_data()

    def load_and_convert_image(self, image_path: str) -> Image:
        """Load an image from a filepath and convert it into a displayable format"""
        image = Image.open(image_path)
        image = image.convert("RGBA")
        data = image.getdata()

        new_data = []
        for item in data:
            # this conditional is horrific - surely a better way to do this..
            if item[0] in list(range(200, 256)) and \
                item[1] in list(range(200, 256)) and \
                    item[2] in list(range(200, 256)):
                if "bugs" in image_path:
                    new_data.append((255, 165, 0, item[3]))  # orange
                elif "bots" in image_path:
                    new_data.append((255, 30, 0, item[3]))  # red
            else:
                new_data.append(item)

        image.putdata(new_data)
        image = image.resize((32, 32))
        return image

    def fetch_data(self) -> Tuple[Optional[str], Optional[str]]:
        """Fetch bug and bot kill data from API"""
        root = "https://api.helldivers2.dev"
        try:
            response = requests.get(f"{root}/raw/api/Stats/war/801/summary")
            response.raise_for_status()
            data = response.json()
            bugs = str(data["galaxy_stats"]["bugKills"])
            bots = str(data["galaxy_stats"]["automatonKills"])
            self.log(f"Fetched data from the HellDivers API - bug count : bot count = {bugs} : {bots}")
            return bugs, bots
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            self.log("There was an error fetching the helldivers data...")
            return None, None

    def update_display(self, image: Image, text: str) -> None:
        """Update the matrix display"""
        self.display.matrix.Clear()
        # Halfway accross the X axis, 1/4 down from the top on Y axis
        x_offset = (self.display.matrix.width - 32) // 2
        y_offset = (self.display.matrix.height - 32) // 4
        self.display.matrix.SetImage(image.convert("RGB"), x_offset, y_offset)

        text_width = graphics.DrawText(
            self.display.matrix, self.display.font, 0, 0, graphics.Color(255, 255, 255), text
        )
        text_x = (self.display.matrix.width - text_width) // 2
        text_y = y_offset + 32 + 10

        graphics.DrawText(
            self.display.matrix, self.display.font, text_x, text_y, graphics.Color(255, 255, 255), text
        )

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        while True:
            current_time = time.time()

            if current_time - self.last_fetch_time >= 10:
                self.bugs, self.bots = self.fetch_data()
                self.last_fetch_time = current_time

            if current_time - self.last_switch_time >= 5:
                self.current_image = self.image_bots if self.current_image == self.image_bugs else self.image_bugs
                current_text = self.bugs if self.current_image == self.image_bugs else self.bots
                self.update_display(self.current_image, current_text)
                self.last_switch_time = current_time

            time.sleep(1)

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
        # need to handle destruction here..
        # @chadders recall our conversation about memory management
        # and see TODO in README.md
