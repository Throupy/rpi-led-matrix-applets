import os
import sys
import evdev
from matrix.matrix_display import MatrixDisplay
from input_handlers.xbox_controller import Controller
from input_handlers.keyboard import Keyboard
from applet_manager import AppletManager

def find_xbox_controller() -> str:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if any(keyword in device.name.lower() for keyword in ["xbox", "x-box"]):
            return device.path
    return None

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root!")
        sys.exit(1)
    
    current_script_path = os.path.realpath(__file__)
    current_script_directory = os.path.dirname(current_script_path)
    applets_root_directory = os.path.join(current_script_directory, "applets")

    display = MatrixDisplay()
    xbox_controller_path = find_xbox_controller()
    input_handler = Controller(xbox_controller_path) if xbox_controller_path else Keyboard()

    display.show_message("Building Menu System...", "loading")
    applet_manager = AppletManager(display, input_handler, applets_root_directory)
    master_app = applet_manager.create_master_app()
    applet_manager.launch_applet(master_app)
