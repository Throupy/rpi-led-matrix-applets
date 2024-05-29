import os
import json
import sys
import importlib.util
from typing import Dict
from matrix.matrix_display import MatrixDisplay
from input_handlers.base_input_handler import BaseInputHandler
from applets.base_applet import Applet
from applets.master_applet.main import MasterApp

class AppletManager:
    def __init__(self, display: MatrixDisplay, input_handler: BaseInputHandler, applets_root_directory: str) -> None:
        """Initialize the AppletManager with the provided display, input handler, and applets root directory.""" 
        self.display = display
        self.input_handler = input_handler
        self.applets_root_directory = applets_root_directory
        self.applets = self.get_applets_information()

    def get_applets_information(self) -> Dict[str, Dict]:
        """Retrieve information about applets from the config file in each applet's directory."""
        applets = {}
        for item in os.listdir(self.applets_root_directory):
            full_path = os.path.join(self.applets_root_directory, item)
            if os.path.isdir(full_path) and item not in ["__pycache__", "template_applet", "applet_information_viewer", "settings_applet", "idle_applet", "master_applet"]:
                config_path = os.path.join(full_path, "config.json")
                try:
                    with open(config_path, "r") as file:
                        config_data = json.load(file)
                        name = config_data.get("name", "No Name Provided")
                        applets[name] = {
                            "description": config_data.get("description", "No Description Provided"),
                            "version": config_data.get("version", "No Version Provided"),
                            "author": config_data.get("author", "No Author Provided"),
                            "path": full_path,
                            "options": config_data.get("options", {}),
                            "class_name": config_data.get("class_name", "No Classname Provided"),
                            "module_path": os.path.join(full_path, "main.py"),
                        }
                except FileNotFoundError:
                    print(f"Config file not found in {full_path}")
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in {full_path}")
        sorted_applets = {key: value for key, value in sorted(applets.items())}
        return sorted_applets

    def dynamic_import_applet(self, module_path: str, module_name: str) -> Applet:
        """Dynamically import a module given its file path and module name."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def create_master_app(self) -> MasterApp:
        """Create and return an instance of the MasterApp."""
        return MasterApp(display=self.display, input_handler=self.input_handler, applet_manager=self)

    def get_applet_instance_by_name(self, applet_name: str) -> Applet:
        """Retrieve an instance of the applet by its name, dynamically importing it if necessary."""
        if applet_name in self.applets:
            module_path = self.applets[applet_name]["module_path"]
            class_name = self.applets[applet_name]["class_name"]
            options = self.applets[applet_name]["options"]
            AppletClass = self.dynamic_import_applet(module_path, class_name)
            if hasattr(AppletClass, class_name):
                applet_type = getattr(AppletClass, class_name)
                return applet_type(display=self.display, options=options, input_handler=self.input_handler)
        print(f"Applet {applet_name} not found!")
        return None

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