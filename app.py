import os
import sys
import time
import json
import importlib.util
import evdev
from typing import Dict, List
from textwrap import wrap
from matrix.matrix_display import MatrixDisplay, graphics
from matrix.colours import Colours
from applets.base_applet import Applet
from applets.applet_information_viewer.main import AppletInformationViewer
from applets.settings_applet.main import SettingsApplet
from input_handlers.xbox_controller import Controller
from input_handlers.keyboard import Keyboard
from input_handlers.base_input_handler import BaseInputHandler


class MasterApp:
    """Master Application - will control all functionality"""

    def __init__(self, _display: MatrixDisplay, _input_handler: BaseInputHandler, _applets_root_directory: str) -> None:
        """Initialise a new MasterApp Instance"""
        # Initialize with a dictionary of applet names to classes
        # so we don't build the app until it's selected
        self.applets_root_directory = _applets_root_directory
        self.MAX_ITEMS_PER_PAGE = 2
        self.applets = self.get_applets_information()
        self.current_index = 0
        self.page_index = 0
        self.display = _display
        self.input_handler = _input_handler

    @staticmethod
    def log(message: str) -> None:
        """Display an identifiable logging message"""
        print(f"[LOG] [Menu] '{message}'")

    @staticmethod
    def error(message: str) -> None:
        """Display an identifiable error message"""
        print(f"[ERROR] [Menu] '{message}'")

    @staticmethod
    def wrap_text(text: str, width: int) -> List[str]:
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
                Colours.RED
                if i == self.current_index
                else Colours.WHITE_MUTED
            )
            wrapped_text = self.wrap_text(applet, 12)  # this is width
            for line in wrapped_text:
                graphics.DrawText(self.display.matrix, self.display.font, 1, y_offset, color, line)
                y_offset += 10  # this is for line height
            y_offset += 5  # Additional spacing between applets

        # dislplay current page and total pages e.g. [1/2] at the bottom of the matrix
        total_pages = (len(self.applets) + self.MAX_ITEMS_PER_PAGE - 1) // self.MAX_ITEMS_PER_PAGE
        page_indicator_text = f"[{self.page_index + 1}/{total_pages}]"
        indicator_color = Colours.WHITE_MUTED
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

    def navigate_menu(self) -> None:
        """Change current index, representing menu navigation"""
        latest_inputs = self.input_handler.get_latest_inputs()
        #print(latest_inputs)
        if latest_inputs['up_pressed']:
            self.current_index = (self.current_index - 1) % len(self.applets)
        elif latest_inputs['down_pressed']:
            self.current_index = (self.current_index + 1) % len(self.applets)
        elif latest_inputs['left_pressed']:
            if self.page_index > 0:
                self.page_index -= 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        elif latest_inputs['right_pressed']:
            if (self.page_index + 1) * self.MAX_ITEMS_PER_PAGE < len(self.applets):
                self.page_index += 1
                self.current_index = self.page_index * self.MAX_ITEMS_PER_PAGE
        self.page_index = self.current_index // self.MAX_ITEMS_PER_PAGE

    def get_applet_instance_by_name(self, applet_name: str) -> Applet:
        if self.is_applet_loaded(applet_name):
            applet = self.applets[applet_name]["instance"]
            return applet
        self.error(f"get_applet_instance_by_name failed! Applet {applet_name} is not loaded!")
        return

    def view_applet_information(self) -> None:
        """Open the view applet applet with the selected applet"""
        selected_applet_name = list(self.applets.keys())[self.current_index]
        # get configuration file for applet
        selected_applet_config_json = self.applets[selected_applet_name]
        # going to add the name to the config here as it is not in (because it's the dict key :D )
        selected_applet_config_json["name"] = selected_applet_name
        #configuration = self.applets[selected_applet_name]
        view_applet_information_applet = AppletInformationViewer(
            display=self.display, 
            input_handler=self.input_handler,
            applet_config=selected_applet_config_json
        )

        try:
            view_applet_information_applet.start()
        except KeyboardInterrupt:
            pass
        finally:
            view_applet_information_applet.stop()
            self.display.matrix.Clear()
            self.input_handler.exit_requested = False

    def open_settings(self) -> None:
        """Open the settings applet"""
        settings_applet = SettingsApplet(
            display=self.display,
            input_handler=self.input_handler
        )

        try:
            settings_applet.start()
        except KeyboardInterrupt:
            pass
        finally:
            settings_applet.stop()
            self.display.matrix.Clear()
            self.input_handler.exit_requested = False

    def select_applet(self) -> None:
        """Select and build (instantiate) the selected applet"""
        selected_applet = None
        applet_name = list(self.applets.keys())[self.current_index]

        self.display.matrix.Clear()
        self.display.show_message(f"Loading {applet_name}...", "loading")

        if self.is_applet_loaded(applet_name):
            self.log(
                f"Applet {applet_name} has already been instantiated, loading from memory instead..."
            )
            selected_applet = self.get_applet_instance_by_name(applet_name)
        else:
            # Dynamically import selected applet
            self.log(
                f"Applet {applet_name} has not been instantiated! Dynamically importing now..."
            )
            module_path = self.applets[applet_name]["module_path"]
            class_name = self.applets[applet_name]["class_name"]
            options = self.applets[applet_name]["options"]
            AppletClass = self.dynamic_import_applet(module_path, class_name)

            # If the class_name parsed from config.json exists in the AppletClass module
            if hasattr(AppletClass, class_name):
                # Get a reference to the Applet's main class (class_name) type definition
                selected_applet_type = getattr(AppletClass, class_name)
                # Instantiate the applet's main class
                # with the required parameter 'self.display' (reference to the matrix)
                selected_applet = selected_applet_type(display=self.display, options=options, input_handler=self.input_handler)

                self.applets[applet_name]["instance"] = selected_applet
                self.log(f"Dynamically imported class {class_name} from module {module_path}")
            else:
                self.error(f"The class '{class_name}' is not found in the module '{module_path}'")
                return

        # This try, except, finally block allows us to
        # CTRL+C out of the applet and return to the menu.
        try:
            selected_applet.start()
        except KeyboardInterrupt:
            pass
        finally:
            selected_applet.stop()
            self.display.matrix.Clear()
            self.input_handler.exit_requested = False

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
            # don't try to add the 1 applet!!!
            if os.path.isdir(full_path) and \
                item not in ["__pycache__", "template_applet", "applet_information_viewer", "settings_applet"]:
                folders.append(full_path)

        # For now, sort alphabetically. This controls the order at which
        # the applets are loaded (and displayed) onto the menu.
        folders.sort()

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
                        "options": config_data.get("options", {}),
                        "class_name": config_data.get("class_name", "No Classname Provided"),
                        "module_path": os.path.join(folder, "main.py"),
                    }

            except FileNotFoundError:
                self.error(f"Config file not found in {folder}")
            except json.JSONDecodeError:
                self.error(f"Error decoding JSON in {folder}")

        return applets

    @staticmethod
    def dynamic_import_applet(module_path: str, module_name: str) -> Applet:
        """Dynamically import a module given its file path and module name."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def is_applet_loaded(self, applet_name: str) -> bool:
        """Determine whether an applet has already been dynamically imported"""
        # Check if "instance" key exists, and if it isn't null
        if self.applets[applet_name].get("instance") and self.applets[applet_name]["instance"]:
            return True
        else:
            return False

    def run(self) -> None:
        """Run the master application"""
        # DONE: Add directory based applets with separate config files, and dynamic applet importing
        self.get_applets_information()
        while True:
            self.display_menu()
            self.navigate_menu()
            if self.input_handler.select_pressed:
                self.select_applet()
            if self.input_handler.x_pressed:
                self.view_applet_information()
            if self.input_handler.y_pressed:
                self.open_settings()
            time.sleep(0.1)

def find_xbox_controller() -> str:
    """Find xbox controller, return the path e.g. /dev/input/eventX"""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        # This is probably not great...
        if any(keyword in device.name.lower() for keyword in ["xbox", "x-box"]):
            return device.path
    return None

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root!")
        sys.exit(1)
    # Get the directory where the current script is located
    current_script_path = os.path.realpath(__file__)
    current_script_directory = os.path.dirname(current_script_path)

    # Define the target subdirectory (change this if you have a differently named applets directory)
    applets_subdirectory = "applets"

    # Construct the full path to the target subdirectory
    applets_root_directory = os.path.join(current_script_directory, applets_subdirectory)

    # here is our ONLY matrix display ever instantiated - will be passed through
    display = MatrixDisplay()

    # try to get xbox controller
    xbox_controller_path = find_xbox_controller()
    if xbox_controller_path:
        input_handler = Controller(xbox_controller_path)
    else:
        input_handler = Keyboard()

    display.show_message("Building Menu System...", "loading")
    master_app = MasterApp(display, input_handler, applets_root_directory)
    master_app.run()
