# FRP-Gui
A lightweight and user-friendly Tkinter GUI for managing FRP (Fast Reverse Proxy) clients and tunnels.

## Features

* **Proxy Management:** Add and delete TCP/UDP proxies directly via the interface without editing TOML configuration files manually.
* **Automation:** Supports launching the application on Windows startup and automatically starting the FRP client execution.
* **Real-time Logging:** Displays live `frpc` process output and logs in a dedicated tab.
* **Version Tracking:** Automatically fetches and displays the latest available FRP release version using the GitHub API.
* **Status Indication:** Asynchronously loads an animated loading indicator from the internet within the About section.

## Requirements

The application is written in Python using the standard `tkinter` library. No external pip packages are required.

* Python 3.x
* FRP Client (`frpc`) executable

## Installation and Usage

1. Download the `FRPGui.py` file.
2. Run the script using Python:
   ```bash
   python FRPGui.py

**OR**

Just download and run the Executable from Releases tab (https://github.com/ForterStudios/FRP-Gui/releases)
