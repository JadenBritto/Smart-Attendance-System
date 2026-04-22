import face_recognition


def detect_faces(rgb_image):
    """Detect face locations in an RGB image. Returns list of (top, right, bottom, left) tuples."""
    return face_recognition.face_locations(rgb_image, model='hog')
