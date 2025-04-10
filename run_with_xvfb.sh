#!/bin/bash

# Start Xvfb with a virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Use a different port to avoid conflicts
export WEBUI_PORT=7789

# Run the webui application
python -m src.ui.webui_enhanced

# Kill Xvfb when the application exits
kill $!
