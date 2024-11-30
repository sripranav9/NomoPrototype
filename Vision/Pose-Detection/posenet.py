import cv2
import time

# Define body parts and pose pairs
BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
              "LEye": 15, "REar": 16, "LEar": 17, "Background": 18}

POSE_PAIRS = [["Neck", "RShoulder"], ["Neck", "LShoulder"],
              ["RShoulder", "RElbow"], ["RElbow", "RWrist"],
              ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
              ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"],
              ["Neck", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"],
              ["Neck", "Nose"], ["Nose", "REye"], ["REye", "REar"],
              ["Nose", "LEye"], ["LEye", "LEar"]]

# Load the pre-trained pose estimation model
net = cv2.dnn.readNetFromTensorflow("Pose-Detection/graph_opt.pb")

# Open a video capture from the default camera
cap = cv2.VideoCapture(1)
time.sleep(2.0)  # Optional delay to allow camera to initialize

while cv2.waitKey(1) < 0:
    hasFrame, frame = cap.read()
    if not hasFrame:
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    
    # Prepare the frame for pose estimation
    inWidth = 368
    inHeight = 368
    net.setInput(cv2.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight),
                                       (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()

    # List to store detected key points
    points = []
    for i in range(len(BODY_PARTS)):
        heatMap = out[0, i, :, :]
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        
        # Only add keypoint if confidence threshold is met
        points.append((int(x), int(y)) if conf > 0.3 else None)

    # Draw skeleton by connecting keypoints
    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv2.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv2.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)
            cv2.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)

    # Display the frame with annotations
    cv2.imshow("Pose Estimation", frame)

cap.release()
cv2.destroyAllWindows()