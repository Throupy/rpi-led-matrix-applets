# Raspberry Pi LED Matrix Applets
Some small applets that are designed to run on a 64x64 LED matrix with a Raspberry Pi.

# Usage
For information on usage, please see the [wiki](https://github.com/Throupy/rpi-led-matrix-applets/wiki)

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
- [ ] Create 2 dirs in applets/ - 1 for system applets (settings, master, etc. ones that shouldn't be displayed), and another for applets which should be loaded and displayed on the menu.

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
- [ ] Add setup for input handling into README

## Other
- [X] APIs - display error message if cannot get data for API for some reason e.g. no network connection
- [ ] Use font.CharacterWidth in matrix_display.py to allow for height AND width scaling (rabbit hole af)

## Input Handling
- [X] Xbox Controller - support debouce (stop joystick movement causing multiple events)

## Applet Ideas:
- [X] Internet speed test
- [ ] Controller Tester
- [ ] Spotify Album Art
- [X] Background idling thing (clock + runtime potentially overlayed over minimalistic GIF)
- [ ] Snake game

## Bugs
- [ ] Text wrapping inconsistent, see helldivers statistics loading page. Need to wrap on words not chars.
- [ ] Known bug when using tom-thumb font, internet speed test claims there is an overlap
