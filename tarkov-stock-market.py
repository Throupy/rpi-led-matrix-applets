import requests
import time
from typing import List, Dict, Optional
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image


class DisplayItem:
    """Class to represent an item to display on the LED matrix."""

    def __init__(self, name: str, price: int, icon_link: str, change_last_48h_percent: float):
        self.name = name
        self.price = price
        self.icon_link = icon_link
        self.change_last_48h_percent = change_last_48h_percent

    @staticmethod
    def get_highest_trader_price(data: Dict) -> int:
        """Extract the highest trader price from the GraphQL data."""
        item_name = data.get("data", {}).get("items", [])[0].get("shortName")
        print(f"No flea market data for {item_name}, going with highest trader price")
        items = data.get("data", {}).get("items", [])
        max_price = max(
            (offer.get("price", 0) for item in items for offer in item.get("sellFor", [])),
            default=-1
        )
        return max_price

    @classmethod
    def from_graphql(cls, data: Dict) -> Optional['DisplayItem']:
        """Create a DisplayItem instance from GraphQL data."""
        items = data.get("data", {}).get("items", [])
        if items:
            item = items[0]
            short_name = item.get("shortName")
            price = item.get("avg24hPrice")
            if not price:
                price = cls.get_highest_trader_price(data)
            icon_link = item.get("iconLink", "")
            change_last_48h_percent = item.get("changeLast48hPercent", 0)
            return cls(name=short_name, price=price, icon_link=icon_link,
                       change_last_48h_percent=change_last_48h_percent)
        return None


def run_query(query: str) -> Dict:
    """Run the GraphQL query and return the JSON response."""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Query failed to run: {e}")


def generate_query(item_name: str) -> str:
    """Generate the GraphQL query for a specific item name."""
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
    """Shorten the price to use 'k' for thousands, rounding to the nearest thousand."""
    return f"{round(price / 1000)}k" if price >= 1000 else str(price)


def display_items_on_matrix(items: List[DisplayItem], matrix: RGBMatrix) -> None:
    """Display a set of items on the LED matrix."""
    font = graphics.Font()
    font.LoadFont("bdf/tom-thumb.bdf")

    # Load images
    images = []
    for item in items:
        image = Image.open(requests.get(item.icon_link, stream=True).raw)
        image = image.resize((16, 16))
        images.append(image)

    offscreen_canvas = matrix.CreateFrameCanvas()

    for index, item in enumerate(items):
        # Draw the image
        offscreen_canvas.SetImage(images[index].convert('RGB'), 0, index * 16)
        short_price = shorten_price(item.price)
        # Prepare the price change text with a "+" if positive
        if item.change_last_48h_percent:
            change_text = f"{item.change_last_48h_percent:+.1f}%"
            text = f"{short_price} {change_text}"
            color = graphics.Color(240, 15, 0) if item.change_last_48h_percent < 0 else graphics.Color(0, 255, 0)
        else:
            text = f"{short_price} TRADER"
            color = graphics.Color(0, 255, 0)

        # Draw the text next to the image (starting from x=18 to leave a small gap)
        graphics.DrawText(offscreen_canvas, font, 18, (index * 16) + 12, color, text)

    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    time.sleep(3)  # Display the current set of items for 3 seconds


def main() -> None:
    item_names = [
        "LEDX", "Graphics Card", "GP Coin", "Defibrillator", "Ophthalmoscope", 
        "Abandoned factory marked key", "Grenade case", "Crash Axe", "Intelligence"
    ]
    items = []

    for item_name in item_names:
        query = generate_query(item_name)
        try:
            result = run_query(query)
            display_item = DisplayItem.from_graphql(result)
            if display_item:
                items.append(display_item)
            else:
                print(f"No item found for {item_name}.")
        except Exception as e:
            print(f"Error retrieving data for {item_name}: {e}")

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'  # Using Adafruit HAT

    matrix = RGBMatrix(options=options)

    while True:
        for i in range(0, len(items), 4):
            display_items_on_matrix(items[i:i+4], matrix)


if __name__ == "__main__":
    main()