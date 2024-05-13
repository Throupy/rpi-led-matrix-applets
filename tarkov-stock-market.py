import requests
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, UnidentifiedImageError

class DisplayItem:
    def __init__(self, name, price, icon_link, change_last_48h_percent):
        """
        Initialize the DisplayItem with the provided parameters.

        :param name: Name of the item.
        :param price: Price of the item.
        :param icon_link: URL to the item's icon.
        :param change_last_48h_percent: Percentage change in price over the last 48 hours.
        """
        self.name = name
        self.price = price
        self.icon_link = icon_link
        self.change_last_48h_percent = change_last_48h_percent

    @staticmethod
    def get_highest_trader_price(data: dict) -> int:
        """
        Get the highest price of the item from trader offers.

        :param data: Dictionary containing item data.
        :return: Highest price of the item.
        """
        items = data.get("data", {}).get("items", [])
        max_price = max(
            (offer.get("price", 0) for item in items for offer in item.get("sellFor", [])),
            default=-1
        )
        return max_price

    @classmethod
    def from_graphql(cls, data: dict):
        """
        Create a DisplayItem instance from GraphQL data.

        :param data: Dictionary containing item data from GraphQL query.
        :return: Instance of DisplayItem or None if no items found.
        """
        items = data.get("data", {}).get("items", [])
        if items:
            item = items[0]
            short_name = item.get("shortName")
            price = cls.get_highest_trader_price(data)
            icon_link = item.get("iconLink", "")
            change_last_48h_percent = item.get("changeLast48hPercent", 0)
            return cls(name=short_name, price=price, icon_link=icon_link, 
                       change_last_48h_percent=change_last_48h_percent)
        return None

def run_query(query: str):
    """
    Run a GraphQL query and return the result.

    :param query: GraphQL query string.
    :return: Result of the query in JSON format.
    """
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Query failed: {e}")
        return None

def generate_query(item_name: str) -> str:
    """
    Generate a GraphQL query for the given item name.

    :param item_name: Name of the item.
    :return: GraphQL query string.
    """
    return f"""
    {{
        items(name: "{item_name}") {{
            shortName
            iconLink
            changeLast48hPercent
            sellFor {{
                price
                source
            }}
        }}
    }}
    """

def display_item_on_matrix(display_item: DisplayItem, matrix: RGBMatrix):
    """
    Display item information on the RGB matrix.

    :param display_item: Instance of DisplayItem containing item data.
    :param matrix: Instance of RGBMatrix to display the data on.
    """
    try:
        # Load and resize image
        image = Image.open(requests.get(display_item.icon_link, stream=True).raw)
        image = image.resize((16, 16))
    except (requests.RequestException, UnidentifiedImageError) as e:
        print(f"Failed to load image: {e}")
        return

    # Prepare the price change text with a "+" if positive
    change_text = f"{display_item.change_last_48h_percent:+.2f}%"
    # Prepare text to scroll
    text = f" {display_item.name} ₽{display_item.price} {change_text}"

    # Set text color based on change_last_48h_percent
    color = graphics.Color(240, 15, 0) if display_item.change_last_48h_percent < 0 else graphics.Color(0, 255, 0)

    # Create a font
    font = graphics.Font()
    font.LoadFont("bdf/verdana-8pt.bdf")

    # Calculate the total width for scrolling (image width + text width)
    text_length = graphics.DrawText(matrix.CreateFrameCanvas(), font, 0, 0, color, text)
    total_length = 16 + text_length  # 16 for the image width

    # Scroll the entire image and text together
    offscreen_canvas = matrix.CreateFrameCanvas()
    pos = offscreen_canvas.width

    while pos + total_length > 0:
        offscreen_canvas.Clear()
        # Draw the image
        offscreen_canvas.SetImage(image.convert('RGB'), pos, 0)
        # Draw the text
        graphics.DrawText(offscreen_canvas, font, pos + 16, 12, color, text)

        pos -= 1
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(0.02)  # Adjust the speed of scrolling

if __name__ == "__main__":
    item_names = ["ledx", "rooster", "gp coin"]
    items = []

    for item_name in item_names:
        query = generate_query(item_name)
        result = run_query(query)
        if result:
            display_item = DisplayItem.from_graphql(result)
            if display_item:
                print(f"Found item: {display_item.name}")
                # This is because of a current event in the game meaning that
                # all items are cheaper... I just want to test the green text!
                if display_item.name == "LEDX":
                    display_item.change_last_48h_percent = 5.6
                items.append(display_item)
            else:
                print(f"No item found for {item_name}.")
        else:
            print(f"Failed to get data for {item_name}")

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'  # Using Adafruit HAT

    matrix = RGBMatrix(options=options)

    try:
        while True:
            for item in items:
                display_item_on_matrix(item, matrix)
    except KeyboardInterrupt:
        print("Program interrupted and terminated gracefully.")
