import time
import os
import requests
from typing import List, Optional, Dict
from PIL import Image
from matrix.matrix_display import graphics
from matrix.colours import Colours
from applets.base_applet import Applet
from applets.tarkov_price_tracker.display_item import DisplayItem


class TarkovPriceTracker(Applet):
    """TarkovPriceTracker applet definition"""

    def __init__(self, **kwargs) -> None:
        """Initialization function"""
        super().__init__("Tarkov Price Tracker", **kwargs)
        self.item_names = self.options.get("item_names")
        self.items = []
        self.images = {}
        self.last_switch_time = time.time() - 5
        self.last_fetch_time = time.time()
        self.current_page_index = 0
        self.fetch_items()

    def run_query(self, query: str) -> Optional[Dict]:
        """Run a GraphQL query"""
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                "https://api.tarkov.dev/graphql", headers=headers, json={"query": query}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log(f"Network error: {e}")
            self.display.show_message("Network error. Check your connection", "error")
            time.sleep(2)
            self.input_handler.exit_requested = True
            return None

    def load_and_convert_image(self, image_name: str, icon_link: str) -> Image:
        """Load image from URL and convert into displayable format, save as BMP if required"""
        image_path = os.path.join(self.resources_directory, image_name)
        bmp_path = image_path.replace(".png", ".bmp")
        if os.path.exists(bmp_path):
            self.log(f"Using file from disk - {bmp_path}")
            image = Image.open(bmp_path)
        else:
            self.log(
                f"Image for {image_path.split('/')[-1].split('.')[0]} not found on disk - downloading, converting and saving"
            )
            image_data = requests.get(icon_link, stream=True)
            image = Image.open(image_data.raw)
            image = image.convert("RGBA")
            image = image.resize((16, 16))
            image.save(bmp_path)
        return image

    def fetch_items(self) -> None:
        """Fetch all the selected items' information from the API"""
        self.log("Fetching items from the Tarkov API")
        self.items = []
        for item_name in self.item_names:
            query = generate_query(item_name)
            result = self.run_query(query)
            if not result:
                self.error(
                    "Something went wrong when fetching the data - result was None"
                )
                return
            display_item = DisplayItem.from_graphql(result)
            if display_item:
                self.items.append(display_item)
                if display_item.name not in self.images.keys():
                    image_path = f"{item_name.lower().replace(' ', '_')}.png"
                    self.images[display_item.name] = self.load_and_convert_image(
                        image_path, display_item.icon_link
                    )
            else:
                self.log(f"No item found for {item_name}.")

    def display_items(self, items: List[DisplayItem]) -> None:
        """Update matrix display with multiple items' information"""
        self.display.clear()
        for index, item in enumerate(items):
            image = self.images[item.name]
            self.display.offscreen_canvas.SetImage(image.convert("RGB"), 0, index * 16)
            short_price = shorten_price(item.price)
            if item.change_last_48h_percent is not None:
                change_text = f"{abs(item.change_last_48h_percent):.1f}%"
                text = f"{short_price} {change_text}"
                color = (
                    Colours.RED if item.change_last_48h_percent < 0 else Colours.GREEN
                )
            else:
                text = f"{short_price} TR."
                color = Colours.GREEN

            self.display.draw_text(
                18,
                (index * 16) + 12,
                text,
                color
            )

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
            self.display.offscreen_canvas
        )

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.clear()
        if not self.items:
            self.fetch_items()
        while not self.input_handler.exit_requested:
            current_time = time.time()
            latest_inputs = self.input_handler.get_latest_inputs()
            if current_time - self.last_fetch_time >= 10:
                self.fetch_items()
                self.last_fetch_time = current_time

            if current_time - self.last_switch_time >= 5 or latest_inputs.get(
                "select_pressed"
            ):
                start_index = self.current_page_index * 4
                end_index = start_index + 4
                self.display_items(self.items[start_index:end_index])
                self.current_page_index = (self.current_page_index + 1) % (
                    (len(self.items) + 3) // 4
                )
                self.last_switch_time = current_time

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.clear()


def generate_query(item_name: str) -> str:
    """Generate a GraphQL query for a given item"""
    return f"""
    {{
        items(name: "{item_name}") {{
            shortName
            iconLink
            changeLast48hPercent
            avg24hPrice
            sellFor {{
                price
                source
            }}
        }}
    }}
    """


def shorten_price(price: int) -> str:
    """Format prices, turning thousands into 'k'"""
    if price >= 1000000:
        return f"{round(price / 1000000, 1)}M"
    elif price >= 1000:
        return f"{round(price / 1000)}k"
    else:
        return str(price)
