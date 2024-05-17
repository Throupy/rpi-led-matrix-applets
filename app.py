import os
import psutil
import time
import threading
import sys
import json
import importlib.util
from typing import Dict, List, Type
from textwrap import wrap
from matrix.matrix_display import MatrixDisplay, graphics
from applets.base_applet import Applet


class MasterApp:
    """Master Application - will control all functionality"""

    def __init__(self, display: MatrixDisplay, applets_root_directory: str) -> None:
        """Initialise a new MasterApp Instance"""
        # Initialize with a dictionary of applet names to classes
        # so we don't build the app until it's selected
        self.applets_root_directory = applets_root_directory
        self.MAX_ITEMS_PER_PAGE = 2
        self.applets = self.get_applets_information()
        self.current_index = 0
        self.page_index = 0
        self.display = display

    def wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to a specified width and add a marker at the start of the first line."""
        wrapped_lines = wrap(text, width)
        if wrapped_lines:
            wrapped_lines[0] = f"* {wrapped_lines[0]}"
            for i in range(1, len(wrapped_lines)):
                wrapped_lines[i] = f"  {wrapped_lines[i]}"
        return wrapped_lines

    def display_menu(self) -> None:
        """Display the menu system on the RGB Matrix"""
        self.display.matrix.Clear()
        y_offset = 10  # Start a bit down from the top
        start_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        end_index = start_index + self.MAX_ITEMS_PER_PAGE
        # get applets for this current page of menu
        current_page_applets = list(self.applets.keys())[start_index:end_index]

        for i, applet in enumerate(current_page_applets):
            # this is because first applet on second page (assuming 2 per page) would have index
            # 0 in this loop, but 2 in the self.applets.
            i += start_index
            color = (
                graphics.Color(255, 0, 0)
                if i == self.current_index
                else graphics.Color(100, 100, 100)
            )
            wrapped_text = self.wrap_text(applet, 14)  # this is width
            for line in wrapped_text:
                graphics.DrawText(self.display.matrix, self.display.font, 1, y_offset, color, line)
                y_offset += 10  # this is for line height
            y_offset += 5  # Additional spacing between applets

        # dislplay current page and total pages e.g. [1/2] at the bottom of the matrix
        total_pages = (len(self.applets) + self.MAX_ITEMS_PER_PAGE - 1) // self.MAX_ITEMS_PER_PAGE
        page_indicator_text = f"[{self.page_index + 1}/{total_pages}]"
        indicator_color = graphics.Color(100, 100, 100)
        text_length = graphics.DrawText(
            self.display.matrix, self.display.font, 0, 0, indicator_color, page_indicator_text
        )
        text_x = (self.display.matrix.width - text_length) // 2
        text_y = self.display.matrix.height - 4  # near the bottom
        graphics.DrawText(
            self.display.matrix,
            self.display.font,
            text_x,
            text_y,
            indicator_color,
            page_indicator_text,
        )

    def navigate_menu(self, direction: str) -> None:
        """Change current index, representing menu navigation"""
        # TODO: Nav system only temporary.
        if direction == "up":
            self.current_index = (self.current_index - 1) % len(self.applets)
        elif direction == "down":
            self.current_index = (self.current_index + 1) % len(self.applets)
        elif direction == "left":
            if self.page_index > 0:
                self.page_index -= 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        elif direction == "right":
            if (self.page_index + 1) * self.MAX_ITEMS_PER_PAGE < len(self.applets):
                self.page_index += 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        self.page_index = self.current_index // self.MAX_ITEMS_PER_PAGE

    def get_applets_information(self) -> Dict[str, Dict]:
        """Retrieve information about applets from the config file in each applet's directory"""
        # List to hold the names of folders
        folders = []
        # List of found applets and their information found in the config.json file
        applets = {}

        # os.listdir() returns a list of all files and folders in the specified directory
        for item in os.listdir(self.applets_root_directory):
            # os.path.join() creates a full path by joining directory and item
            full_path = os.path.join(self.applets_root_directory, item)
            # os.path.isdir() checks if the full path is a directory
            if os.path.isdir(full_path) and item != "__pycache__":
                folders.append(full_path)

        for folder in folders:
            config_path = os.path.join(folder, "config.json")
            try:
                with open(config_path, "r") as file:
                    config_data = json.load(file)
                    name = config_data.get("name", "No Name Provided")
                    # Extracting the desired fields
                    applets[name] = {
                        "description": config_data.get("description", "No Description Provided"),
                        "version": config_data.get("version", "No Version Provided"),
                        "author": config_data.get("author", "No Author Provided"),
                        "path": folder,
                        "class_name": config_data.get("class_name", "No Classname Provided"),
                        "module_path": os.path.join(folder, "main.py"),
                    }

            except FileNotFoundError:
                print(f"Config file not found in {folder}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON in {folder}")

        return applets

    def dynamic_import_applet(self, module_path: str, module_name: str) -> Applet:
        """Dynamically import a module given its file path and module name."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def select_applet(self) -> None:
        """Select and build (instantiate) the selected applet"""
        self.display.matrix.Clear()
        applet_name = list(self.applets.keys())[self.current_index]
        self.display.show_message(f"Loading {applet_name}...", "loading")

        # Dynamically import selected applet

        selected_applet = None
        # Instantiate the selected applet
        # AppletClass = self.applets[applet_name]
        module_path = self.applets[applet_name]["module_path"]
        class_name = self.applets[applet_name]["class_name"]
        AppletClass = self.dynamic_import_applet(module_path, class_name)

        if hasattr(AppletClass, class_name):
            selected_applet_type = getattr(AppletClass, class_name)
            # Instantiate the applet's main class
            # with the required parameter 'self.display' (reference to the matrix)
            selected_applet = selected_applet_type(self.display)
        else:
            print(f"The class '{class_name}' is not found in the module '{module_path}'")

        # This try, except, finally block allows us to
        # CTRL+C out of the applet and return to the menu.
        try:
            selected_applet.start()
        except KeyboardInterrupt:
            print("KBI Detected")
            pass
        finally:
            self.display.matrix.Clear()

    def run(self) -> None:
        """Run the master application"""
        # TODO: This is only temporary, @Chadders you said something about a controller system?
        # DONE: Add directory based applets with separate config files, and dynamic applet importing
        self.get_applets_information()
        while True:
            self.display_menu()
            command = input("Enter command (up, down, left, right, select, exit): ")
            if command == "up":
                self.navigate_menu("up")
            elif command == "down":
                self.navigate_menu("down")
            elif command == "left":
                self.navigate_menu("left")
            elif command == "right":
                self.navigate_menu("right")
            elif command == "select":
                self.select_applet()
            elif command == "exit":
                break


if __name__ == "__main__":
    # Get the directory where the current script is located
    current_script_path = os.path.realpath(__file__)
    current_script_directory = os.path.dirname(current_script_path)

    # Define the target subdirectory (change this if you have a differently named applets directory)
    applets_subdirectory = "applets"

    # Construct the full path to the target subdirectory
    applets_root_directory = os.path.join(current_script_directory, applets_subdirectory)

    # here is our ONLY matrix display ever instantiated - will be passed through
    display = MatrixDisplay()
    display.show_message("Building Menu System...", "loading")
    master_app = MasterApp(display, applets_root_directory)
    master_app.run()
