<img width="15%" height="15%" alt="icon-hi-res" src="https://github.com/user-attachments/assets/38d2c412-5595-44da-ae7f-55419df9d6de" />
<br>

# FRP-Gui

A lightweight Python GUI for managing FRP (Fast Reverse Proxy) clients and proxies.

This app provides an easy way to create, edit, and remove FRP tunnel definitions without manually editing TOML files. It also supports running `frpc`, viewing live logs, and optional Windows startup and system tray support.

## Features

* Add, remove, and manage FRP proxy definitions from a graphical interface.
* Automatically reads and updates `frpc.toml` proxy configuration.
* Start and stop the `frpc` client from the app.
* Live log output is shown in the GUI.
* Detects and saves the path to the `frpc` executable and config file.
* Fetches the latest FRP release version from GitHub.
* Optional Windows startup support when using the executable.
* Optional system tray support via `pystray` and `Pillow`.

## Screenshots

<p align="center">
<img width="40%" alt="appwindow" src="https://github.com/user-attachments/assets/566bce8c-472c-4b79-af67-6805bf81e061" />
<img width="40%" alt="image" src="https://github.com/user-attachments/assets/3687166a-1cef-41fd-a2f8-f00d2b839561" />
</p>

## Requirements

* Python 3.x
* `tkinter` (usually included with Python)
* `frpc` executable
* `frpc` TOML config file

Optional dependencies for enhanced features:

* `pystray` — system tray icon support
* `Pillow` — image support for the tray icon

## Installation

1. Clone or download this repository.
2. Install the optional Python dependencies if you want tray support:
   ```bash
   pip install -r requirements.txt
   ```

If you only want the GUI and already have `tkinter`, you can run the script without installing additional packages.

## Usage

1. Place `FRPGui.py` in a folder.
2. Ensure you have an `frpc` executable and a valid `frpc.toml` configuration file.
3. Run the GUI:
   ```bash
   python FRPGui.py
   ```
4. Use the GUI to:
   * Browse for your `frpc` executable.
   * Browse for or set your TOML config file path.
   * Add new proxy entries.
   * Delete existing proxy entries.
   * Start and stop the `frpc` client.

## Configuration

The app stores settings in `frp_gui_config.json` in the same folder as `FRPGui.py`.

Default settings include:

* `frpc.exe` or `./frpc`
* `frpc.toml`
* `127.0.0.1:7000`

## Notes

* The application rewrites the `frpc` config file when proxies are added or removed.
* The app detects `serverAddr` and `serverPort` values from the existing TOML file.
* If tray support is not installed, the app still works as a normal Tkinter window.
* Windows autostart is only available when running the packaged executable or on Windows with the appropriate registry permissions.

## Project Files

* `FRPGui.py` — main application script
* `requirements.txt` — optional dependencies for tray support

## License

This project is shared as-is. Feel free to modify it for your own FRP setup.
