import time
from textwrap import wrap
from typing import List
from applets.base_applet import Applet
from matrix.matrix_display import MatrixDisplay
from matrix.colours import Colours
from input_handlers.base_input_handler import BaseInputHandler
from applets.applet_information_viewer.main import AppletInformationViewer
from applets.settings_applet.main import SettingsApplet
from applets.idle_applet.main import IdleApplet

class MasterApp(Applet):
    def __init__(self, **kwargs) -> None:
        """Initialise a new MasterApp Instance with the provided display, input handler, and applet manager."""
        super().__init__("MasterApp", **kwargs)
        self.applet_manager = kwargs.get("applet_manager")
        self.MAX_ITEMS_PER_PAGE = 2
        self.IDLE_SCREEN_THRESHOLD_SECONDS = 300
        self.applets = self.applet_manager.get_applets_information()
        self.current_index = 0
        self.page_index = 0
        self.last_input_time = time.time()

    @staticmethod
    def log(message: str) -> None:
        """Display an identifiable logging message."""
        print(f"[LOG] [Menu] '{message}'")

    @staticmethod
    def error(message: str) -> None:
        """Display an identifiable error message."""
        print(f"[ERROR] [Menu] '{message}'")

    @staticmethod
    def wrap_menu_items_text(text: str, width: int) -> List[str]:
        """Wrap text to a specified width and add a marker at the start of the first line."""
        wrapped_lines = wrap(text, width)
        if wrapped_lines:
            wrapped_lines[0] = f"* {wrapped_lines[0]}"
            for i in range(1, len(wrapped_lines)):
                wrapped_lines[i] = f"  {wrapped_lines[i]}"
        return wrapped_lines

    def display_menu(self) -> None:
        """Display the menu system on the RGB Matrix."""
        self.display.clear()
        y_offset = 10
        start_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        end_index = start_index + self.MAX_ITEMS_PER_PAGE
        current_page_applets = list(self.applets.keys())[start_index:end_index]

        for i, applet in enumerate(current_page_applets):
            i += start_index
            color = Colours.RED if i == self.current_index else Colours.WHITE_MUTED
            wrapped_text = self.wrap_menu_items_text(applet, self.display.max_chars_per_line - 2)
            for line in wrapped_text:
                self.display.draw_text(1, y_offset, line, color)
                y_offset += 10
            y_offset += 5

        total_pages = (len(self.applets) + self.MAX_ITEMS_PER_PAGE - 1) // self.MAX_ITEMS_PER_PAGE
        page_indicator_text = f"[{self.page_index + 1}/{total_pages}]"
        indicator_color = Colours.WHITE_MUTED
        text_length = self.display.get_text_width(page_indicator_text)
        text_x = (self.display.matrix.width - text_length) // 2
        text_y = self.display.matrix.height - 4
        self.display.draw_text(text_x, text_y, page_indicator_text, indicator_color)

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)

    def navigate_menu(self) -> None:
        """Change the current index, representing menu navigation."""
        latest_inputs = self.input_handler.get_latest_inputs()
        if any(latest_inputs.values()):
            self.last_input_time = time.time()
        if latest_inputs["up_pressed"]:
            self.current_index = (self.current_index - 1) % len(self.applets)
        elif latest_inputs["down_pressed"]:
            self.current_index = (self.current_index + 1) % len(self.applets)
        elif latest_inputs["left_pressed"]:
            if self.page_index > 0:
                self.page_index -= 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        elif latest_inputs["right_pressed"]:
            if (self.page_index + 1) * self.MAX_ITEMS_PER_PAGE < len(self.applets):
                self.page_index += 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        self.page_index = self.current_index // self.MAX_ITEMS_PER_PAGE

    def create_applet_info_applet(self) -> AppletInformationViewer:
        """Open the view applet with the selected applet information."""
        selected_applet_name = list(self.applets.keys())[self.current_index]
        selected_applet_config_json = self.applets[selected_applet_name]
        selected_applet_config_json["name"] = selected_applet_name
        return AppletInformationViewer(
            display=self.display,
            input_handler=self.input_handler,
            applet_config=selected_applet_config_json,
        )

    def create_settings_applet(self) -> SettingsApplet:
        """Open the settings applet."""
        return SettingsApplet(display=self.display, input_handler=self.input_handler)

    def launch_applet(self, applet: Applet) -> None:
        """Launch the given applet, handling start and stop operations."""
        try:
            self.display.clear()
            applet.start()
        except KeyboardInterrupt:
            pass
        finally:
            applet.stop()
            self.display.clear()
            self.input_handler.exit_requested = False
            self.last_input_time = time.time()

    def create_selected_applet(self) -> Applet:
        """Select and instantiate the applet based on the current index."""
        applet_name = list(self.applets.keys())[self.current_index]
        self.display.show_message(f"Loading {applet_name}...", "loading")
        return self.applet_manager.get_applet_instance_by_name(applet_name)

    def start(self) -> None:
        """Run the master application, handling menu display and navigation."""
        while True:
            self.display_menu()
            self.navigate_menu()
            if self.input_handler.select_pressed:
                self.launch_applet(self.create_selected_applet())
            if self.input_handler.x_pressed:
                self.launch_applet(self.create_applet_info_applet())
            if self.input_handler.y_pressed:
                self.launch_applet(self.create_settings_applet())

            if time.time() - self.last_input_time > self.IDLE_SCREEN_THRESHOLD_SECONDS:
                idle_applet = IdleApplet(display=self.display, input_handler=self.input_handler)
                self.launch_applet(idle_applet)

    def stop(self) -> None:
        """Stop the applet and clear the display."""
        self.log("Stopping")
        self.display.clear()
