"""Contains the code for handling the matrix display - interaction with library"""

import textwrap
from typing import Tuple, List
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from matrix.colours import Colours
from matrix.bounding_box import BoundingBox


class MatrixDisplay:
    def __init__(self) -> None:
        """Initialise the MatrixDisplay"""
        # eventually we could pass "config" object in - is it going to
        # change for each applet? unlikely, but possibly.
        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat-pwm"
        options.drop_privileges = False
        options.gpio_slowdown = 1
        options.show_refresh_rate = 0
        self.LINE_SPACING = 2
        self.DRAW_BOUNDING_BOXES = False
        self.load_font()
        self.matrix = RGBMatrix(options=options)
        self.max_chars_per_line = self._get_max_chars_per_line()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.bounding_boxes = {}

    def _get_max_chars_per_line(self) -> int:
        """Calculate the maximum number of characters per line that fit in the matrix width"""
        max_char_width = self.font.CharacterWidth(ord("W"))
        return self.matrix.width // max_char_width

    def get_text_width(self, text: str) -> int:
        """Calculate pixel width of given string.
        This is currently not utilised but may be used later on so leaving it in for now"""
        width = 0
        for char in text:
            width += self.font.CharacterWidth(ord(char))
        return width

    def load_font(self, font_name: str = "5x5.bdf") -> graphics.Font:
        """Load a font, given the font name"""
        font = graphics.Font()
        font.LoadFont(f"matrix/fonts/{font_name}")
        self.font = font

    def draw_progress_bar(
        self,
        progress_percentage: float,
        colour: graphics.Color,
        x: int = 4,
        y: int = 4,
        width: int = 56,
        height: int = 4,
    ) -> None:
        """Draw a progress bar to the canvas"""
        filled_section_width = int(width * progress_percentage / 100)
        # draw the filled bit of the bar
        for dx in range(filled_section_width):
            for dy in range(height):
                self.offscreen_canvas.SetPixel(
                    x + dx, y + dy, colour.red, colour.green, colour.blue
                )
        # now draw the empty part of hte bar
        for dx in range(filled_section_width, width):
            for dy in range(height):
                self.offscreen_canvas.SetPixel(
                    x + dx,
                    y + dy,
                    max(0, colour.red - 175),
                    max(0, colour.green - 175),
                    max(0, colour.blue - 175),
                )

    def _draw_bounding_box(self, bounding_box: BoundingBox, **kwargs) -> None:
        """Draw a bounding box on the matrix display."""
        colour = kwargs.get("colour", Colours.WHITE_MUTED)
        for x in range(bounding_box.x1, bounding_box.x2 + 1):
            self.offscreen_canvas.SetPixel(
                x, bounding_box.y1, colour.red, colour.green, colour.blue
            )
            self.offscreen_canvas.SetPixel(
                x, bounding_box.y2, colour.red, colour.green, colour.blue
            )

        # Draw the left and right vertical lines
        for y in range(bounding_box.y1, bounding_box.y2 + 1):
            self.offscreen_canvas.SetPixel(
                bounding_box.x1, y, colour.red, colour.green, colour.blue
            )
            self.offscreen_canvas.SetPixel(
                bounding_box.x2, y, colour.red, colour.green, colour.blue
            )

    def calculate_bounding_box(
        self, text: str, x: int, y: int, centered: bool = False, line_spacing: int = 2
    ) -> Tuple[BoundingBox, List[str], int]:
        """Calculate the bounding box for the given text."""
        if centered:
            width_available = self.max_chars_per_line
        else:
            width_available = (self.matrix.width - x) // self.font.CharacterWidth(
                ord("W")
            )

        wrapped_text = textwrap.wrap(text, width=width_available)
        total_height = (
            len(wrapped_text) * self.font.height
            + (len(wrapped_text) - 1) * line_spacing
        )
        max_text_width = max(self.get_text_width(line) for line in wrapped_text)

        if centered:
            x = (self.matrix.width - max_text_width) // 2

        bounding_box = BoundingBox(
            x1=x - 1,
            y1=y - self.font.height - 1,
            x2=x + max_text_width - 1,
            y2=y + total_height - self.font.height + 1,
        )

        return bounding_box, wrapped_text, total_height

    def store_bounding_box(
        self, bounding_box: BoundingBox, box_key: Tuple[int, int, str]
    ) -> bool:
        """Check for overlaps and store the bounding box if valid."""
        if any(
            bounding_box.overlaps(existing_box)
            for existing_box in self.bounding_boxes.values()
        ) or not bounding_box.is_within_screen_bounds(
            self.matrix.width, self.matrix.height
        ):
            return False
        else:
            self.bounding_boxes[box_key] = bounding_box
            return True

    def draw_text(self, x: int, y: int, text: str, colour: graphics.Color):
        """Draw text at x,y coords."""
        box_key = (x, y, text)
        width_available = (self.matrix.width - x) // self.font.CharacterWidth(ord("W"))
        wrapped_text = textwrap.wrap(text, width=width_available)

        if box_key in self.bounding_boxes:
            bounding_box = self.bounding_boxes[box_key]
        else:
            bounding_box, wrapped_text, total_height = self.calculate_bounding_box(
                text, x, y
            )
            if not self.store_bounding_box(bounding_box, box_key):
                # display red bounding box to indicate missing content
                self._draw_bounding_box(bounding_box, colour=Colours.RED)
                return

        if self.DRAW_BOUNDING_BOXES:
            self._draw_bounding_box(bounding_box)

        for line in wrapped_text:
            graphics.DrawText(self.offscreen_canvas, self.font, x, y, colour, line)
            y += self.font.height + self.LINE_SPACING

    def draw_centered_text(self, text: str, color: graphics.Color, **kwargs) -> None:
        """Draw centered text to the matrix."""
        wrapped_text = textwrap.wrap(text, self.max_chars_per_line)
        start_y = kwargs.get(
            "start_y",
            (
                self.matrix.height
                - len(wrapped_text) * (self.font.height + self.LINE_SPACING)
            )
            // 2
            + self.font.height,
        )
        box_key = ("c", "c", text)

        if box_key in self.bounding_boxes:
            bounding_box = self.bounding_boxes[box_key]
        else:
            bounding_box, wrapped_text, total_height = self.calculate_bounding_box(
                text, 0, start_y, centered=True
            )
            if not self.store_bounding_box(bounding_box, box_key):
                self._draw_bounding_box(bounding_box, colour=Colours.RED)
                return

        if self.DRAW_BOUNDING_BOXES:
            self._draw_bounding_box(bounding_box)

        for line in wrapped_text:
            text_width = self.get_text_width(line)
            x = (self.matrix.width - text_width) // 2
            graphics.DrawText(self.offscreen_canvas, self.font, x, start_y, color, line)
            start_y += self.font.height + self.LINE_SPACING

    def clear(self):
        self.bounding_boxes.clear()
        self.offscreen_canvas.Clear()

    def show_message(
        self, message: str = "Loading...", message_type: str = "loading"
    ) -> None:
        """Show a message of a given type e.g. error"""
        self.clear()

        # Determine color based on message_type
        if message_type == "error":
            color = Colours.RED
        else:
            color = Colours.YELLOW

        self.draw_centered_text(message, color)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
