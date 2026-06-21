from ultralytics import YOLO

# Load once at startup
model = YOLO("yolov8n.pt")


def detect_phone(image):

    results = model(
        image,
        verbose=False
    )

    for result in results:

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            label = model.names[
                class_id
            ]

            if label == "cell phone":

                return True

    return False