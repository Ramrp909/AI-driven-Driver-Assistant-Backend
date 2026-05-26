from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np
import mediapipe as mp
import math

app = FastAPI()

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
)

import json

from datetime import datetime

from face_engine import (
    get_face_embedding
)

from database import (
    conn,
    cursor,
)
from numpy.linalg import norm
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

def cosine_similarity(a, b):

    return np.dot(a, b) / (
        norm(a) * norm(b)
    )


# Home route
@app.get("/")
def home():
    return {
        "message": "Smart Vehicle AI Backend Running"
    }
@app.post("/register-driver")
async def register_driver(

    name: str = Form(...),

    driving_style: str = Form(...),

    ac_temperature: str = Form(...),

    ambient_mode: str = Form(...),

    seat_position: str = Form(...),

    assistant_voice: str = Form(...),

    file: UploadFile = File(...)
):

    contents = await file.read()

    np_arr = np.frombuffer(
        contents,
        np.uint8
    )

    image = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    embedding = get_face_embedding(
        image
    )

    if embedding is None:

        return {
            "success": False,
            "message": "No face detected"
        }

    cursor.execute(
        """
        INSERT INTO drivers (

            name,

            embedding,

            driving_style,

            ac_temperature,

            ambient_mode,

            seat_position,

            assistant_voice,

            created_at

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,

            json.dumps(
                embedding.tolist()
            ),

            driving_style,

            ac_temperature,

            ambient_mode,

            seat_position,

            assistant_voice,

            datetime.now().isoformat()
        )
    )

    conn.commit()

    return {
        "success": True,
        "message": f"{name} registered"
    }
    
@app.post("/recognize-driver")
async def recognize_driver(
    file: UploadFile = File(...)
):

    contents = await file.read()

    np_arr = np.frombuffer(
        contents,
        np.uint8
    )

    image = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    embedding = get_face_embedding(
        image
    )

    if embedding is None:

        return {
            "matched": False,
            "message": "No face detected"
        }

    cursor.execute(
        "SELECT name, embedding FROM drivers"
    )

    drivers = cursor.fetchall()

    best_match = None
    best_score = 0

    for driver in drivers:

        name = driver[0]

        saved_embedding = np.array(
            json.loads(driver[1])
        )

        similarity = cosine_similarity(
            embedding,
            saved_embedding
        )

        if similarity > best_score:

            best_score = similarity
            best_match = name

    if best_score > 0.45:

        return {
            "matched": True,
            "driver": best_match,
            "confidence": round(
                float(best_score),
                2
            )
        }

    return {
        "matched": False,
        "message": "Unknown driver"
    }
    
@app.delete("/clear-drivers")
async def clear_drivers():

    cursor.execute(
        "DELETE FROM drivers"
    )

    conn.commit()

    return {
        "success": True,
        "message": "All driver profiles cleared"
    }