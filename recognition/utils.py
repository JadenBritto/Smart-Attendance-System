import base64
import numpy as np
import cv2


def base64_to_image(base64_string):
    """Convert a base64-encoded image string to a numpy array (BGR)."""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    img_bytes = base64.b64decode(base64_string)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)


def image_to_rgb(bgr_image):
    """Convert BGR image to RGB for face_recognition."""
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)


def resize_image(image, max_width=640):
    """Resize image if wider than max_width, preserving aspect ratio."""
    h, w = image.shape[:2]
    if w > max_width:
        scale = max_width / w
        return cv2.resize(image, (max_width, int(h * scale)))
    return image
