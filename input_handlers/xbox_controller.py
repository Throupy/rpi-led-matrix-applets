# controller.py

import threading
from evdev import InputDevice, categorize, ecodes, KeyEvent, AbsEvent
from input_handlers.base_input_handler import BaseInputHandler

class Controller(BaseInputHandler):
    DEAD_ZONE = 8000  # Define a dead zone threshold

    def __init__(self, device_path: str) -> None:
        super().__init__()
        self.device = InputDevice(device_path)
        self.listener_thread = threading.Thread(target=self._input_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        self.left_joystick_x = 0
        self.left_joystick_y = 0

    def _input_listener(self) -> None:
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if isinstance(key_event, KeyEvent):
                    self._handle_key_event(key_event)
            elif event.type == ecodes.EV_ABS:
                abs_event = categorize(event)
                if isinstance(abs_event, AbsEvent):
                    self._handle_abs_event(abs_event)

    def _handle_key_event(self, key_event: KeyEvent) -> None:
        if 'BTN_SOUTH' in key_event.keycode:  # A button
            self.select_pressed = key_event.keystate == KeyEvent.key_down
        elif 'BTN_EAST' in key_event.keycode:  # B button
            self.back_pressed = key_event.keystate == KeyEvent.key_down
            if key_event.keystate == KeyEvent.key_down:
                self.exit_requested = True
        # B button is east, OK. A button is south, OK, makes sense.
        # surely X button is west, right? Nope, it's north :clown: 
        elif 'BTN_NORTH' in key_event.keycode: # X button
            self.x_pressed = key_event.keystate == KeyEvent.key_down

    def _handle_abs_event(self, abs_event: AbsEvent) -> None:
        if abs_event.event.code == ecodes.ABS_X:  # Left joystick horizontal movement
            self.left_joystick_x = abs_event.event.value
        elif abs_event.event.code == ecodes.ABS_Y:  # Left joystick vertical movement
            self.left_joystick_y = abs_event.event.value

        # Apply dead zone
        if abs(self.left_joystick_x) < self.DEAD_ZONE:
            self.left_joystick_x = 0
        if abs(self.left_joystick_y) < self.DEAD_ZONE:
            self.left_joystick_y = 0

        # Update navigation flags based on joystick position
        self.up_pressed = self.left_joystick_y < -self.DEAD_ZONE
        self.down_pressed = self.left_joystick_y > self.DEAD_ZONE
        self.left_pressed = self.left_joystick_x < -self.DEAD_ZONE
        self.right_pressed = self.left_joystick_x > self.DEAD_ZONE

    @staticmethod
    def is_controller() -> bool:
        return True