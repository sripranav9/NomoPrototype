from picamera2 import Picamera2
from flask import Flask, Response
import io
import cv2

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"}))
picam2.start()

def generate_frames():
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
