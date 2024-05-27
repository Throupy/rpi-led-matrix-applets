import time
import requests
from typing import List
from applets.base_applet import Applet
from applets.helldivers_planets_info.planet import Planet


class HelldiversPlanetsInfo(Applet):
    """Hell divers 2 planets info applet Definition"""

    def __init__(self, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Template Applet", **kwargs)
        self.last_switch_time = time.time() - 5
        self.last_fetch_time = time.time()
        self.current_planet_index = 0
        self.planets = self.get_occupied_and_started_planets()

    def get_occupied_and_started_planets(self) -> List[Planet]:
        """Get all of the enemy-occupied planets, which have started being liberated"""
        try:
            root_url = "https://api.helldivers2.dev/api/v1/planets"
            response = requests.get(root_url).json()
            planets = [
                planet
                for planet in response
                if planet["currentOwner"] != "Human"
                and planet["maxHealth"] != planet["health"]
            ]
            planets = [Planet.from_json(planet) for planet in planets]
            return planets
        except requests.exceptions.RequestException:
            self.display.show_message("Network error. Check your connection", "error")
            time.sleep(2)
            self.input_handler.exit_requested = True
            return None

    def display_planet(self, planet: Planet) -> None:
        """Update matrix display with planet information"""
        self.log(
            f"Updating display to show information of planet with name {planet.name}"
        )
        self.display.matrix.Clear()
        # Draw the planet's name
        self.display.draw_centered_text(planet.name, planet.colour, start_y=8)

        # Draw a progress bar
        self.display.draw_progress_bar(
            planet.percentage_liberated,
            planet.colour,
            x=4,
            y=12,
        )

        # Display the liberation percentage underneath the progress bar
        self.display.draw_centered_text(
            f"{planet.percentage_liberated}%", planet.colour, start_y=28
        )

        # Display the number of currently active helldivers (democracy spreaders) on the planet
        self.display.draw_centered_text(
            f"{planet.player_count} Active Helldivers", planet.colour, start_y=40
        )

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(self.display.offscreen_canvas)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.offscreen_canvas.Clear()
        # when the app is "loaded from memory" it messes with previous error handling
        # to prevent this, I have added a presence check on self.planets
        if not self.planets:
            self.planets = self.get_occupied_and_started_planets()
        while not self.input_handler.exit_requested:
            current_time = time.time()
            latest_inputs = self.input_handler.get_latest_inputs()
            # Every 10 seconds refresh the data
            if current_time - self.last_fetch_time >= 20:
                self.planets = self.get_occupied_and_started_planets()
                self.last_fetch_time = current_time
            if (
                current_time - self.last_switch_time >= 5
                or latest_inputs["select_pressed"]
            ):
                self.display_planet(self.planets[self.current_planet_index])
                self.current_planet_index = (self.current_planet_index + 1) % len(
                    self.planets
                )
                self.last_switch_time = current_time

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
        self.display.offscreen_canvas.Clear()

