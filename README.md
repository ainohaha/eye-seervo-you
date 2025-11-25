# eye-seervo-you

A little interactive installation that only looks at you when you look at it.

If you make eye contact, the physical servo and digital eye track your movement. If you turn your back, it ignores you completely.

### how it acts

  * **I See You:** When you face the camera, the on-screen eye opens, and the physical servo rotates to follow you.
  * **Ignoring You:** If you turn away (or the camera can't see your eyes), the system shuts down—the eye closes, the servo centers, and the LED turns off.

### the stack

  * **Python (Vision):** Uses `MediaPipe` to track your nose and eye visibility. Sends coordinate data via OSC.
  * **Processing (Bridge):** Renders the digital eye interface and forwards tracking data to the hardware via Serial.
  * **ESP32 (Hardware):** Controls a servo motor (movement) and an LED (brightness based on angle).

### setup

**1. Hardware**

  * Connect a Servo to **Pin 26**.
  * Connect an LED to **Pin 13**.
  * Flash `Arduino_Firmware.ino` to your ESP32.

**2. Software**
Install the Python dependencies:

```bash
pip install opencv-python mediapipe python-osc
```

**3. Run it**
Mac/Linux users can use the helper script to launch everything at once:

```bash
./start_system.sh
```

*(This script kills old processes, starts the Python tracker, waits for the camera, and then launches the Processing sketch.)*

-----

### logic notes

  * **Data Throttling:** The Python tracker limits updates to \~20 FPS to prevent flooding the ESP32.
  * **Auto-Connect:** The Processing sketch automatically hunts for a valid serial port (usbserial/SLAB/usbmodem) so you don't have to hardcode it.

-----

**Next Step:** Would you like me to create a `requirements.txt` file to go along with this so people can install the dependencies in one command?
