# Raspberry Pi LED Matrix Applets
Some small applets that are designed to run on a 64x64 LED matrix with a Raspberry Pi.

# Usage
TODO

## Creating an Applet
Using the example applet in the `applets/` directory is likely the easiest way to create a new one.

### Directory Structure
Applets should be self-contained within their own directory under the `applets/` directory, for example:
```
applets
├── helldivers_counter
│   ├── config.json
│   ├── main.py
│   └── resources
│       ├── bots.bmp
│       ├── bots.png
│       ├── bugs.bmp
│       └── bugs.png
```
- `main.py` should contain your Applet implementation
- `config.json` is required, it contains Applet metadata and configuration parameters - see section "Configuration Files > Required Options"
- `resources` contains various resources (e.g. images) which are used in your applet.

### Applet Definition
Your applet class must inherit from the `Applet` class within `applets.base_applet`, for example:
```python
class MyAwesomeApplet(Applet):
    def __init__(self, *args, **kwargs):
        super().init("Applet Name", *args, **kwargs)
```

#### Resources Directory
The BaseApplet (parent) creates a reference to a resources directory within the applet's directory. It is accessible through `self.resource_directory`, which will return the full filesystem path.
```python
class MyAwesomeApplet(Applet):
    def __init__(self, *args, **kwargs):
        super().init("Applet Name", *args, **kwargs)

    def display_image(self):
        image_path = os.path.join(self.resources_directory, "image.png")
        ...
```
#### Configuration Files - Required Options
As mentioned, the `config.json` file is required for the applet to be loaded into the menu system. Below is an example definition and explanation of each option. **All of the following values are required:**
```json
{
    "name": "Template Applet", // Friendly display name
    "description": "Stuff", // Description
    "version": "1.0", // Version Number
    "author": "Joe Bloggs", // Author
    // Class name - must match the class name in main.py
    "class_name": "TemplateApplet", 
}
```



#### Configuration Files - Optional Parameters
Notice the parameter `options` in the `__init__` function of the Applet. This is a dictionary containing key-value pairs of configuration parameters for the applet. They are set in `config.json`, also within the base directory of the applet.

These options can be loaded within the `__init__` function, and then accessed accordingly.
```python
class MyAwesomeApplet(Applet):
    def __init__(self, *args, **kwargs):
        super().init("Applet Name", *args, **kwargs)
+       self.option_value = self.options.get("example_option")
```
Note: this will require the following `config.json` definition:
```json
{
    "name": "Template Applet",
    "description": "Some amazing stuff!",
    "version": "1.0",
    "author": "Joe Bloggs",
    "class_name": "TemplateApplet",
    "options": {
        "example_option": "example_value"
    }
}
```

#### Main loop and Starting applets
All applets should implement the `start` method. Inside this method you should add a while loop which will run the app until an interrupt is received from an input handler (e.g. CTRL+C, B button on Xbox controller). An example is shown below:
```python
def start():
    """Start the applet"""
    self.log("Starting applet")
    while self.input_handler.exit_requested:
        self.display.matrix.Clear() # clear the display
        # here, you can do things with the display - set images, text, etc.
        self.display.matrix.SwapOnVSync(self.display.offscreen_canvas) # required
        time.sleep(1) # you may wish to change the delay

```
This `start` method can call other methods from within your applets to, for example, fetch data from an API. An example of this could be:
```python
@staticmethod
def fetch_data():
    """Fetch data from a cool API and return it for the mainloop"""
    data = requests.get("http://api.com/get_data")
    ...
    return data

def start():
    """Start the applet"""
    self.log("Starting applet")
    while self.input_handler.exit_requested:
        self.display.matrix.Clear() # clear the display
        # fetch data from API
        text = self.fetch_data()
        # write the data to the matrix
        graphics.DrawText(
            self.display.offscreen_canvas,
            self.display.font,
            18, # x
            32, # y
            graphics.Color(200, 200, 200), # white
            text,
        )
        self.display.matrix.SwapOnVSync(self.display.offscreen_canvas) # required
        time.sleep(1) # you may wish to change the delay
```

### Some Notes about Xbox Controllers
Drivers and permissions are usually the culprits for xbox controller related issues. Make sure you do the following things if you have issues:
1. ```
    sudo nano /etc/group
    input:x:104:user1,user2,root
    ```
    make sure `root` user is in the input group.
2. `sudo python3 -m pip install evdev` - should be in requirements.txt anyway
3. Make sure you are running the script as root (using `sudo python3 app.py`)

### Wrapping Up
The best way to see this in action is to just look at the `template_applet` directory and files.

### TODO:
## Menu
- [ ] Add theming system with customisable colours etc
- [ ] Potentially implement threading for input handling + rendering (on one thread for simplicity), then everything else runs on a separate thread (such as API calls that could take up to a second etc), which will improve responsiveness
- [X] Add background/idle applet that loads after 5 mins idling on menu (configurable), could show clock / system uptime overlayed onto a GIF
- [X] Some form of brightness control (for the idle app), not sure if brightness can be changed after instantiating the matrix though...
- [X] Add support to view applet information (press X on controller) such as version, description, author etc
- [ ] Add a border to the menu (can be part of theming feature)
- [ ] Currently, it looks bad if the app takes like 1 second to load and you just get a tiny flicker of the loading screen. Maybe add a time threshold before the loading screen is presented?
- [ ] Press B (or CTRL+C, whatever) when in menu to quit application

## Applets
- [X] Some kind of Config class for an applet e.g. for the tarkov applet, I want to be able to specify what items to get the values for.
- [X] Add an Applet template
- [X] System Monitor - Scale between red and green for system usage
- [X] Applet Information Viewer - "Name" key isn't in the configuration. Look at the way applets are loaded in app.py. Ben can probably help
- [X] Tarkov Price Tracker - Format price function to include millions
- [X] Tarkov Price Tracker - When BMP files don't exist it goes crazy (on bens pi, works on my machine :nerd:)
- [X] Tarkov Price Tracker - App takes long time to quit when B button pressed
- [X] Tarkov Price Tracker - Move DisplayItem out of applet definition
- [X] Tarkov Price Tracker - Complete refactor - this was the first app created and doesn't use good format e.g. fetching, updating. Use the helldivers apps as references.
- [ ] Tarkov Price Tracker - User pressing A does not do anything if they press A while fetch_data is running. This is because the function is blocking. Consider using async approach but, is it worth it?
- [X] Pong Game - Fix scoreboard
- [X] Pong Game - Styling and formatting - make it look pretty
- [X] Helldivers Counter - Make select button skip (e.g. planets)
- [X] Fix usage of offscreen_canvas in certain applets (Owen)
- [ ] Applet.stop() needs some more sort of memory management - destruction

## README
- [X] Improve README
- [X] Add start() definition into README
- [ ] Add documentation for each applet (e.g. what options it takes etc)

## Other
- [X] APIs - display error message if cannot get data for API for some reason e.g. no network connection

## Input Handling
- [X] Xbox Controller - support debouce (stop joystick movement causing multiple events)

## Applet Ideas:
- [X] Internet speed test
- [ ] Controller Tester
- [ ] Spotify Album Art
- [ ] Background idling thing (clock + runtime potentially overlayed over minimalistic GIF)
- [ ] Snake game
