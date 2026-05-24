from fastapi import APIRouter, File, UploadFile
from app.services.face_detection_service import process_driver_frame

router = APIRouter()

# Face + Drowsiness Detection
@router.post("/detect-face")
async def detect_face(file: UploadFile = File(...)):

    contents = await file.read()

    result = process_driver_frame(contents)

    return result