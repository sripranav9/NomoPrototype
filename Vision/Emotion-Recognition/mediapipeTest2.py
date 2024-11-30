import csv
import copy
import itertools
import cv2 as cv
import mediapipe as mp

def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    return number, mode

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])
    return landmark_point

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = temp_landmark_list[0]
    for index, landmark_point in enumerate(temp_landmark_list):
        temp_landmark_list[index][0] -= base_x
        temp_landmark_list[index][1] -= base_y
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(map(abs, temp_landmark_list))
    return [n / max_value for n in temp_landmark_list]

def logging_csv(number, mode, landmark_list):
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])

def draw_annotations(debug_image, landmark_list, mode, label):
    # Draw landmarks
    for (x, y) in landmark_list:
        cv.circle(debug_image, (x, y), 3, (0, 255, 0), -1)

    # Draw bounding rectangle
    x_min = min([x for (x, _) in landmark_list])
    y_min = min([y for (_, y) in landmark_list])
    x_max = max([x for (x, _) in landmark_list])
    y_max = max([(_, y) for (_, y) in landmark_list])
    cv.rectangle(debug_image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

    # Show mode and label
    if mode == 1:
        cv.putText(debug_image, f"Recording Mode: Label {label}", (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv.LINE_AA)

cap_device = 1  # Change to 1 if necessary
cap_width = 1280
cap_height = 720

cap = cv.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

mode = 0
number = -1

while True:
    key = cv.waitKey(10)
    if key == 27:  # ESC to exit
        break
    number, mode = select_mode(key, mode)

    ret, image = cap.read()
    if not ret:
        break
    image = cv.flip(image, 1)
    debug_image = copy.deepcopy(image)

    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmark_list = calc_landmark_list(debug_image, face_landmarks)
            pre_processed_landmark_list = pre_process_landmark(landmark_list)
            logging_csv(number, mode, pre_processed_landmark_list)
            draw_annotations(debug_image, landmark_list, mode, number)

    cv.imshow('Facial Emotion Recognition', debug_image)

cap.release()
cv.destroyAllWindows()
