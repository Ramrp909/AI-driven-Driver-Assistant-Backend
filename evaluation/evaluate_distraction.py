import os
import requests

API_URL = "http://localhost:8000/detect-face"

DATASET_ROOT = "../dataset/distraction"

results = {
    "focused": {
        "total": 0,
        "correct": 0
    },
    "looking_away": {
        "total": 0,
        "correct": 0
    },
    "phone_usage": {
        "total": 0,
        "correct": 0
    },
    "talking": {
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


# Focused
folder = os.path.join(
    DATASET_ROOT,
    "focused"
)

for file_name in os.listdir(folder):

    path = os.path.join(folder, file_name)

    response = test_image(path)

    results["focused"]["total"] += 1

    if response["driver"]["attentionStatus"] == "Focused":

        results["focused"]["correct"] += 1


# Looking Away
folder = os.path.join(
    DATASET_ROOT,
    "looking_away"
)

for file_name in os.listdir(folder):

    path = os.path.join(folder, file_name)

    response = test_image(path)

    results["looking_away"]["total"] += 1

    if response["driver"]["lookingAway"]:

        results["looking_away"]["correct"] += 1


# Phone Usage
folder = os.path.join(
    DATASET_ROOT,
    "phone_usage"
)

for file_name in os.listdir(folder):

    path = os.path.join(folder, file_name)

    response = test_image(path)

    results["phone_usage"]["total"] += 1

    if response["driver"]["attentionStatus"] == "Distracted":

        results["phone_usage"]["correct"] += 1


# Talking
folder = os.path.join(
    DATASET_ROOT,
    "talking"
)

for file_name in os.listdir(folder):

    path = os.path.join(folder, file_name)

    response = test_image(path)

    results["talking"]["total"] += 1

    if response["driver"]["attentionStatus"] == "Distracted":

        results["talking"]["correct"] += 1


print("\nDISTRACTION RESULTS\n")

overall_total = 0
overall_correct = 0

for category in results:

    total = results[category]["total"]

    correct = results[category]["correct"]

    overall_total += total
    overall_correct += correct

    accuracy = (
        correct / total
    ) * 100

    print(
        f"{category}: "
        f"{correct}/{total} "
        f"({accuracy:.2f}%)"
    )

overall_accuracy = (
    overall_correct /
    overall_total
) * 100

print(
    f"\nOverall Accuracy: "
    f"{overall_accuracy:.2f}%"
)