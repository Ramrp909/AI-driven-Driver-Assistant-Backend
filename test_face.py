import cv2

from face_engine import (
    get_face_embedding
)

image = cv2.imread(
    "test.jpg"
)

embedding = get_face_embedding(
    image
)

print(type(embedding))
print(len(embedding))