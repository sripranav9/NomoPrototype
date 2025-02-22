import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from flask import Flask, Response
from picamera2 import Picamera2
import serial

# Serial to connect to the Raspberry Pi
ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
# Vairables for pyserial
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

# Flask App for Streaming
app = Flask(__name__)

# Global Variables
FACE_DETECTION_RESULT = None
GESTURE_RESULT_LIST = []
FRAME_COUNTER = 0  # For skipping frames
closed_fist_counter = 0
alone_timer_start = None  # Track when no one is detected
COUNTER, FPS = 0, 0
START_TIME = time.time()
LOG_TIMER = time.time()  # Timer for reducing log frequency


# Initialize MediaPipe utilities
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Callback for Face Detection
def face_callback(result: vision.FaceDetectorResult, unused_output_image: mp.Image, timestamp_ms: int):
    global FACE_DETECTION_RESULT
    FACE_DETECTION_RESULT = result

# Callback for Gesture Recognition
def gesture_callback(result: vision.GestureRecognizerResult, unused_output_image: mp.Image, timestamp_ms: int):
    global GESTURE_RESULT_LIST
    GESTURE_RESULT_LIST.append(result)

# Initialize Picamera2
picam2 = Picamera2()
# picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})) # Low resolution
picam2.configure(picam2.create_video_configuration(main={"size": (960, 540), "format": "RGB888"})) # Medium resolution
# picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"})) # HD resolution
picam2.start()

# Function to generate frames with detection and logging
def generate_frames(face_model: str, gesture_model: str, skip_frames: int = 3):
    global FRAME_COUNTER, closed_fist_counter, alone_timer_start, FPS, COUNTER, START_TIME, LOG_TIMER

    # Initialize Face Detection
    face_base_options = python.BaseOptions(model_asset_path=face_model)
    face_options = vision.FaceDetectorOptions(
        base_options=face_base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        min_detection_confidence=0.5,
        min_suppression_threshold=0.3,
        result_callback=face_callback
    )
    face_detector = vision.FaceDetector.create_from_options(face_options)

    # Initialize Gesture Recognition
    gesture_base_options = python.BaseOptions(model_asset_path=gesture_model)
    gesture_options = vision.GestureRecognizerOptions(
        base_options=gesture_base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=gesture_callback
    )
    gesture_recognizer = vision.GestureRecognizer.create_from_options(gesture_options)

    # Variables
    update_interval = 1 # Interval variable for logging and actions in seconds, earlier #2
    last_gesture = None
    gesture_timer = time.time()  # Timer to manage gesture debounce duration

    while True:
        # Capture frame using Picamera2
        frame = picam2.capture_array()

        # Frame Skipping to reduce load
        FRAME_COUNTER += 1
        if FRAME_COUNTER % skip_frames != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run Face Detection
        face_detector.detect_async(mp_image, time.time_ns() // 1_000_000)

        # Run Gesture Recognition
        gesture_recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

        # Count Detected Faces
        num_people = len(FACE_DETECTION_RESULT.detections) if FACE_DETECTION_RESULT else 0

        # Detect Gestures
        gesture_detected = None
        if GESTURE_RESULT_LIST:
            for gesture_result in GESTURE_RESULT_LIST:
                if gesture_result.gestures:
                    current_gesture = gesture_result.gestures[0][0].category_name
                    if current_gesture != last_gesture and time.time() - gesture_timer > update_interval:
                        last_gesture = current_gesture
                        gesture_timer = time.time()  # Reset timer
                    gesture_detected = current_gesture
                    break
            GESTURE_RESULT_LIST.clear()

        
        # Interaction Logic (State-Based Logging)
        if time.time() - LOG_TIMER > update_interval:
            if num_people == 0:
                # Start the "alone" timer if it hasn't started yet
                if  not gesture_detected and alone_timer_start is None:
                    alone_timer_start = time.time()
                
                # Someone is hiding?
                elif gesture_detected:
                    print(f"\n{gesture_detected} detected. Where's your face human? \nAre you a ghost?")
                    ser.write(b'7') # send the command to arduino
                    alone_timer_start = None

                # Check if 10 seconds have elapsed since the "alone" timer started
                elif alone_timer_start is not None and time.time() - alone_timer_start > 10:
                    print("\nWhere's everyone? \nI need people! Talk to me!")
                    ser.write(b'1') # send the command to arduino
                    alone_timer_start = None  # Reset the timer once the message is displayed
            else:
                # Reset the "alone" timer once people are detected
                alone_timer_start = None
                if num_people >= 3:
                    print(f"{num_people} people detected! \nMoving back and closing eyes.")
                    ser.write(b'2') # send the command to arduino
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Open_Palm":
                    print(f"{num_people} people detected with an open palm! \nWaving Back! Hii!")
                    ser.flushInput()  # Clear input buffer
                    ser.write(b'4')   # Send the command
                    ser.flush()       # Ensure the command is sent immediately
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Thumb_Up":
                    print(f"{num_people} people detected with a thumbs-up! \nCheers!")
                    ser.write(b'5') # send the command to arduino
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Closed_Fist":
                    if closed_fist_counter == 1:
                        print(f"Starting desk mode!")
                        ser.write(b'6') # send the command to arduino
                        closed_fist_counter = 0
                    else:
                        print(f"{num_people} people detected with closed fist. \nChecking for desk mode.")
                        closed_fist_counter += 1
                elif num_people > 0:
                    print(f"{num_people} people detected. Awaiting interaction...")
                    ser.write(b'3') # send the command to arduino
                else:
                    continue
            LOG_TIMER = time.time()

        # Draw Bounding Boxes
        if FACE_DETECTION_RESULT:
            for detection in FACE_DETECTION_RESULT.detections:
                bbox = detection.bounding_box
                start_point = (int(bbox.origin_x), int(bbox.origin_y))
                end_point = (int(bbox.origin_x + bbox.width), int(bbox.origin_y + bbox.height))
                cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
                cv2.putText(frame, "Face", (start_point[0], start_point[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if gesture_detected:
            cv2.putText(frame, f"Gesture: {gesture_detected}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Convert to MJPEG Streaming Format
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Flask Route for Video Streaming
@app.route('/nomo')
def nomo():
    return Response(generate_frames("/home/sripranav/Desktop/pi_camera/detector.tflite", "/home/sripranav/Desktop/pi_camera/gesture_recognizer.task", skip_frames=3), mimetype='multipart/x-mixed-replace; boundary=frame')

# Start Flask Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
