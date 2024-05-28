import random
import time
import threading
from rgbmatrix import graphics
from matrix.colours import Colours
from applets.base_applet import Applet


class PongGame(Applet):
    """PongGame applet definition"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialization function"""
        super().__init__("Pong Game", *args, **kwargs)
        self.width = self.display.matrix.width
        self.height = self.display.matrix.height
        self.paddle_height = 10
        self.paddle_thickness = 2
        self.ball_size = 2
        self.ball_speed = 1.2  # Increase this value to make the ball move faster
        self.reset_game()
        self.player1_pos = self.height // 2 - self.paddle_height // 2
        self.player2_pos = self.height // 2 - self.paddle_height // 2
        self.player_speed = 2.4
        self.ai_speed = 1.2
        self.lock = threading.Lock()

    def reset_game(self) -> None:
        """Reset the game state"""
        self.ball_pos = [self.width // 2, self.height // 2]
        self.ball_dir = [
            random.choice([-self.ball_speed, self.ball_speed]),
            random.choice([-self.ball_speed, self.ball_speed]),
        ]
        self.player1_pos = self.height // 2 - self.paddle_height // 2
        self.player2_pos = self.height // 2 - self.paddle_height // 2

    def move_ball(self) -> None:
        """Move the ball and handle collisions"""
        with self.lock:
            # Move the ball
            self.ball_pos[0] += self.ball_dir[0]
            self.ball_pos[1] += self.ball_dir[1]

            # Ball collision with top and bottom walls
            if (
                self.ball_pos[1] <= 1
                or self.ball_pos[1] >= self.height - self.ball_size - 1
            ):
                self.ball_dir[1] = -self.ball_dir[1]

            # Ball collision with paddles
            if self.ball_pos[0] <= self.paddle_thickness:
                if (
                    self.player1_pos
                    <= self.ball_pos[1]
                    <= self.player1_pos + self.paddle_height
                ):
                    self.ball_dir[0] = -self.ball_dir[0]
                else:
                    self.score[1] += 1
                    self.reset_game()

            if self.ball_pos[0] >= self.width - self.ball_size - self.paddle_thickness:
                if (
                    self.player2_pos
                    <= self.ball_pos[1]
                    <= self.player2_pos + self.paddle_height
                ):
                    self.ball_dir[0] = -self.ball_dir[0]
                else:
                    self.score[0] += 1
                    self.reset_game()

    def move_paddles(self) -> None:
        """Move the paddles based on AI and player input"""
        with self.lock:
            # Move paddle1 (player) based on D-pad input
            if self.input_handler.up_pressed:
                self.player1_pos = max(1, self.player1_pos - self.player_speed)
            if self.input_handler.down_pressed:
                self.player1_pos = min(
                    self.height - self.paddle_height - 1,
                    self.player1_pos + self.player_speed,
                )

            # Move paddle2 (AI) to follow the ball
            if self.ball_pos[1] < self.player2_pos + self.paddle_height // 2:
                self.player2_pos = max(1, self.player2_pos - self.ai_speed)
            elif self.ball_pos[1] > self.player2_pos + self.paddle_height // 2:
                self.player2_pos = min(
                    self.height - self.paddle_height - 1,
                    self.player2_pos + self.ai_speed,
                )

    def display_game(self) -> None:
        """Display the game on the matrix"""
        self.display.clear()

        # Draw the border
        for x in range(self.width):
            self.display.offscreen_canvas.SetPixel(
                x,
                0,
                Colours.WHITE_NORMAL.red,
                Colours.WHITE_NORMAL.green,
                Colours.WHITE_NORMAL.blue,
            )
            self.display.offscreen_canvas.SetPixel(
                x,
                self.height - 1,
                Colours.WHITE_NORMAL.red,
                Colours.WHITE_NORMAL.green,
                Colours.WHITE_NORMAL.blue,
            )
        for y in range(self.height):
            self.display.offscreen_canvas.SetPixel(
                0,
                y,
                Colours.WHITE_NORMAL.red,
                Colours.WHITE_NORMAL.green,
                Colours.WHITE_NORMAL.blue,
            )
            self.display.offscreen_canvas.SetPixel(
                self.width - 1,
                y,
                Colours.WHITE_NORMAL.red,
                Colours.WHITE_NORMAL.green,
                Colours.WHITE_NORMAL.blue,
            )

        # Draw the ball
        for dx in range(self.ball_size):
            for dy in range(self.ball_size):
                self.display.offscreen_canvas.SetPixel(
                    self.ball_pos[0] + dx,
                    self.ball_pos[1] + dy,
                    Colours.BLUE.red,
                    Colours.BLUE.green,
                    Colours.BLUE.blue,
                )

        # Draw the paddles
        for dy in range(self.paddle_height):
            for px in range(self.paddle_thickness):
                self.display.offscreen_canvas.SetPixel(
                    1 + px,
                    self.player1_pos + dy,
                    Colours.GREEN.red,
                    Colours.GREEN.green,
                    Colours.GREEN.blue,
                )
                self.display.offscreen_canvas.SetPixel(
                    self.width - 2 - px,
                    self.player2_pos + dy,
                    Colours.GREEN.red,
                    Colours.GREEN.green,
                    Colours.GREEN.blue,
                )

        # Draw the scores
        score_text = f"{self.score[0]} - {self.score[1]}"
        text_length = self.display.get_text_width(score_text)
        text_x = (self.width - text_length) // 2  # Center the text horizontally
        self.display.draw_text(
            text_x,
            8,
            score_text,
            Colours.WHITE_NORMAL
        )

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)
        time.sleep(0.025)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting Pong Game")
        self.display.clear()
        if not self.input_handler.is_controller():
            self.display.show_message("Controller required!", "error")
            time.sleep(2)
            # simulate back button press to return to menu
            self.input_handler.exit_requested = True

        self.score = [0, 0]  # Initialize score
        try:
            while not self.input_handler.exit_requested:
                self.move_ball()
                self.move_paddles()
                self.display_game()
        except KeyboardInterrupt:
            pass

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping Pong Game")
        self.display.clear()
