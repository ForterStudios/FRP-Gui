# FRP-Gui
A lightweight and user-friendly Tkinter GUI for managing FRP (Fast Reverse Proxy) clients and tunnels.

## Features

* **Proxy Management:** Add and delete TCP/UDP proxies directly via the interface without editing TOML configuration files manually.
* **Automation:** Supports launching the application on Windows startup and automatically starting the FRP client execution.
* **Real-time Logging:** Displays live `frpc` process output and logs in a dedicated tab.
* **Version Tracking:** Automatically fetches and displays the latest available FRP release version using the GitHub API.
* **Status Indication:** Asynchronously loads an animated loading indicator from the internet within the About section.

## Program Windows
<p align="center">
<img width="40%" height="552" alt="appwindow" src="https://github.com/user-attachments/assets/566bce8c-472c-4b79-af67-6805bf81e061" />
<img width="40%" height="852" alt="image" src="https://github.com/user-attachments/assets/3687166a-1cef-41fd-a2f8-f00d2b839561" />
</p>

## Requirements

The application is written in Python using the standard `tkinter` library. No external pip packages are required.

* Python 3.x
* FRP Client (`frpc`) executable
* FRP Client (`frpc`) .toml file (usually comes with FRP)

## Installation and Usage

1. Download the `FRPGui.py` file.
2. Run the script using Python:
   ```bash
   python FRPGui.py

**OR**

Just download and run the Executable from Releases tab (https://github.com/ForterStudios/FRP-Gui/releases)
