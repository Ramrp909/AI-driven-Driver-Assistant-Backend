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

from app.services.face_detection_service import (
    process_driver_frame
)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "lighting_conditions"
)

results = {}

total = 0
correct = 0

for folder in os.listdir(DATASET_PATH):

    folder_path = os.path.join(
        DATASET_PATH,
        folder
    )

    if not os.path.isdir(folder_path):
        continue

    folder_total = 0
    folder_correct = 0

    for file in os.listdir(folder_path):

        image_path = os.path.join(
            folder_path,
            file
        )

        image = cv2.imread(
            image_path
        )

        if image is None:
            continue

        _, buffer = cv2.imencode(
            ".jpg",
            image
        )

        result = process_driver_frame(
            buffer.tobytes()
        )

        detected = (
            result.driver.faceDetected
        )

        folder_total += 1
        total += 1

        if detected:

            folder_correct += 1
            correct += 1

    results[folder] = (
        folder_correct,
        folder_total
    )

print("\nLIGHTING EVALUATION\n")

for cls, (c, t) in results.items():

    accuracy = (
        c / t * 100
        if t > 0
        else 0
    )

    print(
        f"{cls}: "
        f"{c}/{t} "
        f"({accuracy:.2f}%)"
    )

overall = (
    correct / total * 100
    if total > 0
    else 0
)

print(
    f"\nOverall Face Detection Rate: "
    f"{overall:.2f}%"
)