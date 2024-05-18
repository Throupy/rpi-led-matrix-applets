import requests
import os
import time
from typing import List, Dict, Optional
from rgbmatrix import graphics
from PIL import Image
from applets.base_applet import Applet


class DisplayItem:
    """Represent a 64x16 row on the matrix"""

    def __init__(
        self, name: str, price: int, icon_link: str, change_last_48h_percent: float
    ) -> None:
        """Initialise a DisplayItem"""
        self.name = name
        self.price = price
        self.icon_link = icon_link
        self.change_last_48h_percent = change_last_48h_percent

    @staticmethod
    def get_highest_trader_price(data: Dict) -> int:
        """Get the highest price offered by a trader for a given item"""
        item_name = data.get("data", {}).get("items", [])[0].get("shortName")
        items = data.get("data", {}).get("items", [])
        max_price = max(
            (offer.get("price", 0) for item in items for offer in item.get("sellFor", [])),
            default=-1,
        )
        return max_price

    @classmethod
    def from_graphql(cls, data: Dict) -> Optional["DisplayItem"]:
        """Create a DisplayItem from a GraphQL query response"""
        items = data.get("data", {}).get("items", [])
        if items:
            item = items[0]
            short_name = item.get("shortName")
            price = item.get("avg24hPrice")
            if not price:
                price = cls.get_highest_trader_price(data)
            icon_link = item.get("iconLink", "")
            change_last_48h_percent = item.get("changeLast48hPercent", 0)
            return cls(
                name=short_name,
                price=price,
                icon_link=icon_link,
                change_last_48h_percent=change_last_48h_percent,
            )
        return None


def run_query(query: str) -> Dict:
    """Run a GraphQL query"""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            "https://api.tarkov.dev/graphql", headers=headers, json={"query": query}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Query failed to run: {e}")


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


class TarkovPriceTracker(Applet):
    """TarkovPriceTracker applet definition"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("Tarkov Price Tracker", *args, **kwargs)
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # assume a dir called 'resources' exists in the same dir as implementation
        self.resources_directory = os.path.join(current_directory, "resources")
        # self.options is made available via *args and **kwargs
        self.item_names = self.options.get("item_names")
        self.items = []
        self.images = {}

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
            data = image.getdata()

            new_data = []
            for item in data:
                new_data.append(item)

            image.putdata(new_data)
            image = image.resize((16, 16))
            image.save(bmp_path)
        return image

    def fetch_items(self) -> None:
        """Fetch all the selected items' information from the API"""
        self.log("Fetching items from the Tarkov API")
        self.items = []
        for item_name in self.item_names:
            query = generate_query(item_name)
            try:
                result = run_query(query)
                display_item = DisplayItem.from_graphql(result)
                if display_item:
                    self.items.append(display_item)
                    # only do this if image not already loaded - only on first time
                    if display_item.name not in self.images.keys():
                        # e.g. ledx.png
                        image_path = f"{item_name.lower().replace(' ', '_')}.png"
                        self.images[display_item.name] = self.load_and_convert_image(
                            image_path, display_item.icon_link
                        )
                else:
                    self.log(f"No item found for {item_name}.")
            except Exception as e:
                self.log(f"Error retrieving data for {item_name}: {e}")

    def display_items(self, items: List[DisplayItem]) -> None:
        """Display the selected items onto the matrix"""
        font = self.display.font
        self.display.matrix.Clear()
        for index, item in enumerate(items):
            image = self.images[item.name]
            self.display.offscreen_canvas.SetImage(image.convert("RGB"), 0, index * 16)
            short_price = shorten_price(item.price)
            if item.change_last_48h_percent:
                change_text = f"{item.change_last_48h_percent:+.1f}%"
                text = f"{short_price} {change_text}"
                color = (
                    graphics.Color(240, 15, 0)
                    if item.change_last_48h_percent < 0
                    else graphics.Color(0, 255, 0)
                )
            else:
                text = f"{short_price} TRADER"
                color = graphics.Color(0, 255, 0)

            graphics.DrawText(
                self.display.offscreen_canvas, font, 18, (index * 16) + 12, color, text
            )

        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
            self.display.offscreen_canvas
        )
        time.sleep(2)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        while not self.input_handler.exit_requested:
            self.fetch_items()
            for i in range(0, len(self.items), 4):
                self.display_items(self.items[i : i + 4])
                time.sleep(4)  # Refresh every 4 (+ 2) = 6 seconds

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
