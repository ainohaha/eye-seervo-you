#!/bin/bash

# 1. Ensure we are in the correct folder
cd "$(dirname "$0")"

echo "👁️  --- I'M WAKING UP ---"

# 2. Kill any old zombies (optional cleanup)
pkill -f "tracker.py"

# 3. Start Python Tracker in the background
echo "Launching Eye Tracker..."
python3 Python_Tracker/tracker.py &

# 4. Wait 3 seconds for the camera to turn on
echo "Waiting to see you..."
sleep 3

# 5. Start Processing Sketch
echo "Launching my face..."
# "$(pwd)/Processing_UI" gets the full path to your sketch folder
processing-java --sketch="$(pwd)/Processing_UI" --run
