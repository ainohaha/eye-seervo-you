import cv2
import mediapipe as mp
from pythonosc import udp_client
import time

# --- CONFIGURATION ---
# Use same Port to ensure a clean connection with Processing
client = udp_client.SimpleUDPClient("127.0.0.1", 9999)

# --- MEDIAPIPE SETUP ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0)

print("👁️ TRACKER STARTED on Port 9999")
print("Logic: Eye Visibility + Data Throttling Enabled")
print("Press 'ESC' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Flip frame for "Mirror" feel
    frame = cv2.flip(frame, 1)
    
    # 2. Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    # Default values (Center, turned away)
    nose_x = 0.5
    nose_y = 0.5
    is_facing = 0

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # --- 1. EXTRACT COORDINATES ---
        nose_x = landmarks[mp_pose.PoseLandmark.NOSE].x
        nose_y = landmarks[mp_pose.PoseLandmark.NOSE].y
        
        # --- 2. DETECT "TURNING AROUND" (EYE LOGIC) ---
        # Check visibility of eyes and nose
        left_eye_vis = landmarks[mp_pose.PoseLandmark.LEFT_EYE].visibility
        right_eye_vis = landmarks[mp_pose.PoseLandmark.RIGHT_EYE].visibility
        nose_vis = landmarks[mp_pose.PoseLandmark.NOSE].visibility
        
        # Average the visibility score (0.0 = Invisible, 1.0 = Clear)
        avg_visibility = (left_eye_vis + right_eye_vis + nose_vis) / 3.0
        
        # THRESHOLD: If score > 0.6, we are looking at the camera.
        # If you turn around, this score drops drastically.
        if avg_visibility > 0.6:
            is_facing = 1 # Facing Camera
            status_text = f"EYE CONTACT ({int(avg_visibility*100)}%)"
            color = (0, 255, 0) # Green
        else:
            is_facing = 0 # Back Turned
            status_text = f"NO EYES ({int(avg_visibility*100)}%)"
            color = (0, 0, 255) # Red

        # --- 3. SEND TO PROCESSING ---
        # Format: [float x, float y, int facing]
        client.send_message("/pose", [float(nose_x), float(nose_y), int(is_facing)])

        # --- 4. VISUAL DEBUGGING ---
        h, w, c = frame.shape
        
        # Draw Visibility Bar (Top Left)
        cv2.rectangle(frame, (10, 60), (200, 80), (50, 50, 50), -1)
        bar_width = int(avg_visibility * 190)
        cv2.rectangle(frame, (10, 60), (10 + bar_width, 80), color, -1)
        
        # Status Text
        cv2.putText(frame, status_text, (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw Skeleton
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show the window
    cv2.imshow('Python Tracker', frame)
    
    # --- 5. THROTTLE DATA (CRITICAL FOR ARDUINO) ---
    # Sleep for 50ms to limit speed to ~20 FPS.
    # This prevents flooding the ESP32 and causing servo glitches.
    time.sleep(0.05)

    # Exit if 'ESC' key is pressed
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
