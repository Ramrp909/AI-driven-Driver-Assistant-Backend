import cv2

from app.services.phone_detection_service import (
    detect_phone
)

image = cv2.imread(
    "test_phone.png"
)

print(
    detect_phone(image)
)