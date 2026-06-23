from pydantic import BaseModel
from typing import List

class DriverTelemetry(BaseModel):

    faceDetected: bool

    faceCount: int

    isDrowsy: bool
    isYawning: bool = False
    isTalking: bool = False
    fatigueLevel: str = "Low"
    safetyScore: int = 100
    phoneDetected: bool = False
    warningCount: int = 0
    emergencyMode: bool = False
    recommendedAction: str = ""

    attentionStatus: str

    headDirection: str

    lookingAway: bool

    attentionScore: int

    blinkRate: int
    gazeStability: int

class VisionTelemetry(BaseModel):

    trackingState: str

    meshEnabled: bool

    meshConfidence: float

    pipelineStatus: str

    fps: int

    latency: int

class VehicleTelemetry(BaseModel):

    riskLevel: str

    safetyMode: str

    assistState: str

class AIEvent(BaseModel):

    type: str

    severity: str

class TelemetryResponse(BaseModel):

    driver: DriverTelemetry

    vision: VisionTelemetry

    vehicle: VehicleTelemetry

    events: List[AIEvent]