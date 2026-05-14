from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np
import mediapipe as mp
import math

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenCV Face Detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
)

# Distance helper
def calculate_distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )

# Home route
@app.get("/")
def home():
    return {
        "message": "Smart Vehicle AI Backend Running"
    }

# Face + Drowsiness Detection
@app.post("/detect-face")
async def detect_face(file: UploadFile = File(...)):

    # Read uploaded image
    contents = await file.read()

    # Convert image
    np_array = np.frombuffer(contents, np.uint8)

    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # OpenCV grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # RGB for MediaPipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Face Mesh processing
    results = face_mesh.process(rgb_image)

    # Default values
    is_drowsy = False
    attention_status = "Focused"

    # OpenCV face detection
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # MediaPipe eye tracking
    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            # Left eye landmarks
            left_eye_top = face_landmarks.landmark[159]
            left_eye_bottom = face_landmarks.landmark[145]

            # Eye openness distance
            eye_distance = calculate_distance(
                left_eye_top,
                left_eye_bottom
            )

            # Threshold for closed eye
            if eye_distance < 0.015:
                is_drowsy = True
                attention_status = "Drowsy"

            else:
                attention_status = "Focused"

    return {
        "faceDetected": len(faces) > 0,
        "faceCount": len(faces),
        "isDrowsy": is_drowsy,
        "attentionStatus": attention_status
    }