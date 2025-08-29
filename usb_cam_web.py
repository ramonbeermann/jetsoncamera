import argparse
import cv2
from flask import Flask, Response

app = Flask(__name__)
cap = None
fallback = False


def gstreamer_pipeline(device='/dev/video0', width=1280, height=720, framerate=30):
    return (
        f"v4l2src device={device} ! "
        f"image/jpeg, width={width}, height={height}, framerate={framerate}/1 ! "
        "jpegdec ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
    )


def generate_frames():
    global cap, fallback
    device = app.config['DEVICE']
    width = app.config['WIDTH']
    height = app.config['HEIGHT']
    framerate = app.config['FRAMERATE']
    while True:
        if cap is None:
            pipeline = gstreamer_pipeline(device, width, height, framerate)
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            fallback = False
            if not cap.isOpened():
                print("GStreamer pipeline failed, falling back to V4L2 capture")
                cap = cv2.VideoCapture(device)
                if not cap.isOpened():
                    raise RuntimeError(f"Unable to open camera {device}")
                fallback = True
        ret, frame = cap.read()
        if not ret:
            if not fallback:
                print("GStreamer read failed, falling back to V4L2 capture")
                cap.release()
                cap = cv2.VideoCapture(device)
                if not cap.isOpened():
                    raise RuntimeError(f"Unable to open camera {device}")
                fallback = True
                continue
            else:
                break
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()


@app.route('/')
def index():
    return '<html><body><h1>USB MJPEG Camera</h1><img src="/video_feed"/></body></html>'


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def main(device, width, height, framerate, host, port):
    app.config['DEVICE'] = device
    app.config['WIDTH'] = width
    app.config['HEIGHT'] = height
    app.config['FRAMERATE'] = framerate
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stream MJPEG video from USB camera to web browser')
    parser.add_argument('--device', default='/dev/video0', help='V4L2 device path')
    parser.add_argument('--width', type=int, default=1280, help='Capture width')
    parser.add_argument('--height', type=int, default=720, help='Capture height')
    parser.add_argument('--framerate', type=int, default=30, help='Frame rate')
    parser.add_argument('--host', default='0.0.0.0', help='Web server host')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    args = parser.parse_args()

    main(args.device, args.width, args.height, args.framerate, args.host, args.port)
