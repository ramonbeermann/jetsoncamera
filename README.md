# Jetson USB MJPEG Camera

This repository contains a minimal Python example that displays video
from a USB camera which delivers MJPEG frames. The stream is decoded and
shown using a GStreamer pipeline and OpenCV. It is intended for use on
NVIDIA Jetson devices but should work on any Linux system with GStreamer
and a supported camera.

## Requirements

* Python 3
* [OpenCV](https://opencv.org/) built with GStreamer support (preinstalled on Jetson)
* GStreamer runtime libraries
* A USB camera that outputs MJPEG

## Usage

Connect a USB camera to the device and run:

```bash
python usb_cam_mjpeg.py --device /dev/video0 --width 1280 --height 720 --framerate 30
```

Arguments:

| Option | Description |
| ------ | ----------- |
| `--device` | V4L2 device path (default `/dev/video0`) |
| `--width` | Capture width in pixels (default `1280`) |
| `--height` | Capture height in pixels (default `720`) |
| `--framerate` | Frames per second (default `30`) |

Press **ESC** to close the preview window.

## Pipeline Overview

The script constructs the following GStreamer pipeline:

```
v4l2src device=/dev/video0 ! \
  image/jpeg, width=1280, height=720, framerate=30/1 ! \
  jpegdec ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! \
  video/x-raw, format=BGR ! appsink
```

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

