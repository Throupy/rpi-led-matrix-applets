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
        options.hardware_mapping = "adafruit-hat"
        self.matrix = RGBMatrix(options=options)
        # no font specified - a default font of tom-thumb.bdf (it's nice)
        self.font = self.load_font()

    def load_font(self, font_name: str = "tom-thumb.bdf") -> graphics.Font:
        """Load a font, given the font name"""
        font = graphics.Font()
        font.LoadFont(f"resources/bdf/{font_name}")
        return font

    def show_message(self, message: str = "Loading...", message_type: str = "loading") -> None:
        """Show a message of a given type e.g. error"""
        self.matrix.Clear()
        offscreen_canvas = self.matrix.CreateFrameCanvas()

        # Determine color based on message_type
        if message_type == "error":
            color = graphics.Color(220, 0, 0)  # Red color for error message
        else:
            color = graphics.Color(220, 220, 0)  # Yellow color for loading message

        # Split the message into lines if it's too long
        wrapped_text = textwrap.wrap(message, width=10)  # Adjust width as necessary

        # Calculate starting Y position to center the text vertically
        line_height = 8  # Approximate height of one line of text, adjust if necessary
        total_text_height = line_height * len(wrapped_text)
        text_y = (self.matrix.height - total_text_height) // 2

        # Draw each line of text
        for line in wrapped_text:
            text_length = graphics.DrawText(offscreen_canvas, self.font, 0, 0, color, line)
            text_x = (self.matrix.width - text_length) // 2
            graphics.DrawText(offscreen_canvas, self.font, text_x, text_y, color, line)
            text_y += line_height

        self.matrix.SwapOnVSync(offscreen_canvas)
