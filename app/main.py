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

    allow_origins=[
        "http://localhost:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

from app.api.routes.detection import router as detection_router
app.include_router(detection_router)



# Home route
@app.get("/")
def home():
    return {
        "message": "Smart Vehicle AI Backend Running"
    }

