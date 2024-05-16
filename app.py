from typing import Dict, List, Type
from textwrap import wrap
from matrix.matrix_display import MatrixDisplay, graphics
from applets.helldivers_counter import HelldiversKillCounter
from applets.tarkov_price_tracker import TarkovPriceTracker


class MasterApp:
    """Master Application - will control all functionality"""
    def __init__(self, applets: Dict[str, Type], display: MatrixDisplay) -> None:
        """Initialise a new MasterApp Instance"""
        # Initialize with a dictionary of applet names to classes
        # so we don't build the app until it's selected
        self.applets = applets
        self.current_index = 0
        self.display = display

    def wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to a specified width and add a marker at the start of the first line."""
        wrapped_lines = wrap(text, width)
        if wrapped_lines:
            wrapped_lines[0] = f"* {wrapped_lines[0]}"
        return wrapped_lines

    def display_menu(self) -> None:
        """Display the menu system on the RGB Matrix"""
        self.display.matrix.Clear()
        y_offset = 10  # Start a bit down from the top
        for i, applet in enumerate(self.applets.keys()):
            color = graphics.Color(255, 0, 0) if i == self.current_index else graphics.Color(100, 100, 100)
            wrapped_text = self.wrap_text(applet, 14)  # this is width
            for line in wrapped_text:
                graphics.DrawText(self.display.matrix, self.display.font, 1, y_offset, color, line)
                y_offset += 10  # this is for line height
            y_offset += 5  # Additional spacing between applets

    def navigate_menu(self, direction: str) -> None:
        """Change current index, representing menu navigation"""
        # TODO: Nav system only temporary.
        if direction == "up":
            self.current_index = (self.current_index + 1) % len(self.applets)
        elif direction == "down":
            self.current_index = (self.current_index - 1) % len(self.applets)

    def select_applet(self) -> None:
        """Select and build (instantiate) the selected applet"""
        self.display.matrix.Clear()
        applet_name = list(self.applets.keys())[self.current_index]
        self.display.show_message(f"Loading {applet_name}...", "loading")

        # Instantiate the selected applet
        AppletClass = self.applets[applet_name]
        selected_applet = AppletClass(self.display)

        # This try, except, finally block allows us to CTRL+C out of the applet and return to the menu.
        try:
            selected_applet.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.display.matrix.Clear()

    def run(self) -> None:
        """Run the master application"""
        # TODO: This is only temporary, @Chadders you said something about a controller system?
        while True:
            self.display_menu()
            command = input("Enter command (up, down, select, exit): ")
            if command == "up":
                self.navigate_menu("up")
            elif command == "down":
                self.navigate_menu("down")
            elif command == "select":
                self.select_applet()
            elif command == "exit":
                break


if __name__ == "__main__":
    # Going to pass this into the MasterApp
    # this means nothing gets instantiated until we select it
    # inside MasterApp.select_applet(). This is very good for
    # performance - app starts almost instantly.
    applets = {
        "Tarkov Price Tracker": TarkovPriceTracker,
        "Helldivers Kill Counter": HelldiversKillCounter
    }
    # here is our ONLY matrix display ever instantiated - will be passed through
    display = MatrixDisplay()
    display.show_message("Building Menu System...", "loading")
    master_app = MasterApp(applets, display)
    master_app.run()