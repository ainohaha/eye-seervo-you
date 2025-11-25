#include <ESP32Servo.h>

// --- CONFIGURATION ---
#define SERVO_PIN 26
#define LED_PIN 13 

// Tuning variables (WIDER RANGE 10-170)
int minAngle = 10;   // Right limit
int maxAngle = 170;  // Left limit

class GazeUI {
  private:
    Servo servo;
    int currentAngle;
    
  public:
    GazeUI() {
      currentAngle = 90; 
    }

    void begin() {
      // 1. Servo Setup
      servo.setPeriodHertz(50); 
      servo.attach(SERVO_PIN, 1000, 2000); 
      
      // 2. LED Setup (ESP32 v3.0 compatible)
      ledcAttach(LED_PIN, 5000, 8);
      
      servo.write(currentAngle);
      ledcWrite(LED_PIN, 255); 
    }

    void interact(float xPos, bool isFacing) {
      if (!isFacing) {
        // TURNED AROUND: Servo centers, LED off
        servo.write(90);
        ledcWrite(LED_PIN, 0);
      } else {
        // 1. SERVO LOGIC (INVERTED & WIDER)
        // Previous: map(..., maxAngle, minAngle)
        // NEW: map(..., minAngle, maxAngle) <--- SWAPPED TO FIX DIRECTION
        // Range: 0.0 -> 10 deg, 1.0 -> 170 deg
        int targetAngle = map((int)(xPos * 100), 0, 100, minAngle, maxAngle);
        
        // Smoothing (85% old, 15% new)
        currentAngle = (currentAngle * 0.85) + (targetAngle * 0.15);
        servo.write(currentAngle);

        // 2. LED LOGIC
        // Mapping Brightness to Angle
        // If Angle 170 (Left) = Dim (20)
        // If Angle 10 (Right) = Bright (255)
        int brightness = map(currentAngle, maxAngle, minAngle, 20, 255);
        
        // Safety constraints
        brightness = constrain(brightness, 0, 255);
        
        // Update LED
        ledcWrite(LED_PIN, brightness);
      }
    }
};

GazeUI jealy;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10); // Fast reading
  jealy.begin();
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Filter glitchy short data
    if (data.length() < 3) return;

    int commaIndex = data.indexOf(',');
    
    if (commaIndex > 0) {
      float xPos = data.substring(0, commaIndex).toFloat();
      bool isFacing = (data.substring(commaIndex + 1).toInt() == 1);
      
      // Filter exact 0.0 glitch unless it's a real string "0"
      if (xPos == 0.0 && data.charAt(0) != '0') return;

      jealy.interact(xPos, isFacing);
    }
  }
}
