import cv2
import numpy as np
import mediapipe as mp
import math
import time

from app.models.telemetry_models import (

    DriverTelemetry,

    VisionTelemetry,

    VehicleTelemetry,

    AIEvent,

    TelemetryResponse,
)

from app.services.event_service import generate_events

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
blink_counter = 0

blink_detected = False

blink_start_time = time.time()
gaze_history = []

# Distance helper
def calculate_distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )

def process_driver_frame(contents):
    
    start_time = time.perf_counter()
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
    global blink_counter
    global blink_detected
    global blink_start_time
    global gaze_history

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
    if results.multi_face_landmarks  and len(faces) > 0:

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
            gaze_history.append(
                head_direction
            )

            if len(gaze_history) > 20:
                 gaze_history.pop(0)
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
            if not blink_detected:
                    blink_counter += 1
                    blink_detected = True
            else:
                    drowsy_counter = 0
                    blink_detected = False
            
            # if eye_distance < 0.015 and not looking_away:
            #     # if drowsy_counter > 2:
            #         is_drowsy = True
            #         attention_status = "Drowsy"

            # else:
            #         is_drowsy = False
            #         attention_status = "Focused"
            # if len(faces) == 0:
            #         is_drowsy = False
            #         attention_status = "No Driver"


            # No valid driver detected
        if len(faces) == 0:
            is_drowsy = False
            attention_status = "No Driver"

        # Driver visible → run drowsiness logic
        else:

            if eye_distance < 0.015 and not looking_away:
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

    processing_time = (
    time.perf_counter() - start_time
    )

    latency = int(
    processing_time * 1000
    )

    fps = (
    int(1 / processing_time)
    if processing_time > 0
    else 0
    )

    elapsed_minutes = (
    time.time() - blink_start_time
            ) / 60

    blink_rate = (
    int(blink_counter / elapsed_minutes)
    if elapsed_minutes > 0
    else 0
    )

    center_count = gaze_history.count(
    "Center"
    )

    gaze_stability = (
        int(
            (center_count / len(gaze_history))
            * 100
        )
        if len(gaze_history) > 0
        else 100
    )
    
    events = generate_events(
        attention_status=
            attention_status,
        is_drowsy=
            is_drowsy,
        looking_away=
            looking_away,
        face_detected=
            face_detected,
        gaze_stability=
            gaze_stability,
    )
    
    return TelemetryResponse(

        driver=DriverTelemetry(

        faceDetected=face_detected,

        faceCount=len(faces),

        isDrowsy=is_drowsy,

        attentionStatus=attention_status,

        headDirection=head_direction,

        lookingAway=looking_away,

        attentionScore=attention_score,

        blinkRate=blink_rate,
        gazeStability=gaze_stability,
    ),

    vision=VisionTelemetry(

        trackingState=
            "Locked"
            if face_detected
            else "Lost",

        meshEnabled=True,

        meshConfidence=
            round(0.95
        if face_detected
        else 0.0,2),

           

        pipelineStatus=
            "Operational",

        fps=fps,

        latency=latency,
    ),

    vehicle=VehicleTelemetry(

        riskLevel=

            "Critical"
            if is_drowsy

            else "Warning"
            if looking_away

            else "Low",

        safetyMode=

            "Protection"
            if is_drowsy

            else "Monitoring",

        assistState=

            "Intervention"
            if is_drowsy

            else "Active",
    ),

    events=events,
)
    
    # return {
    #     "faceDetected": face_detected,
        
    #     "faceCount": len(faces),
    #     "isDrowsy": is_drowsy,
    #     "attentionStatus": attention_status,

    #     "headDirection": head_direction,
    #     "lookingAway": looking_away,

    #     "attentionScore": attention_score,
    # }