import threading
import time
from input_handlers.base_input_handler import BaseInputHandler


class Keyboard(BaseInputHandler):
    def __init__(self) -> None:
        super().__init__()
        self.listener_thread = threading.Thread(target=self._input_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def _input_listener(self) -> None:
        while True:
            self.reset_inputs()
            key = (
                input("up/down/left/right/select (CTRL+C to go back) : ")
                .strip()
                .lower()
            )
            if key == "up":
                self.up_pressed = True
            elif key == "down":
                self.down_pressed = True
            elif key == "left":
                self.left_pressed = True
            elif key == "right":
                self.right_pressed = True
            elif key == "select":
                self.select_pressed = True
            elif key == "x":
                self.x_pressed = True
            elif key == "y":
                self.y_pressed = True
            elif key == "q":
                self.exit_requested = True
                break
            time.sleep(0.1)

    def reset_inputs(self):
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.select_pressed = False
        self.back_pressed = False
