import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import serial
import time

# Serial to connect to the Raspberry Pi
# ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
# Serial to connect to the MacBook
ser = serial.Serial("/dev/tty.usbmodem11301", 115200, timeout=1)
# Vairables for pyserial
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

# Global Variables
FACE_DETECTION_RESULT = None
GESTURE_RESULT_LIST = []
COUNTER, FPS = 0, 0
START_TIME = time.time()
LOG_TIMER = time.time()  # Timer for reducing log frequency
FRAME_COUNTER = 0  # For skipping frames

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

# Function to initialize and run combined detections
def run(face_model: str, gesture_model: str, camera_id: int, width: int, height: int, skip_frames: int = 3):
    global FPS, COUNTER, START_TIME, LOG_TIMER, FRAME_COUNTER

    # Start capturing video
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

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

    # Variables for debounce and state tracking
    last_num_people = None
    last_gesture = None
    gesture_timer = time.time()  # Timer to manage gesture debounce duration
    update_interval = 2  # Interval for logging and actions in seconds
    closed_fist_counter = 0 # Interval for hold for desk mode
    alone_timer_start = None # Interval to display that it's lonely

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error: Unable to read from the camera.")
            break

        # Frame Skipping
        # This is done to reduce the load on the Raspberry Pi. It only processes every 5th frame.
        FRAME_COUNTER += 1
        if FRAME_COUNTER % skip_frames != 0:
            continue

        frame = cv2.flip(frame, 1)  # Flip for a mirrored view
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run Face Detection
        face_detector.detect_async(mp_image, time.time_ns() // 1_000_000)

        # Run Gesture Recognition
        gesture_recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

        # Count Detected Faces
        num_people = len(FACE_DETECTION_RESULT.detections) if FACE_DETECTION_RESULT else 0

        # Debounce Gesture Recognition
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
                    # ser.write(b'4') # send the command to arduino
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

        # Annotate Frame
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

        # Calculate and display FPS
        COUNTER += 1
        if COUNTER % 10 == 0:
            FPS = 10 / (time.time() - START_TIME)
            START_TIME = time.time()
        cv2.putText(frame, f"FPS: {FPS:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Display the output frame
        cv2.imshow("Face & Gesture Detection", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    face_detector.close()
    gesture_recognizer.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Define the face and gesture models
    face_model_path = "face-detector/detector.tflite"  # Update with the actual path
    gesture_model_path = "gesture-recognition/gesture_recognizer.task"  # Update with the actual path

    # Run the combined detection with frame skipping
    run(face_model_path, gesture_model_path, camera_id=1, width=640, height=480, skip_frames=5)
