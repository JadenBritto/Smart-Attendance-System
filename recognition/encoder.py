import face_recognition


def encode_faces(rgb_image, face_locations=None):
    """Generate 128-d face encodings for all faces in the image.
    Returns list of numpy arrays.
    """
    return face_recognition.face_encodings(rgb_image, known_face_locations=face_locations)
