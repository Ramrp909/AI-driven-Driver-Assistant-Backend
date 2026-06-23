from app.models.telemetry_models import AIEvent
import time

event_memory = {}

def can_trigger_event(

    event_name,

    cooldown=10,
):

    current_time = time.time()

    last_triggered = event_memory.get(
        event_name,
        0
    )

    if (
        current_time - last_triggered
        > cooldown
    ):

        event_memory[event_name] = (
            current_time
        )

        return True

    return False

def generate_events(

    attention_status,

    is_drowsy,
    is_yawning,
    is_talking,
    phone_detected,
    emergency_mode,

    looking_away,

    face_detected,

    gaze_stability,

):

    events = []

    # Critical drowsiness
    if (
    is_drowsy
    and can_trigger_event(
        "Drowsiness Detected",
        cooldown=10
    )
        ):
        events.append(

            AIEvent(

                type="Drowsiness Detected",

                severity="critical",
            )
        )
        
    if (
        is_drowsy
         and can_trigger_event(
        "Emergency Intervention",
        cooldown=20
        )
        ):
        events.append(
        AIEvent(
            type=
                "Emergency Intervention",
            severity=
                "critical",
        )
    )
        
        
    #yawning
    if is_yawning:
        events.append(
            AIEvent(
            type="Yawning Detected",
            severity="warning"
        )
    )
        
    if is_talking:
        events.append(
            AIEvent(
                type="Talking Detected",
                severity="info"
        )
    )
        

    # Driver distracted
    if (
    looking_away
    and can_trigger_event(
        "Driver Distracted",
        cooldown=6
        )
        ):
        events.append(

            AIEvent(

                type="Driver Distracted",

                severity="warning",
            )
        )

    # Driver missing
    if (
    not face_detected
    and can_trigger_event(
        "Driver Not Detected",
        cooldown=8
        )
        ):
        events.append(
            AIEvent(
                type="Driver Not Detected",
                severity="warning",
            )
        )

    # Low gaze stability
    if (
    gaze_stability < 50
    and can_trigger_event(
        "Unstable Attention",
        cooldown=7
       )
        ):
        events.append(
            AIEvent(
                type="Unstable Attention",
                severity="info",
            )
        )
        
    #phone usage
    if phone_detected:
        events.append(
            AIEvent(
            type="Phone Usage Detected",
            severity="critical"
        )
    )
        
    if emergency_mode:
        events.append(
            AIEvent(
                type="Emergency Intervention",
                severity="critical"
            )
        )

    # Stable driving state
    if (
        not is_drowsy
        and not looking_away
        and face_detected
    ):
        events.append(
            AIEvent(
                type="Driver Focus Stable",
                severity="monitoring",
            )
        )
    

    return events