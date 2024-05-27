"""Hell divers kill counter applet implementation"""

import time
import os
import requests
from typing import Tuple, Optional
from PIL import Image
from matrix.matrix_display import graphics
from matrix.colours import Colours
from applets.base_applet import Applet


class HelldiversKillCounter(Applet):
    """Helldivers Kill Counter Definition"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Helldivers Kill Counter", *args, **kwargs)
        self.image_bugs = self.load_and_convert_image("bugs.png")
        self.image_bots = self.load_and_convert_image("bots.png")
        # intialise variables
        self.bugs, self.bots = self.fetch_data()
        # start displaying terminid kill count
        self.current_image = self.image_bugs
        # add a -5 to hit the first conditinal in update_display()
        self.last_switch_time = time.time() - 5
        self.last_fetch_time = time.time()

    def load_and_convert_image(self, image_name: str) -> Image:
        """Load an image from a filepath and convert it into a displayable format"""
        image_path = os.path.join(self.resources_directory, image_name)
        bmp_path = image_path.replace(".png", ".bmp")
        if os.path.exists(bmp_path):
            image = Image.open(bmp_path)
        else:
            image = Image.open(image_path)
            image = image.convert("RGBA")
            data = image.getdata()

            new_data = []
            for item in data:
                # this conditional is horrific - surely a better way to do this..
                if (
                    item[0] in list(range(200, 256))
                    and item[1] in list(range(200, 256))
                    and item[2] in list(range(200, 256))
                ):
                    if "bugs" in image_path:
                        new_data.append(
                            (
                                Colours.TERMINID.red,
                                Colours.TERMINID.green,
                                Colours.TERMINID.blue,
                                item[3],
                            )
                        )  # orange
                    elif "bots" in image_path:
                        new_data.append(
                            (
                                Colours.AUTOMATON.red,
                                Colours.AUTOMATON.green,
                                Colours.AUTOMATON.blue,
                                item[3],
                            )
                        )  # red
                else:
                    new_data.append(item)

            image.putdata(new_data)
            image = image.resize((32, 32))
            try:
                image.save(bmp_path)
            except PermissionError:
                print(
                    f"Permission denied: Unable to save to {bmp_path}. Check perms and retry"
                )
                raise
        return image

    def fetch_data(self) -> Tuple[Optional[str], Optional[str]]:
        """Fetch bug and bot kill data from API"""
        root = "https://api.helldivers2.dev"
        try:
            response = requests.get(f"{root}/raw/api/Stats/war/801/summary")
            data = response.json()
            bugs = str(data["galaxy_stats"]["bugKills"])
            bots = str(data["galaxy_stats"]["automatonKills"])
            self.log(
                f"Fetched data from the HellDivers API - bug count : bot count = {bugs} : {bots}"
            )
            return bugs, bots
        except requests.exceptions.RequestException:
            self.display.show_message("Network error. Check your connection", "error")
            time.sleep(2)
            self.input_handler.exit_requested = True
            return None, None

    def update_display(self, image: Image, text: str) -> None:
        """Update the matrix display"""
        self.display.matrix.Clear()
        # Halfway accross the X axis, 1/4 down from the top on Y axis
        x_offset = (self.display.matrix.width - 32) // 2
        y_offset = (self.display.matrix.height - 32) // 4
        self.display.offscreen_canvas.SetImage(image.convert("RGB"), x_offset, y_offset)

        # 75% down from the top (make room for image)
        offset_y = (self.display.matrix.height // 4) * 3 

        self.display.draw_centered_text(
            text,
            Colours.WHITE_NORMAL,
            start_y=offset_y
        )

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
            self.display.offscreen_canvas
        )

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.offscreen_canvas.Clear()
        # when the app is "loaded from memory" it messes with previous error handlign
        # to prevent this, I have added a presence check on self.bots / self.bugs
        if not self.bots or not self.bugs:
            self.bugs, self.bots = self.fetch_data()
        while not self.input_handler.exit_requested:
            current_time = time.time()
            latest_inputs = self.input_handler.get_latest_inputs()
            if current_time - self.last_fetch_time >= 10:
                self.bugs, self.bots = self.fetch_data()
                self.last_fetch_time = current_time

            if (
                current_time - self.last_switch_time >= 5
                or latest_inputs["select_pressed"]
            ):
                self.current_image = (
                    self.image_bots
                    if self.current_image == self.image_bugs
                    else self.image_bugs
                )
                current_text = (
                    self.bugs if self.current_image == self.image_bugs else self.bots
                )
                self.update_display(self.current_image, current_text)
                self.last_switch_time = current_time

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
        self.display.offscreen_canvas.Clear()
        # need to handle destruction here..
        # @chadders recall our conversation about memory management
        # and see TODO in README.md
