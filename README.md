# AI-driven Driver Assistant Backend (ADDA)

**Backend for Intelligent Vehicle Driver Monitoring System**

A real-time driver monitoring and safety system leveraging computer vision, deep learning, and AI to detect drowsiness, distraction, and unsafe driving behaviors. The system provides real-time alerts, emergency intervention triggers, and automated parking assistance.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Backend](#running-the-backend)
- [Running Frontend](#running-frontend)
- [API Overview](#api-overview)
- [Evaluation & Testing](#evaluation--testing)
- [Dataset](#dataset)
- [Performance Metrics](#performance-metrics)
- [Architecture Diagrams](#architecture-diagrams)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## 🎯 Overview

ADDA is a Final Year Engineering Project that implements an intelligent driver monitoring system. The backend continuously analyzes video frames from a dashboard camera using:

- **Face Detection & Recognition**: Identify drivers and monitor facial features
- **Drowsiness Detection**: Eye closure and yawning detection
- **Distraction Monitoring**: Head pose, gaze tracking, and phone usage detection
- **Emergency Response**: Multi-level warning system and automated parking assist
- **Real-time Telemetry**: Performance metrics, FPS, latency, confidence scores

**Design Principle**: Safety-critical system that prioritizes driver intervention over false negatives.

---

## ✨ Features

### Core Monitoring

- ✅ **Real-time Face Detection** - OpenCV cascade + MediaPipe mesh (468 landmarks)
- ✅ **Drowsiness Detection** - Eye closure tracking with configurable thresholds
- ✅ **Yawning Detection** - Mouth distance analysis
- ✅ **Head Pose Estimation** - Forward/Left/Right/Down directions
- ✅ **Gaze Stability** - Eye movement consistency tracking
- ✅ **Phone Detection** - YOLOv8 nano for cell phone objects

### Driver Management

- ✅ **Driver Registration** - Face embedding storage with InsightFace
- ✅ **Driver Recognition** - Cosine similarity matching (threshold: 0.45)
- ✅ **Profile Persistence** - SQLite driver database with preferences
- ✅ **Multi-Driver Support** - Handle multiple registered drivers

### Safety Systems

- ✅ **Warning Escalation** - 3-tier alert system (Yellow/Orange/Red)
- ✅ **Emergency Mode** - Triggered at warning level 3+
- ✅ **Event System** - Categorized events with severity levels
- ✅ **Telemetry Streaming** - Real-time metrics to frontend
- ✅ **Latency Optimization** - <100ms target per frame

### Evaluation & Analytics

- ✅ **Comprehensive Testing** - 5 evaluation scripts covering all features
- ✅ **CSV & JSON Reports** - Metrics export for analysis
- ✅ **Visual Charts** - Performance graphs generation
- ✅ **Category-wise Accuracy** - Detailed breakdown per detection type

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.136.1 |
| **Server** | Uvicorn | 0.46.0 |
| **Computer Vision** | OpenCV | 4.13.0.92 |
| **Face Mesh** | MediaPipe | 0.10.14 |
| **Object Detection** | YOLOv8 (nano) | Latest |
| **Face Recognition** | InsightFace | 1.0.1 |
| **Data Validation** | Pydantic | 2.13.4 |
| **Database** | SQLite 3 | Native |
| **Numerical Compute** | NumPy | 2.2.6 |
| **Inference** | ONNX Runtime | 1.23.2 |
| **CORS** | FastAPI Middleware | Built-in |
| **Language** | Python | 3.8+ |

---

## 📁 Repository Structure

```
AI-driven-Driver-Assistant-Backend/
│
├── app/                              # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application + routes (register, recognize)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── detection.py          # POST /detect-face endpoint
│   ├── services/
│   │   ├── face_detection_service.py # Core ML pipeline (drowsiness, head pose, gaze)
│   │   ├── phone_detection_service.py # YOLOv8 phone detection wrapper
│   │   └── event_service.py          # Event generation & cooldown system
│   └── models/
│       └── telemetry_models.py       # Pydantic schemas (DriverTelemetry, VisionTelemetry)
│
├── evaluation/                       # Testing & benchmarking
│   ├── evaluate_drowsiness.py        # Test eyes_open, eyes_closed, yawning, fatigued
│   ├── evaluate_distraction.py       # Test focused, looking_away, phone_usage, talking
│   ├── evaluate_face_recognition.py  # Test driver matching accuracy
│   ├── evaluate_head_pose.py         # Test forward, left, right directions
│   ├── evaluate_lighting.py          # Test daylight, indoor, low_light, night conditions
│   ├── generate_csv.py               # Export results to CSV
│   ├── generate_charts.py            # Create matplotlib visualizations
│   ├── generate_report.py            # Generate text report
│   ├── test_yawning_threshold.py     # Threshold tuning utility
│   └── results/
│       ├── metrics.json              # Aggregated accuracy metrics
│       ├── report.txt                # Summary report
│       ├── drowsiness_results.csv
│       ├── distraction_results.csv
│       ├── face_recognition_results.csv
│       ├── head_pose_results.csv
│       ├── lighting_results.csv
│       └── charts/                   # Generated performance graphs
│
├── dataset/                          # Training & evaluation datasets
│   ├── drowsiness/
│   │   ├── eyes_open/               # Alert driver state (negative example)
│   │   ├── eyes_closed/             # Drowsy state (positive example)
│   │   ├── yawning/                 # Fatigue indicator
│   │   └── fatigued/                # Low energy state
│   ├── distraction/
│   │   ├── focused/                 # Eyes on road
│   │   ├── looking_away/            # Head turned (distracted)
│   │   ├── phone_usage/             # Cell phone visible
│   │   └── talking/                 # Mouth moving (communication)
│   ├── face_recognition/
│   │   ├── ram/                     # Driver identity 1
│   │   ├── saketh/                  # Driver identity 2
│   │   └── unknown_driver/          # Unregistered faces
│   ├── head_pose/
│   │   ├── forward/                 # 0° yaw
│   │   ├── left/                    # Negative yaw
│   │   ├── right/                   # Positive yaw
│   │   └── down/                    # Downward gaze
│   └── lighting_conditions/
│       ├── daylight/                # Bright external lighting
│       ├── indoor/                  # Office/interior lighting
│       ├── low_light/               # Twilight/evening
│       └── night/                   # No ambient light, infrared only
│
├── database.py                       # SQLite connection & driver table schema
├── face_engine.py                    # InsightFace wrapper for embeddings
├── run.py                            # Entry point (python run.py)
├── requirements.txt                  # Core dependencies (minimal)
├── requirements-full.txt             # All dependencies with versions
├── requirements-lock.txt             # Locked version snapshot
├── drivers.db                        # SQLite database (driver profiles)
├── yolov8n.pt                        # Pre-trained YOLOv8 nano weights
│
├── FRONTEND_REFERENCE_FOR_BACKEND.md # Frontend API contract (READ FIRST)
├── README.md                         # This file
└── .gitignore                        # Ignored files
```

---

## 💻 Installation

### Prerequisites

- **Python 3.8+** (tested on 3.10, 3.11)
- **pip** package manager
- **Git** for version control
- **~2GB disk space** for models (YOLOv8, InsightFace)
- **GPU recommended** (NVIDIA CUDA 11.8+) for real-time performance

### Clone Repository

```bash
git clone https://github.com/Ramrp909/AI-driven-Driver-Assistant-Backend.git
cd AI-driven-Driver-Assistant-Backend
```

### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install Dependencies

```bash
# Option 1: Core dependencies only (minimal)
pip install -r requirements.txt

# Option 2: Full dependencies with all extras
pip install -r requirements-full.txt

# Option 3: Use locked versions (recommended for reproducibility)
pip install -r requirements-lock.txt
```

### Download Pre-trained Models

Models are auto-downloaded on first run:

- **YOLOv8 nano** (`yolov8n.pt`) - ~6.5 MB, auto-fetched by ultralytics
- **InsightFace** - Auto-fetched when first embedding is requested

Manual download (if needed):

```bash
# YOLOv8
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# InsightFace (embedded in face_engine.py, loads on first use)
```

---

## 🔧 Environment Setup

### Development Environment

Create `.env` file in project root:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True
RELOAD=True

# CORS Configuration (Development)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Database
DATABASE_PATH=drivers.db

# Model Paths
YOLO_MODEL_PATH=yolov8n.pt
INSIGHTFACE_PROVIDER=CPUExecutionProvider  # or CUDAExecutionProvider

# Processing
TARGET_FPS=30
TARGET_LATENCY_MS=100
```

### Production Environment

```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=False
RELOAD=False

CORS_ORIGINS=["https://your-domain.com"]

DATABASE_PATH=/var/lib/adda/drivers.db
LOG_LEVEL=INFO
INSIGHTFACE_PROVIDER=CUDAExecutionProvider

TARGET_FPS=30
TARGET_LATENCY_MS=100
```

---

## 🚀 Running the Backend

### Development Mode

```bash
# Start with auto-reload
python run.py

# OR direct uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
INFO:     Reloading on file changes
```

### Production Mode

```bash
# No reload, optimized startup
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Health Check

```bash
curl http://127.0.0.1:8000/
# Response: {"message": "Smart Vehicle AI Backend Running"}
```

---

## 🎨 Running Frontend

The frontend is a separate React application. See `FRONTEND_REFERENCE_FOR_BACKEND.md` for integration details.

**Frontend Expectations:**
- Backend URL: `http://127.0.0.1:8000` (development) or `/api` (production)
- CORS headers must be configured
- Endpoints: `/detect-face`, `/recognize-driver`, `/register-driver`

---

## 📡 API Overview

### 1. `/detect-face` (POST)

Real-time driver monitoring with comprehensive telemetry.

**Request:**
```http
POST /detect-face HTTP/1.1
Content-Type: multipart/form-data

file: <JPEG image binary (640x480 to 1280x720)>
```

**Response:**
```json
{
  "driver": {
    "faceDetected": true,
    "faceCount": 1,
    "isDrowsy": false,
    "isYawning": false,
    "isTalking": false,
    "phoneDetected": false,
    "warningCount": 0,
    "emergencyMode": false,
    "recommendedAction": "Continue Driving",
    "fatigueLevel": "Low",
    "safetyScore": 95,
    "attentionStatus": "Focused",
    "blinkRate": 18,
    "gazeStability": 92,
    "headDirection": "Center",
    "lookingAway": false,
    "attentionScore": 96
  },
  "vision": {
    "trackingState": "Locked",
    "meshEnabled": true,
    "meshConfidence": 0.95,
    "pipelineStatus": "Operational",
    "fps": 28,
    "latency": 42
  },
  "vehicle": {
    "riskLevel": "Low",
    "safetyMode": "Monitoring",
    "assistState": "Active"
  },
  "events": [
    {
      "type": "Driver Focus Stable",
      "severity": "monitoring"
    }
  ]
}
```

**Latency Target:** <100ms  
**Frequency:** Every ~33ms (30 FPS)

---

### 2. `/recognize-driver` (POST)

Identify driver from face image.

**Request:**
```http
POST /recognize-driver HTTP/1.1
Content-Type: multipart/form-data

file: <JPEG image binary>
```

**Response:**
```json
{
  "matched": true,
  "driver": "Alex Driver",
  "confidence": 0.87
}
```

Or (unknown driver):
```json
{
  "matched": false,
  "message": "Unknown driver"
}
```

**Threshold:** 0.45 cosine similarity = matched

---

### 3. `/register-driver` (POST)

Register new driver with face embedding.

**Request:**
```http
POST /register-driver HTTP/1.1
Content-Type: multipart/form-data

name: "Alex Driver"
driving_style: "Smooth"
ac_temperature: "22"
ambient_mode: "dim"
seat_position: "{\"horizontal\": 50, \"vertical\": 50, \"lumbar\": 60}"
assistant_voice: "male"
file: <JPEG image binary>
```

**Response:**
```json
{
  "success": true,
  "message": "Alex Driver registered"
}
```

---

### 4. `/clear-drivers` (DELETE)

Clear all driver profiles from database.

```http
DELETE /clear-drivers HTTP/1.1
```

**Response:**
```json
{
  "success": true,
  "message": "All driver profiles cleared"
}
```

---

## 🧪 Evaluation & Testing

### Run All Evaluations

```bash
cd evaluation

# Test drowsiness detection
python evaluate_drowsiness.py

# Test distraction detection
python evaluate_distraction.py

# Test face recognition
python evaluate_face_recognition.py

# Test head pose estimation
python evaluate_head_pose.py

# Test lighting robustness
python evaluate_lighting.py

# Generate CSV reports
python generate_csv.py

# Generate charts
python generate_charts.py

# Generate text report
python generate_report.py
```

### View Results

```bash
# Text report
cat results/report.txt

# JSON metrics
cat results/metrics.json

# CSV files
ls results/*.csv

# Charts
open results/charts/  # or explorer on Windows
```

---

## 📊 Dataset

### Structure & Categories

| Dataset | Categories | Purpose |
|---------|-----------|---------|
| **drowsiness** | eyes_open, eyes_closed, yawning, fatigued | Fatigue detection training |
| **distraction** | focused, looking_away, phone_usage, talking | Attention tracking |
| **face_recognition** | ram, saketh, unknown_driver | Driver identity validation |
| **head_pose** | forward, left, right, down | Gaze direction estimation |
| **lighting_conditions** | daylight, indoor, low_light, night | Robustness testing |

### Usage

```python
# Images are evaluated during test runs
# Results saved to evaluation/results/
# Dataset is NOT part of repository (download separately if needed)
```

---

## 📈 Performance Metrics

### Current Evaluation Results

**Face Recognition:**
- ram: 100.0%
- saketh: 100.0%
- unknown_driver: 100.0%
- **Overall: 100.0%**

**Drowsiness Detection:**
- eyes_open: 100.0%
- eyes_closed: 100.0%
- fatigued: 38.89%
- yawning: 44.44%

**Distraction Detection:**
- focused: 100.0%
- looking_away: 31.25%
- phone_usage: 82.61%
- talking: 100.0%

**Head Pose Estimation:**
- forward: 75.0%
- left: 95.0%
- right: 80.0%
- **Overall: 83.33%**

**Lighting Robustness:**
- daylight: 100.0%
- indoor: 100.0%
- low_light: 100.0%
- night: 100.0%
- **Overall: 100.0%**

### Real-time Performance

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **FPS** | 24-30 | ~28 | ✅ |
| **Latency** | <100ms | ~42ms | ✅ |
| **Memory** | <512MB | ~300MB | ✅ |
| **CPU Usage** | <80% | ~45% | ✅ |

---

## 🏗️ Architecture Diagrams

### System Flow

```
┌─────────────────┐
│   Webcam/Camera │
└────────┬────────┘
         │ (JPEG frames)
         ▼
┌──────────────────────────┐
│   Backend (FastAPI)      │
├──────────────────────────┤
│ /detect-face endpoint    │
│ - Read image             │
│ - Preprocess (BGR→RGB)   │
└─────────┬────────────────┘
          │
    ┌─────▼──────────────────────────────┐
    │ Face Detection Service             │
    ├────────────────────────────────────┤
    │ 1. OpenCV CascadeClassifier        │
    │ 2. MediaPipe Face Mesh (468 pts)   │
    │ 3. Calculate distances (eyes, mouth)│
    │ 4. Detect drowsiness, yawning      │
    │ 5. Head pose estimation            │
    │ 6. Gaze tracking & stability       │
    └─────┬──────────────────────────────┘
          │
    ┌─────▼──────────────────────────────┐
    │ Phone Detection Service            │
    ├────────────────────────────────────┤
    │ YOLOv8 nano: detect cell phones    │
    └─────┬──────────────────────────────┘
          │
    ┌─────▼──────────────────────────────┐
    │ Event Generation Service           │
    ├────────────────────────────────────┤
    │ Generate events with cooldowns     │
    │ Calculate warning levels           │
    │ Trigger emergency mode             │
    └─────┬──────────────────────────────┘
          │
          ▼
┌──────────────────────────┐
│ TelemetryResponse (JSON) │
├──────────────────────────┤
│ - driver (state metrics) │
│ - vision (ML metrics)    │
│ - vehicle (safety mode)  │
│ - events (alert list)    │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│   React Frontend         │
├──────────────────────────┤
│ - Display metrics        │
│ - Show alerts            │
│ - Emergency overlay      │
│ - Parking assist panel   │
└──────────────────────────┘
```

---

## 🔮 Future Enhancements

### Short Term (v1.1)
- [ ] GPU optimization (ONNX quantization)
- [ ] Multi-frame temporal analysis
- [ ] Improved yawning detection (~70% accuracy)
- [ ] Looking-away refinement using 3D gaze
- [ ] Database migration to PostgreSQL

### Medium Term (v1.2)
- [ ] License plate recognition
- [ ] Seatbelt detection
- [ ] Hand gesture recognition
- [ ] Vehicle telemetry integration (CAN bus)
- [ ] Cloud-based analytics dashboard

### Long Term (v2.0)
- [ ] Real-time 3D pose estimation
- [ ] Federated learning for privacy
- [ ] Edge deployment (Jetson, TPU)
- [ ] Multi-camera support
- [ ] Blockchain for event verification
- [ ] Integration with vehicle APIs (throttle, steering)

---

## 📜 License

This project is part of a Final Year Engineering Program. Use for educational and research purposes.

---

## 👥 Contributing

For modifications or improvements:
1. Create a feature branch
2. Test thoroughly with evaluation scripts
3. Submit pull request with test results
4. Update documentation

---

## 📞 Support & Documentation

- **Frontend Integration**: See `FRONTEND_REFERENCE_FOR_BACKEND.md`
- **Full Technical Details**: See `PROJECT_DOCUMENTATION.md`
- **API Details**: See `API_REFERENCE.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Evaluation Guide**: See `EVALUATION.md`
- **Quick Start**: See `QUICK_START_GUIDE.md`

---

**Last Updated**: 2026-06-24  
**Backend Version**: 1.0.0  
**Status**: Production Ready for Testing
