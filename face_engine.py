from insightface.app import FaceAnalysis
import cv2

app = FaceAnalysis(
    providers=["CPUExecutionProvider"]
)

app.prepare(ctx_id=0)

def get_face_embedding(image):

    faces = app.get(image)

    if not faces:
        return None

    face = faces[0]

    return face.embedding