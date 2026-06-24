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

from app.services.phone_detection_service import (
    detect_phone
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
warning_counter = 0
drowsy_start_time = None
looking_away_counter = 0
blink_counter = 0

blink_detected = False

blink_start_time = time.time()
gaze_history = []
YAWNING_THRESHOLD = 0.05

WARNING_1_SECONDS = 2
WARNING_2_SECONDS = 4
WARNING_3_SECONDS = 6

TALKING_MIN_DISTANCE = 0.015
TALKING_MAX_DISTANCE = 0.05

DROWSY_EYE_THRESHOLD = 0.015

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
    phone_detected = detect_phone(image)

    # OpenCV grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # RGB for MediaPipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Face Mesh processing
    results = face_mesh.process(rgb_image)

    # Default values
    is_drowsy = False
    drowsy_duration = 0
    is_yawning = False
    is_talking = False
    attention_status = "Focused"
    

    head_direction = "Center"
    looking_away = False
    attention_score = 100
    emergency_mode = False
    recommended_action = "Continue Driving"
    

    global drowsy_counter
    global warning_counter
    global drowsy_start_time
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
        warning_counter = 0
        drowsy_start_time = None

    # MediaPipe eye tracking
    if results.multi_face_landmarks  and len(faces) > 0:

        for face_landmarks in results.multi_face_landmarks:
            # Nose landmark
            nose = face_landmarks.landmark[1]

                # Left and right face landmarks
            left_face = face_landmarks.landmark[234]
            right_face = face_landmarks.landmark[454]
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]

            eye_y = (left_eye.y + right_eye.y) / 2
            

                # Calculate face balance
            left_distance = abs(nose.x - left_face.x)
            right_distance = abs(right_face.x - nose.x)

                # Head direction detection
            # if left_distance > right_distance + 0.03:
            #     head_direction = "Right"
            #     looking_away = True

            # elif right_distance > left_distance + 0.03:
            #     head_direction = "Left"
            #     looking_away = True
            
            
            # if nose.y > eye_y + 0.06:
            #     head_direction = "Down"
            #     looking_away = True
            # elif left_distance > right_distance + 0.015:
            #     head_direction = "Right"
            #     looking_away = True
            # elif right_distance > left_distance + 0.015:
            #     head_direction = "Left"
            #     looking_away = True
            # else:
            #     head_direction = "Center"
            #     looking_away = False
            if left_distance > right_distance + 0.015:
                head_direction = "Right"
                looking_away = True
            elif right_distance > left_distance + 0.015:
                head_direction = "Left"
                looking_away = True
            else:
                head_direction = "Center"
                looking_away = False

            if looking_away:
                looking_away_counter += 1
            else:
                looking_away_counter = 0
                
                
            #yawning
            
            upper_lip = face_landmarks.landmark[13]

            lower_lip = face_landmarks.landmark[14]

            mouth_distance = calculate_distance(
                upper_lip,
                lower_lip
            )
            
            # if mouth_distance > 0.05:
            #     is_yawning = True
                
            is_yawning = (
    mouth_distance > YAWNING_THRESHOLD
)
                
            # if ( mouth_distance > 0.015 and mouth_distance < 0.05):
            #     is_talking = True
            is_talking = (
                TALKING_MIN_DISTANCE
                < mouth_distance
                < TALKING_MAX_DISTANCE
            )

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
            if is_drowsy:
                if drowsy_start_time is None:
                    drowsy_start_time = time.time()
                drowsy_duration = (
                    time.time()
                    - drowsy_start_time
                )
            else:
                drowsy_start_time = None
                drowsy_duration = 0
                
                
            # if drowsy_duration > 5:
            #     warning_counter = 1
            # if drowsy_duration > 10:
            #     warning_counter = 2
            # if drowsy_duration > 15:
            #     warning_counter = 3
                
            warning_counter = 0

            if drowsy_duration > WARNING_1_SECONDS:
                warning_counter = 1

            if drowsy_duration > WARNING_2_SECONDS:
                warning_counter = 2

            if drowsy_duration > WARNING_3_SECONDS:
                warning_counter = 3
                
           
    
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
    
   
    
    
    
    fatigue_level = "Low"
    safety_score = 100
    # if is_drowsy:
    #     fatigue_level = "High"
    # elif is_yawning:
    #     fatigue_level = "Medium"
    
    fatigue_score = 0
    if is_yawning:
        fatigue_score += 30
    if is_drowsy:
        fatigue_score += 50
    # if head_direction == "Down":
    #     fatigue_score += 20
    if fatigue_score >= 70:
        fatigue_level = "High"
    elif fatigue_score >= 30:
        fatigue_level = "Medium"
    else:
        fatigue_level = "Low"
    
    if is_drowsy:
        safety_score -= 50
    if is_yawning:
        safety_score -= 20
    if is_talking:
        safety_score -= 10
    if looking_away:
        safety_score -= 25
    if not face_detected:
        safety_score -= 40
        
    if phone_detected:
        safety_score -= 35
    safety_score = max(0,min(100, safety_score))
    # if phone_detected:
    #     attention_status = "Phone Usage"
    if phone_detected:
        attention_status = "Phone Usage"
    elif is_drowsy:
        attention_status = "Drowsy"
    elif looking_away:
        attention_status = "Distracted"
    else:
        attention_status = "Focused"
        
    # emergency_mode = False
    # recommended_action = "Continue Driving"
    # if warning_counter >= 3:
    #         emergency_mode = True
    #         recommended_action = "Pull Over"
    emergency_mode = (warning_counter >= 3 )

    recommended_action = (
            "Pull Over"
            if emergency_mode
            else "Continue Driving"
    )
    
    events = generate_events(
        attention_status=
            attention_status,
        is_drowsy=
            is_drowsy,
        is_yawning=
            is_yawning,
        is_talking = 
            is_talking,
        phone_detected =
            phone_detected,
        looking_away=
            looking_away,
        face_detected=
            face_detected,
        gaze_stability=
            gaze_stability,
        emergency_mode = emergency_mode,
    )
        
    
    
    return TelemetryResponse(

        driver=DriverTelemetry(

        faceDetected=face_detected,

        faceCount=len(faces),

        isDrowsy=is_drowsy,
        isYawning = is_yawning,
        isTalking = is_talking,
        fatigueLevel=fatigue_level,
        safetyScore=safety_score,
        phoneDetected=phone_detected,
        
        warningCount=warning_counter,
        emergencyMode=emergency_mode,
        recommendedAction=recommended_action,

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