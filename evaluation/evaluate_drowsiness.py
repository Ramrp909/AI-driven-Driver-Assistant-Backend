import os
import requests

API_URL = "http://localhost:8000/detect-face"

DATASET_ROOT = "../dataset/drowsiness"

results = {
    "eyes_open": {
        "total": 0,
        "correct": 0
    },
    "eyes_closed": {
        "total": 0,
        "correct": 0
    }
}


def test_image(image_path):

    with open(image_path, "rb") as f:

        files = {
            "file": f
        }

        response = requests.post(
            API_URL,
            files=files
        )

        return response.json()


# Eyes Open
folder = os.path.join(
    DATASET_ROOT,
    "eyes_open"
)

for file_name in os.listdir(folder):

    path = os.path.join(
        folder,
        file_name
    )

    response = test_image(path)

    results["eyes_open"]["total"] += 1

    if response["driver"]["isDrowsy"] is False:

        results["eyes_open"]["correct"] += 1


# Eyes Closed
folder = os.path.join(
    DATASET_ROOT,
    "eyes_closed"
)

for file_name in os.listdir(folder):

    path = os.path.join(
        folder,
        file_name
    )

    response = test_image(path)

    results["eyes_closed"]["total"] += 1

    if response["driver"]["isDrowsy"] is True:

        results["eyes_closed"]["correct"] += 1


print("\nDROWSINESS RESULTS\n")

for category in results:

    total = results[category]["total"]

    correct = results[category]["correct"]

    accuracy = (
        correct / total
    ) * 100

    print(
        f"{category}: "
        f"{correct}/{total} "
        f"({accuracy:.2f}%)"
    )