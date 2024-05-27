"""Contains the code for handling the matrix display - interaction with library"""

import textwrap
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from matrix.colours import Colours


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
        self.load_font()
        self.matrix = RGBMatrix(options=options)
        self.max_chars_per_line = self._get_max_chars_per_line()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

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

    def draw_centered_text(
        self, text: str, color: graphics.Color, line_spacing: int = 2, **kwargs
    ) -> None:
        """Draw centered text to the matrix
        kwargs:
            start_y: where to draw the text on y axis - if not specified then it will be centered
        """
        # Split the message into lines if it's too long
        wrapped_text = textwrap.wrap(text, width=self.max_chars_per_line) 
        total_height = len(wrapped_text) * (
            self.font.height + line_spacing
        )  # Assuming 2 pixels spacing between lines

        # pass start_y to change where it starts on Y axis - if not specified then centre.
        # this is because we don't always want to centre on both axis
        start_y = kwargs.get(
            "start_y", (self.matrix.height - total_height) // 2 + self.font.height
        )

        for line in wrapped_text:
            text_width = self.get_text_width(line)
            x = (self.matrix.width - text_width) // 2
            graphics.DrawText(self.offscreen_canvas, self.font, x, start_y, color, line)
            start_y += self.font.height + 2

    def show_message(
        self, message: str = "Loading...", message_type: str = "loading"
    ) -> None:
        """Show a message of a given type e.g. error"""
        self.offscreen_canvas.Clear()

        # Determine color based on message_type
        if message_type == "error":
            color = Colours.RED
        else:
            color = Colours.YELLOW

        self.draw_centered_text(message, color)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
