class BaseInputHandler:
    def __init__(self) -> None:
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.select_pressed = False
        self.back_pressed = False
        self.exit_requested = False

    def listen(self) -> None:
        raise NotImplementedError("This method should be overridden by subclasses")

    # this is overridden in the controller.
    # the same could be acheived with isinstance but this is more graceful IMHO
    @staticmethod
    def is_controller() -> bool:
        return False