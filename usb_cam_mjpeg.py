import argparse
import cv2


def gstreamer_pipeline(device='/dev/video0', width=1280, height=720, framerate=30):
    return (
        f"v4l2src device={device} ! "
        f"image/jpeg, width={width}, height={height}, framerate={framerate}/1 ! "
        "jpegdec ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
    )


def display_camera(device='/dev/video0', width=1280, height=720, framerate=30):
    pipeline = gstreamer_pipeline(device, width, height, framerate)
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    fallback = False
    if not cap.isOpened():
        # Fallback to a direct V4L2 capture if the GStreamer pipeline fails to open
        print("GStreamer pipeline failed, falling back to V4L2 capture")
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise RuntimeError(f"Unable to open camera {device}")
        fallback = True

    window = 'USB MJPEG Camera'
    cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if not fallback:
                    # Try switching to direct capture once on internal data stream error
                    print("GStreamer read failed, falling back to V4L2 capture")
                    cap.release()
                    cap = cv2.VideoCapture(device)
                    fallback = True
                    if not cap.isOpened():
                        raise RuntimeError(f"Unable to open camera {device}")
                    continue
                break
            cv2.imshow(window, frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display MJPEG stream from USB camera using OpenCV')
    parser.add_argument('--device', default='/dev/video0', help='V4L2 device path')
    parser.add_argument('--width', type=int, default=1280, help='Capture width')
    parser.add_argument('--height', type=int, default=720, help='Capture height')
    parser.add_argument('--framerate', type=int, default=30, help='Frame rate')
    args = parser.parse_args()
    display_camera(args.device, args.width, args.height, args.framerate)
