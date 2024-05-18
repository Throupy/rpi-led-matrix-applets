"""Contains the code for handling the matrix display - interaction with library"""

import textwrap
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


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
        self.matrix = RGBMatrix(options=options)
        # no font specified - a default font of tom-thumb.bdf (it's nice)
        self.font = self.load_font()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

        # Define some preset colors
        self.COLOR_BLACK = graphics.Color(0, 0, 0)
        self.COLOR_WHITE = graphics.Color(255, 255, 255)
        self.COLOR_RED = graphics.Color(255, 0, 0)
        self.COLOR_GREEN = graphics.Color(0, 255, 0)
        self.COLOR_BLUE = graphics.Color(0, 0, 255)
        self.COLOR_CYAN = graphics.Color(0, 255, 255)
        self.COLOR_MAGENTA = graphics.Color(255, 0, 255)
        self.COLOR_YELLOW = graphics.Color(255, 255, 0)
        self.COLOR_ORANGE = graphics.Color(255, 165, 0)
        self.COLOR_PURPLE = graphics.Color(128, 0, 128)
        self.COLOR_PINK = graphics.Color(255, 192, 203)
        self.COLOR_BROWN = graphics.Color(165, 42, 42)
        self.COLOR_GRAY = graphics.Color(128, 128, 128)
        self.COLOR_LIGHT_GRAY = graphics.Color(211, 211, 211)
        self.COLOR_DARK_GRAY = graphics.Color(169, 169, 169)

    def load_font(self, font_name: str = "tom-thumb.bdf") -> graphics.Font:
        """Load a font, given the font name"""
        font = graphics.Font()
        font.LoadFont(f"matrix/fonts/{font_name}")
        return font

    def _get_text_width(self, font: graphics.Font, text: str) -> int:
        """Calculate pixel width of given string.
        This is currently not utilised but may be used later on so leaving it in for now"""
        width = 0
        for char in text:
            width += font.CharacterWidth(ord(char))
        return width

    def _draw_centered_text(
        self, text: str, font: graphics.Font, color: graphics.Color, line_spacing: int = 2
    ) -> None:
        # Split the message into lines if it's too long
        wrapped_text = textwrap.wrap(text, width=10)  # Adjust width as necessary
        total_height = len(wrapped_text) * (
            font.height + line_spacing
        )  # Assuming 2 pixels spacing between lines
        start_y = (self.matrix.height - total_height) // 2 + font.height

        for line in wrapped_text:
            text_width = graphics.DrawText(
                self.offscreen_canvas, font, 0, start_y, self.COLOR_BLACK, line
            )
            # ^ Alternatively we could use the line below to reduce draw calls
            # (may be less CPU intensive when dealing with large amounts of DrawText calls)
            # text_width = self._get_text_width(font, line)
            x = (self.matrix.width - text_width) // 2
            graphics.DrawText(self.offscreen_canvas, font, x, start_y, color, line)
            start_y += font.height + 2

    def show_message(self, message: str = "Loading...", message_type: str = "loading") -> None:
        """Show a message of a given type e.g. error"""
        self.matrix.Clear()
        self.offscreen_canvas.Clear()

        # Determine color based on message_type
        if message_type == "error":
            color = self.COLOR_RED
        else:
            color = self.COLOR_YELLOW

        self._draw_centered_text(message, self.font, color)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
