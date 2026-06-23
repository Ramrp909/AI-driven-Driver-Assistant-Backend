import os
import sys
import cv2

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.services.face_detection_service import process_driver_frame

DATASET = "dataset/drowsiness/yawning"

for file in os.listdir(DATASET):

    path = os.path.join(DATASET, file)

    image = cv2.imread(path)

    if image is None:
        continue

    _, buffer = cv2.imencode(".jpg", image)

    result = process_driver_frame(
        buffer.tobytes()
    )

    print(
        file,
        result.driver.isYawning
    )