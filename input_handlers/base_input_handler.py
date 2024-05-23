from typing import Dict

class BaseInputHandler:
    def __init__(self) -> None:
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.select_pressed = False
        self.x_pressed = False
        self.back_pressed = False
        self.exit_requested = False

        # Track previous states
        self.previous_states = {
            'up_pressed': self.up_pressed,
            'down_pressed': self.down_pressed,
            'left_pressed': self.left_pressed,
            'right_pressed': self.right_pressed,
            'select_pressed': self.select_pressed,
            'x_pressed': self.x_pressed,
            'back_pressed': self.back_pressed,
            'exit_requested': self.exit_requested,
        }

        # Track state changes
        self.state_changes = {
            'up_pressed': False,
            'down_pressed': False,
            'left_pressed': False,
            'right_pressed': False,
            'select_pressed': False,
            'x_pressed': False,
            'back_pressed': False,
            'exit_requested': False,
        }

    def listen(self) -> None:
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_latest_inputs(self) -> Dict[str, bool]:
        # Current states
        current_states = {
            'up_pressed': self.up_pressed,
            'down_pressed': self.down_pressed,
            'left_pressed': self.left_pressed,
            'right_pressed': self.right_pressed,
            'select_pressed': self.select_pressed,
            'back_pressed': self.back_pressed,
            'x_pressed': self.x_pressed,
            'exit_requested': self.exit_requested,
        }

        # Determine if states have changed and update state changes
        for key in current_states:
            if current_states[key] == True and current_states[key] != self.previous_states[key]:
                self.state_changes[key] = True
            else:
                self.state_changes[key] = False

        # Update previous states to current states
        self.previous_states = current_states.copy()

        return self.state_changes

    # this is overridden in the controller.
    # the same could be acheived with isinstance but this is more graceful IMHO
    @staticmethod
    def is_controller() -> bool:
        return False