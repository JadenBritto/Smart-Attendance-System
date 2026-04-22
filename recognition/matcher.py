import numpy as np

def match_faces(unknown_encodings, known_encodings, known_ids, tolerance=0.5):
    """Match unknown face encodings against known ones — vectorized & fast.

    Speedups vs. original:
      1. Pure NumPy vectorized distance matrix — no Python loop over known faces,
         no face_recognition.face_distance() call per unknown face.
      2. Single batched matrix operation: all unknowns vs. all knowns at once.
      3. L2 distances via einsum (avoids sqrt until the very end with np.sqrt
         on only the best-match column, keeping memory low).

    Args:
        unknown_encodings : list/array of 128-d numpy arrays (faces to identify)
        known_encodings   : list/array of 128-d numpy arrays (registered faces)
        known_ids         : list of student IDs matching known_encodings
        tolerance         : distance threshold (lower = stricter, default 0.5)

    Returns:
        list of dicts {'student_id', 'confidence'} per unknown face, or None if
        no match found within tolerance.
    """
    if not known_encodings:
        return [None] * len(unknown_encodings)

    # Shape: (K, 128) and (U, 128)
    known_np   = np.array(known_encodings, dtype=np.float32)
    unknown_np = np.array(unknown_encodings, dtype=np.float32)

    # ------------------------------------------------------------------ #
    # Vectorized squared-L2 distance matrix  (U x K)                     #
    #   ||u - k||² = ||u||² + ||k||² - 2·u·kᵀ                           #
    # ------------------------------------------------------------------ #
    u_sq = np.einsum('ij,ij->i', unknown_np, unknown_np)[:, None]  # (U,1)
    k_sq = np.einsum('ij,ij->i', known_np,   known_np  )[None, :]  # (1,K)
    sq_dists = u_sq + k_sq - 2.0 * (unknown_np @ known_np.T)       # (U,K)
    sq_dists = np.maximum(sq_dists, 0.0)                            # clip fp noise

    best_idx   = np.argmin(sq_dists, axis=1)                        # (U,)
    best_sq    = sq_dists[np.arange(len(unknown_np)), best_idx]     # (U,)
    best_dists = np.sqrt(best_sq)                                   # (U,)

    results = []
    for dist, idx in zip(best_dists, best_idx):
        if dist <= tolerance:
            results.append({
                'student_id': known_ids[idx],
                'confidence': round(float(1.0 - dist), 4),
            })
        else:
            results.append(None)

    return results