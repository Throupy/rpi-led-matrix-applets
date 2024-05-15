import requests
import json
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

def load_and_convert_image(image_path):
    image = Image.open(image_path)
    image = image.convert('RGBA')
    data = image.getdata()

    new_data = []
    for item in data:
        if item[0] in list(range(200, 256)) and item[1] in list(range(200, 256)) and item[2] in list(range(200, 256)):
            if "bugs" in image_path:
                new_data.append((255, 165, 0, item[3]))  # orange
            elif "bots" in image_path:
                new_data.append((255, 30, 0, item[3])) # red
        else:
            new_data.append(item)

    image.putdata(new_data)
    image = image.resize((32, 32), Image.ANTIALIAS)
    return image

# Load and manipulate images
image_bugs = load_and_convert_image('images/bugs.png')
image_bots = load_and_convert_image('images/bots.png')

# Center the images on the matrix but slightly up
x_offset = (matrix.width - 32) // 2
y_offset = (matrix.height - 32) // 4

font = graphics.Font()
font.LoadFont("bdf/tom-thumb.bdf")
color = graphics.Color(255, 255, 255)

def fetch_data():
    # no auth required on API - poggers
    root = "https://api.helldivers2.dev"
    try:
        response = requests.get(f"{root}/raw/api/Stats/war/801/summary")
        response.raise_for_status() 
        data = response.json()
        bugs = str(data['galaxy_stats']['bugKills'])
        bots = str(data['galaxy_stats']['automatonKills'])
        return bugs, bots
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print("Looks like we hit the rate limit (of a whopping 5 req / 10 seconds!!!)...")
        rate_limit = response.headers.get('X-Ratelimit-Limit')
        rate_remaining = response.headers.get('X-RateLimit-Remaining')
        retry_after = response.headers.get('Retry-After')
        print(f"X-Ratelimit-Limit: {rate_limit}")
        print(f"X-RateLimit-Remaining: {rate_remaining}")
        if retry_after:
            print(f"Retry-After: {retry_after} seconds")
        return None, None  # Return None values in case of error

def update_display(image, text):
    matrix.Clear()
    matrix.SetImage(image.convert('RGB'), x_offset, y_offset)
    
    # Calculate the width of the text to center it
    text_width = graphics.DrawText(matrix, font, 0, 0, color, text)  # Measure text width
    text_x = (matrix.width - text_width) // 2  # Center the text horizontally
    text_y = y_offset + 32 + 10  # Position text below the image with some margin

    graphics.DrawText(matrix, font, text_x, text_y, color, text)
    time.sleep(0.1)

current_image = image_bugs
last_switch_time = time.time()
bugs, bots = fetch_data()

try:
    while True:
        current_time = time.time()
        
        # Make the API request every 10 seconds
        if current_time - last_switch_time >= 10:
            bugs, bots = fetch_data()
        current_text = bugs if current_image == image_bugs else bots
        update_display(current_image, current_text)
        
        # every 5 secs, swap bots and bugs
        if current_time - last_switch_time >= 5:
            current_image = image_bots if current_image == image_bugs else image_bugs
            last_switch_time = current_time
except KeyboardInterrupt:
    pass
finally:
    matrix.Clear()