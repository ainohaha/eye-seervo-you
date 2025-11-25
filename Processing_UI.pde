import oscP5.*;
import netP5.*;
import processing.serial.*;

OscP5 oscP5;
Serial myPort;

// Variables from Python
float userX = 0.5;
float userY = 0.5;
int isFacing = 1; 

// Animation variables
float pupilX = 0;
float pupilY = 0;

void setup() {
  size(800, 600);
  
  // 1. Start Listening on Port 9999 (Matches Python)
  oscP5 = new OscP5(this, 9999);
  
  // 2. AUTO-CONNECT TO ARDUINO
  printArray(Serial.list());
  String[] ports = Serial.list();
  String portName = "";
  
  // Look for valid Mac serial ports
  for (int i = 0; i < ports.length; i++) {
    if (ports[i].contains("usbserial") || ports[i].contains("SLAB") || ports[i].contains("usbmodem")) {
      portName = ports[i];
      println("✅ Auto-Detected Arduino at: " + portName);
      break;
    }
  }
  
  if (!portName.equals("")) {
    try {
      myPort = new Serial(this, portName, 115200);
    } catch (Exception e) {
      println("⚠️ Port found but busy. Arduino might be unplugged.");
    }
  } else {
    println("❌ No USB Arduino found. Running in Virtual Mode.");
  }

  // Start pupil in center
  pupilX = width/2;
  pupilY = height/2;
}

void draw() {
  background(20); 
  
  // --- VISUALIZATION ---
  if (isFacing == 1) {
    // Eye Open
    fill(255); 
    stroke(0);
    strokeWeight(4);
    ellipse(width/2, height/2, 400, 250);
    
    float targetPupilX = map(userX, 0, 1, width/2 - 100, width/2 + 100);
    float targetPupilY = map(userY, 0, 1, height/2 - 80, height/2 + 80);
    
    pupilX = lerp(pupilX, targetPupilX, 0.2);
    pupilY = lerp(pupilY, targetPupilY, 0.2);
    
    fill(200, 0, 0);
    noStroke();
    ellipse(pupilX, pupilY, 90, 90);
    fill(255, 150);
    ellipse(pupilX + 20, pupilY - 20, 30, 30); // Glint
    
    fill(255);
    textAlign(CENTER);
    textSize(24);
    text("I SEE YOU", width/2, height - 50);
    
  } else {
    // Eye Closed
    stroke(150);
    strokeWeight(5);
    line(width/2 - 200, height/2, width/2 + 200, height/2);
    
    fill(150);
    textAlign(CENTER);
    textSize(24);
    text("IGNORING YOU (Turn Around)", width/2, height - 50);
  }
  
  // --- SEND TO ARDUINO ---
  if (myPort != null) {
    try {
      String payload = userX + "," + isFacing + "\n";
      myPort.write(payload);
    } catch (Exception e) { }
  }
}

// --- RECEIVE DATA FROM PYTHON ---
void oscEvent(OscMessage theOscMessage) {
  // SPY MODE: Print incoming data to console
  if (theOscMessage.checkAddrPattern("/pose") == true) {
    userX = theOscMessage.get(0).floatValue();
    userY = theOscMessage.get(1).floatValue();
    isFacing = theOscMessage.get(2).intValue();
    
    // Print data to prove connection
    print("Data Received: X=" + userX + " Y=" + userY + " Face=" + isFacing);
    println(" -> Arduino");
  }
}
