import os
import sys


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import cv2
import json
import numpy as np

from face_engine import get_face_embedding
from database import cursor

from numpy.linalg import norm


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        norm(a) * norm(b)
    )


DATASET_PATH = "dataset/face_recognition"

total = 0
correct = 0

results = {}


def recognize_image(image):

    embedding = get_face_embedding(image)

    if embedding is None:
        return None

    cursor.execute(
        "SELECT name, embedding FROM drivers"
    )

    drivers = cursor.fetchall()

    best_match = None
    best_score = 0

    for driver in drivers:

        name = driver[0]

        saved_embedding = np.array(
            json.loads(driver[1])
        )

        similarity = cosine_similarity(
            embedding,
            saved_embedding
        )

        if similarity > best_score:

            best_score = similarity
            best_match = name

    if best_score > 0.45:
        return best_match

    return "unknown"


for folder in os.listdir(DATASET_PATH):
    print(folder)
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

        image = cv2.imread(image_path)

        if image is None:
            continue

        prediction = recognize_image(
            image
        )

        expected = (
            "unknown"
            if folder == "unknown_driver"
            else folder
        )

        folder_total += 1
        total += 1

        if prediction == expected:

            folder_correct += 1
            correct += 1

    results[folder] = (
        folder_correct,
        folder_total
    )


print("\nFACE RECOGNITION RESULTS\n")

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
    f"\nOverall Accuracy: "
    f"{overall:.2f}%"
)

print(DATASET_PATH)
print(os.listdir(DATASET_PATH))