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
If you're using resources, be sure to add a reference to the directory on the Applet:
```python
class MyAwesomeApplet(Applet):
    def __init__(self, *args, **kwargs):
        super().init("Applet Name", *args, **kwargs)
+       current_directory = os.path.dirname(os.path.realpath(__file__))
+       # assume a dir called 'resources' exists in the same dir
+       self.resources_directory = os.path.join(current_directory, "resources")
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

## TODO:
- [X] NOT HAPPENING - Make something that automatically chmods the resources folder for each individual applet
- [X] Some kind of Config class for an applet e.g. for the tarkov applet, I want to be able to specify what items to get the values for.
- [ ] Applet.stop() needs some more sort of memory management - destruction
- [ ] Improve README
- [X] Add an Applet template
- [X] Scale between red and green for system usage
- [X] Tarkov applet - format price function to include millions
- [ ] Currently, it looks bad if the app takes like 1 second to load and you just get a tiny flicker of the loading screen. Maybe add a time threshold before the loading screen is presented?
- [X] Pong game - scoreboard doesn't work
- [X] Pong game - styling and formatting - make it look pretty
- [ ] Tarkov - when BMP files don't exist it goes crazy (on bens pi, works on my machine :nerd:)
- [ ] Into README add start() definition
- [ ] Tarkov app takes long time to quit when B button pressed
- [ ] Xbox Controller - support debouce (stop joystick movement causing multiple events)
- [ ] APIs - display error message if cannot get data for API for some reason e.g. no network connection
- [ ] Add documentation for each applet (e.g. what options it takes etc)

## Applet Ideas:
- [X] Internet speed test