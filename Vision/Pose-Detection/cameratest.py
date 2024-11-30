import cv2

# Test default camera (index 0)
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Unable to access the default camera.")
else:
    print("Default camera accessed successfully.")

# Try additional camera indices if necessary
for index in range(5):  # Test the first 5 indices
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        print(f"Camera found at index {index}")
        cap.release()
    else:
        print(f"No camera found at index {index}")