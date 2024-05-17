import requests
import time
from typing import List, Dict, Optional
from rgbmatrix import graphics
from PIL import Image
from applets.base_applet import Applet
from matrix.matrix_display import MatrixDisplay

class DisplayItem:
    """Represent a 64x16 row on the matrix"""
    def __init__(self, name: str, price: int, icon_link: str, change_last_48h_percent: float) -> None:
        """Initialise a DisplayItem"""
        self.name = name
        self.price = price
        self.icon_link = icon_link
        self.change_last_48h_percent = change_last_48h_percent

    @staticmethod
    def get_highest_trader_price(data: Dict) -> int:
        """Get the highest price offered by a trader for a given item"""
        item_name = data.get("data", {}).get("items", [])[0].get("shortName")
        self.log(f"No flea market data for {item_name}, going with highest trader price")
        items = data.get("data", {}).get("items", [])
        max_price = max(
            (offer.get("price", 0) for item in items for offer in item.get("sellFor", [])),
            default=-1
        )
        return max_price

    @classmethod
    def from_graphql(cls, data: Dict) -> Optional['DisplayItem']:
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
            return cls(name=short_name, price=price, icon_link=icon_link,
                       change_last_48h_percent=change_last_48h_percent)
        return None


def run_query(query: str) -> Dict:
    """Run a GraphQL query"""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
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
    return f"{round(price / 1000)}k" if price >= 1000 else str(price)


class TarkovPriceTracker(Applet):
    """TarkovPriceTracker applet definition"""
    def __init__(self, display: MatrixDisplay) -> None:
        """Initialisation function"""
        super().__init__("Tarkov Price Tracker", display)
        self.item_names = [
            "LEDX", "Graphics Card", "GP Coin", "Defibrillator", "Ophthalmoscope",
            "Abandoned factory marked key", "Grenade case", "Crash Axe", "Intelligence"
        ]
        self.items = []

    def fetch_items(self) -> None:
        """Fetch all the selected items' information from the API"""
        self.log("Fetching items from the Tarkov API")
        for item_name in self.item_names:
            query = generate_query(item_name)
            try:
                result = run_query(query)
                display_item = DisplayItem.from_graphql(result)
                if display_item:
                    self.items.append(display_item)
                else:
                    self.log(f"No item found for {item_name}.")
            except Exception as e:
                self.log(f"Error retrieving data for {item_name}: {e}")

    def display_items(self, item: List[DisplayItem]) -> None:
        """Display the selected items onto the matrix"""
        font = self.display.font

        images = []
        for item in self.items:
            image = Image.open(requests.get(item.icon_link, stream=True).raw)
            image = image.resize((16, 16))
            images.append(image)

        offscreen_canvas = self.display.matrix.CreateFrameCanvas()

        for index, item in enumerate(self.items):
            offscreen_canvas.SetImage(images[index].convert('RGB'), 0, index * 16)
            short_price = shorten_price(item.price)
            if item.change_last_48h_percent:
                change_text = f"{item.change_last_48h_percent:+.1f}%"
                text = f"{short_price} {change_text}"
                color = graphics.Color(240, 15, 0) if item.change_last_48h_percent < 0 else graphics.Color(0, 255, 0)
            else:
                text = f"{short_price} TRADER"
                color = graphics.Color(0, 255, 0)

            graphics.DrawText(offscreen_canvas, font, 18, (index * 16) + 12, color, text)

        offscreen_canvas = self.display.matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(3)

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        while True:
            self.fetch_items()
            for i in range(0, len(self.items), 4):
                self.display_items(self.items[i:i+4])
                time.sleep(10)  # Refresh every 10 seconds

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.matrix.Clear()
