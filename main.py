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

drowsy_counter = 0
looking_away_counter = 0

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

    head_direction = "Center"
    looking_away = False
    attention_score = 100

    global drowsy_counter
    global looking_away_counter

    # OpenCV face detection
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    face_detected = len(faces) > 0
    if not face_detected:
        attention_status = "No Face"

    # MediaPipe eye tracking
    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:
            # Nose landmark
            nose = face_landmarks.landmark[1]

                # Left and right face landmarks
            left_face = face_landmarks.landmark[234]
            right_face = face_landmarks.landmark[454]

                # Calculate face balance
            left_distance = abs(nose.x - left_face.x)
            right_distance = abs(right_face.x - nose.x)

                # Head direction detection
            if left_distance > right_distance + 0.03:
                head_direction = "Right"
                looking_away = True

            elif right_distance > left_distance + 0.03:
                head_direction = "Left"
                looking_away = True
                

            else:
                head_direction = "Center"
                looking_away = False

            if looking_away:
                looking_away_counter += 1
            else:
                looking_away_counter = 0

            # Confirm only after few frames
            looking_away = looking_away_counter > 3
            if looking_away:
                attention_status = "Distracted"

            # Left eye landmarks
            left_eye_top = face_landmarks.landmark[159]
            left_eye_bottom = face_landmarks.landmark[145]

            # Eye openness distance
            eye_distance = calculate_distance(
                left_eye_top,
                left_eye_bottom
            )

            # Threshold for closed eye

            
            if eye_distance < 0.015 and not looking_away:
                    drowsy_counter += 1
            else:
                     drowsy_counter = 0
            
            if eye_distance < 0.015 and not looking_away:
                if drowsy_counter > 4:
                    is_drowsy = True
                    attention_status = "Drowsy"

            else:
                    is_drowsy = False
                    attention_status = "Focused"

            if attention_status == "Focused":
                attention_score = 96

            elif attention_status == "Distracted":
                attention_score = 65

            elif attention_status == "Drowsy":
                attention_score = 30

            else:
                attention_score = 0



    return {
        "faceDetected": face_detected,
        
        "faceCount": len(faces),
        "isDrowsy": is_drowsy,
        "attentionStatus": attention_status,

        "headDirection": head_direction,
        "lookingAway": looking_away,

        "attentionScore": attention_score,
    }