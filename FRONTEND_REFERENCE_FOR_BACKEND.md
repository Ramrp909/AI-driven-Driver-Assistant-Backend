# FRONTEND REFERENCE FOR BACKEND DEVELOPERS

## Overview

This document specifies exactly what the **frontend expects from the backend APIs** without requiring backend developers to read frontend code.

**Target Audience**: FastAPI backend developers  
**Purpose**: API contract, data formats, field definitions  
**Last Updated**: 2026-06-24

---

## API Configuration

### Base URL
The frontend determines the backend URL via `src/services/api.ts`:

```typescript
const isLocalhost = window.location.hostname === "localhost" 
                 || window.location.hostname === "127.0.0.1"

export const API_BASE = isLocalhost
  ? "http://127.0.0.1:8000"     // Development
  : "/api"                       // Production proxy
```

**Frontend Assumptions:**
- Development: Backend runs on `localhost:8000`
- Production: Backend is proxied via `/api` (reverse proxy requirement)
- CORS headers properly configured
- HTTPS enforced in production

---

## Endpoint 1: Face Detection & Driver Monitoring

### `POST /detect-face`

**Purpose**: Analyze driver state, vision pipeline metrics, and vehicle assessment from a single frame.

**Request**
```
Method: POST
Content-Type: multipart/form-data
URL: ${API_BASE}/detect-face

Body:
  file: <JPEG image binary>
  - The driver's face as captured by webcam
  - Typical size: 640x480 to 1280x720 JPEG
  - Must contain driver face, clear enough for ML models
```

**Response**
```json
{
  "driver": {
    "faceDetected": boolean,        // Is face visible in frame?
    "faceCount": number,             // Number of faces (usually 1)
    "isDrowsy": boolean,             // Eyes closed or drooping?
    "isYawning": boolean,            // Mouth open in yawn pattern?
    "isTalking": boolean,            // Mouth moving, speaking detected?
    "phoneDetected": boolean,        // Hand holding phone-like object?
    "warningCount": number,          // Cumulative warnings (0-5)
    "emergencyMode": boolean,        // Critical threshold reached?
    "recommendedAction": string,     // e.g., "Continue Driving", "Take Break", "Pull Over"
    "fatigueLevel": string,          // "Low" | "Medium" | "High"
    "safetyScore": number,           // 0-100 (higher = safer)
    "attentionStatus": string,       // "Focused" | "Distracted" | "Critical"
    "blinkRate": number,             // Blinks per minute (typical: 15-20)
    "gazeStability": number,         // 0-100 (higher = more stable)
    "headDirection": string,         // "Forward" | "Left" | "Right" | "Down" | "Up"
    "lookingAway": boolean,          // Eyes not on road (derived from headDirection)?
    "attentionScore": number         // 0-100 (higher = more focused)
  },
  
  "vision": {
    "trackingState": string,         // "stable" | "lost" | "searching"
    "meshEnabled": boolean,          // Face mesh landmarks detected?
    "meshConfidence": number,        // 0-100 confidence in landmarks
    "pipelineStatus": string,        // "Running" | "Error" | "Initializing"
    "fps": number,                   // Frames processed per second (target: 24-30)
    "latency": number                // Processing time in milliseconds (target: <100ms)
  },
  
  "vehicle": {
    "riskLevel": string,             // "Low" | "Medium" | "High" | "Critical"
    "safetyMode": string,            // "Active" | "Assist" | "Safe" | "Emergency"
    "assistState": string            // "Ready" | "Active" | "Alert" | "Intervening"
  },
  
  "events": [
    {
      "type": string,               // "drowsiness" | "distraction" | "phone" | "collision_warning" | etc.
      "severity": string            // "info" | "warning" | "critical"
    }
  ]
}
```

**Field Definitions**

| Field | Type | Range | Meaning |
|---|---|---|---|
| `faceDetected` | bool | true/false | Is driver face in frame? |
| `isDrowsy` | bool | true/false | Eye closure detected? |
| `isYawning` | bool | true/false | Yawning motion detected? |
| `phoneDetected` | bool | true/false | Phone/hand-object detected? |
| `attentionScore` | number | 0-100 | Focus level (80+ = Focused, 50-80 = Distracted, <50 = Critical) |
| `safetyScore` | number | 0-100 | Overall driver safety (80+ = Safe, 60-80 = Caution, <60 = Unsafe) |
| `gazeStability` | number | 0-100 | Eye movement smoothness (higher = steadier gaze) |
| `blinkRate` | number | 0-60 | Blinks per minute (normal: 15-20) |
| `fatigueLevel` | string | Low/Medium/High | Derived from blink rate, yawning, attention |
| `trackingState` | string | stable/lost/searching | Face mesh tracking quality |
| `meshConfidence` | number | 0-100 | Reliability of 468 face landmarks |
| `fps` | number | 0-60 | Processing speed (client updates at 30 FPS) |
| `latency` | number | 0-500ms | How long backend took to process frame |
| `riskLevel` | string | Low/Medium/High/Critical | Derived from multiple driver metrics |

**Frontend Behavior**

```typescript
// Frontend calls every ~33ms (30 FPS)
const detectFace = async (imageFile: File) => {
  const formData = new FormData()
  formData.append("file", imageFile)
  
  const response = await fetch(`${API_BASE}/detect-face`, {
    method: "POST",
    body: formData
  })
  
  const data = await response.json()  // ← Must match DriverMonitorResponse schema above
  
  // Update global state with response
  updateContext({
    isDrowsy: data.driver.isDrowsy,
    attentionScore: data.driver.attentionScore,
    fps: data.vision.fps,
    latency: data.vision.latency,
    // ... all other fields
  })
  
  // Check for alerts
  if (data.driver.emergencyMode) {
    showEmergencyOverlay()
  }
  
  if (data.vision.trackingState === "lost") {
    addNotification({ type: "warning", message: "Face tracking lost" })
  }
}
```

**Expected Behavior**

- Called **continuously** (~30 FPS) during driving
- Must handle **no face** in frame gracefully (faceDetected=false)
- **Multiple faces**: Return faceCount > 1, but analyze driver (first face)
- Must be **fast** (<100ms per frame for smooth real-time updates)
- **Error response**: Return HTTP 400 with error details if image invalid

---

## Endpoint 2: Driver Face Recognition

### `POST /recognize-driver`

**Purpose**: Identify which saved driver profile matches the face in the image.

**Request**
```
Method: POST
Content-Type: multipart/form-data
URL: ${API_BASE}/recognize-driver

Body:
  file: <JPEG image binary>
  - Same format as /detect-face
  - Should be clearest possible face crop
  - Typical: 640x480 minimum, full face visible
```

**Response**
```json
{
  "matched": boolean,              // Was a known driver recognized?
  "driver": string,                // Driver name if matched (e.g., "Alex Driver")
  "confidence": number             // 0-100 confidence score (threshold: 70+)
}
```

**Frontend Behavior**

```typescript
// Called on startup and every ~8 seconds
const recognizeDriver = async (frame: Blob) => {
  const formData = new FormData()
  formData.append("file", new File([frame], "driver.jpg", { type: "image/jpeg" }))
  
  try {
    const response = await fetch(`${API_BASE}/recognize-driver`, {
      method: "POST",
      body: formData
    })
    
    const data = await response.json()
    
    if (data.matched && data.confidence > 70) {
      // Load driver profile
      setRecognizedDriver({ name: data.driver, confidence: data.confidence })
      setDriverStatus(`${data.driver} Connected`)
      
      // Show welcome animation (5s)
      showWelcomeCard(data.driver)
      
      // Load preferences from context
      const profile = profiles.find(p => p.name === data.driver)
      applyDriverPreferences(profile)
    } else {
      // Unknown driver
      setDriverStatus("Unknown Driver")
      showNewDriverModal()  // Prompt registration
    }
  } catch (error) {
    console.error("Recognition failed:", error)
  }
}
```

**Frontend Assumptions**

1. **Driver Database** exists with saved face encodings
2. **Confidence Score** 70+ is "recognized", <70 is "unknown"
3. **Driver Names** are unique strings (e.g., "Alex Driver", "Sarah Smith")
4. **First Recognition**: New drivers show registration modal
5. **Subsequent Drives**: Recognized drivers auto-load preferences

**Expected Calls**

- **Interval**: Every 8 seconds during startup
- **Then**: Only if new face detected (face disappeared & reappeared)
- **Triggers**: App load, driver change, recognition confidence drops

---

## Telemetry Fields Used

### From `/detect-face` Response, Frontend Uses:

**Driver State Metrics**
```typescript
telemetryData = {
  // From driver object
  isDrowsy: boolean,
  isYawning: boolean,
  isTalking: boolean,
  phoneDetected: boolean,
  attentionScore: number,
  attentionStatus: string,
  blinkRate: number,
  gazeStability: number,
  headDirection: string,
  lookingAway: boolean,
  fatigueLevel: string,
  safetyScore: number,
  warningCount: number,
  emergencyMode: boolean,
  faceDetected: boolean,
  faceCount: number,
  
  // From vision object
  fps: number,
  latency: number,
  trackingConfidence: number,  // Derived from meshConfidence
  trackingState: string,
  meshEnabled: boolean,
  meshConfidence: number,
  pipelineStatus: string,
  
  // From vehicle object
  riskLevel: string,
  safetyMode: string,
  assistState: string
}
```

### Real-time Display in UI
- **TelemetryPanel**: Shows all metrics listed above
- **VehicleStatus**: Uses `isDrowsy`, `lookingAway` to determine drive mode
- **AIAlerts**: Uses `warningCount`, `safetyScore`, `attentionScore`
- **EmergencyOverlay**: Triggers on `emergencyMode === true`
- **ParkingAssist**: Activates on `emergencyMode === true` or collision warning

---

## Warning & Alert System

### Frontend Alert Logic

```
Input: warningCount from backend
Output: Alert level (Yellow → Orange → Red)

warningCount = 0 → No alert
warningCount = 1 → Yellow alert
  ├─ Type: "warning"
  ├─ Sound: warning.mp3
  ├─ Message: "Driver distracted - please focus"
  └─ Duration: 3-5 seconds

warningCount = 2 → Orange alert
  ├─ Type: "warning"
  ├─ Sound: warning.mp3
  ├─ Message: "Safety score low - take a break"
  └─ Duration: 4-6 seconds
  └─ Vehicle: May enter Assist mode

warningCount >= 3 → Red alert + Emergency
  ├─ Type: "danger"
  ├─ Sound: critical.mp3
  ├─ Display: Full-screen red overlay
  ├─ Voice: "CRITICAL ALERT - Taking Control"
  ├─ Vehicle: Emergency braking may engage
  └─ Parking: Assist panel opens
```

### Backend Responsibilities

1. **Calculate warningCount** based on:
   - `isDrowsy = true` → +1
   - `attentionScore < 50` → +1
   - `phoneDetected = true` → +1
   - Any combination of the above → stack warnings

2. **Calculate emergencyMode**:
   - `warningCount >= 3` → `emergencyMode = true`
   - OR `isDrowsy = true AND attentionScore < 30` → `emergencyMode = true`
   - Persist until driver regains focus

3. **Provide recommendedAction** (string):
   - "Continue Driving" (normal)
   - "Stay Focused" (attention low)
   - "Take a Break" (fatigue high)
   - "Pull Over Safely" (critical)

---

## Emergency Mode Fields

Frontend expects these exact fields to determine emergency severity:

```typescript
// From driver object
emergencyMode: boolean         // Primary trigger
warningCount: number          // Count of concurrent issues (1-5+)
isDrowsy: boolean             // Most severe condition
attentionScore: number        // If < 30: critical attention loss
phoneDetected: boolean        // Distraction indicator
fatigueLevel: string          // "High" = added risk
safetyScore: number           // If < 60: unsafe conditions

// From vision object
trackingState: string         // "lost" = safety concern

// From vehicle object
riskLevel: string             // "Critical" = all systems alert
```

### Emergency Overlay Trigger

```typescript
if (showDangerAlert) {
  // Display full-screen red overlay
  // Play critical.mp3 sound (1000ms)
  // Text-to-speech: "CRITICAL ALERT - TAKING CONTROL"
  // Show options:
  // - Emergency Call button
  // - Continue Driving button
  // - Parking Assist button
}
```

---

## Parking Assist Fields

Frontend uses these fields from `/detect-face` to show parking assist panel:

```typescript
if (emergencyMode || testEmergencyMode) {
  // Show parking assist modal
  
  // Display data:
  warningCount           // Color intensity (1=low, 3+=high)
  recommendedAction      // Guidance text
  fatigueLevel           // Additional context
  
  // Options available:
  "Let AI Park" (automatic)
  "I'll Handle It" (manual)
  "Call Emergency" (SOS)
}
```

**Flow**
1. Parking assist modal opens
2. Prompt for lane selection (left/right)
3. After 2.5s: Slow vehicle animation
4. After 5s: Stop animation
5. Show continue or emergency options

---

## Notification System

### Notification Types Expected by Frontend

```typescript
type NotificationType = "danger" | "warning" | "safe" | "info"

// Based on /detect-face response, frontend generates:

if (data.driver.emergencyMode) {
  addNotification({
    type: "danger",
    title: "CRITICAL ALERT",
    message: "Multiple safety issues detected",
    duration: 5000
  })
}

if (data.vision.trackingState === "lost") {
  addNotification({
    type: "warning",
    title: "Tracking Lost",
    message: "Face tracking temporarily lost",
    duration: 3000
  })
}

if (data.driver.phoneDetected) {
  addNotification({
    type: "warning",
    title: "Phone Detected",
    message: "Please keep eyes on road",
    duration: 3000
  })
}

if (data.driver.safetyScore > 80) {
  addNotification({
    type: "safe",
    title: "Safety OK",
    message: "All systems normal",
    duration: 2000
  })
}
```

### Audio Alerts

Frontend plays these from `/public/sounds/`:
- `notification.mp3` - Info alert (green)
- `warning.mp3` - Warning alert (yellow/orange)
- `critical.mp3` - Critical alert (red)
- `parking.mp3` - Parking assist
- `success.mp3` - Positive confirmation

**Backend Constraint**: Frontend doesn't control audio; it's triggered by response conditions.

---

## Driver Data Fields

### Driver Profile (Stored Locally in Frontend)

```typescript
interface DriverProfile {
  id: string                    // Unique identifier
  name: string                  // "Alex Driver", "Sarah Smith"
  avatar?: string               // URL to profile picture
  isActive: boolean
  preferences: {
    acTemperature: number       // 16-28°C
    seatPosition: {
      horizontal: number        // 0-100
      vertical: number          // 0-100
      lumbar: number            // 0-100
    }
    ambientLighting: "off" | "dim" | "medium" | "bright" | "rainbow"
    steeringWheel: {
      tilt: number              // 0-100
      telescope: number         // 0-100
    }
    mirrors: {
      driver: number            // 0-100
      passenger: number         // 0-100
    }
    sound: {
      volume: number            // 0-100
      equalizer: string         // "bass", "balanced", "treble"
    }
  }
}
```

**Backend Note**: Driver profiles are stored in frontend (localStorage, not yet persisted). Backend should return driver names only for `/recognize-driver`.

---

## Vehicle State Integration

### Expected Vehicle Data from Backend

Frontend expects `/detect-face` response to include:

```json
{
  "vehicle": {
    "riskLevel": "Low|Medium|High|Critical",
    "safetyMode": "Active|Assist|Safe|Emergency",
    "assistState": "Ready|Active|Alert|Intervening"
  }
}
```

### Frontend Use

```typescript
// VehicleStatus component displays:
- Drive Mode: Derived from isDrowsy, lookingAway
  - isDrowsy → "Safe Mode"
  - lookingAway → "Assist"
  - Normal → "Comfort"

- Vehicle State: From riskLevel
  - "Low" → "Active" (green)
  - "Medium" → "Caution" (yellow)
  - "High" → "Assist" (orange)
  - "Critical" → "Critical" (red)

// VehicleMetrics component displays:
- Speed (simulated, not from API)
- RPM (simulated, not from API)
- Power consumption (simulated, not from API)
```

---

## API Error Handling

### HTTP Status Codes

| Code | Meaning | Frontend Action |
|---|---|---|
| 200 | Success | Process response |
| 400 | Bad request (invalid image) | Log error, try next frame |
| 401 | Unauthorized | Show auth error (if auth added later) |
| 500 | Server error | Show "Backend unavailable" notification |
| 503 | Service unavailable | Show "System offline" notification |

### Error Response Format (Recommended)

```json
{
  "error": "descriptive error message",
  "details": "optional technical details"
}
```

Frontend logs errors to console for debugging.

---

## CORS Requirements

### Production Deployment

Frontend runs on one domain (e.g., `nexusai.example.com`), backend on another (e.g., `api.example.com`).

**Backend must include these headers:**

```
Access-Control-Allow-Origin: https://nexusai.example.com
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
```

OR for development:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## Performance Requirements

### Expected Performance Metrics

| Metric | Target | Frontend Impact |
|---|---|---|
| **FPS** | 24-30 | Real-time responsiveness |
| **Latency** | <100ms | Smooth 30 FPS updates |
| **Throughput** | 30 req/sec max | Network bandwidth |
| **Uptime** | 99.5% | Service availability |

### Image Specifications

| Property | Recommendation |
|---|---|
| **Format** | JPEG (compressed) |
| **Resolution** | 640x480 to 1280x720 |
| **File Size** | 50-200 KB |
| **Quality** | 70-85 JPEG quality |

**Frontend does NOT compress images** before sending. Backend should handle various resolutions.

---

## Development & Testing

### Mocking the Backend Locally

For frontend development without backend:

```typescript
// In DriverMonitor.tsx, replace actual API call with:
const mockResponse: DriverMonitorResponse = {
  driver: {
    faceDetected: true,
    isDrowsy: false,
    attentionScore: 85,
    // ... other fields
  },
  vision: { fps: 30, latency: 42, /* ... */ },
  vehicle: { riskLevel: "Low", /* ... */ },
  events: []
}
```

### Backend Testing Checklist

- [ ] `/detect-face` accepts JPEG files
- [ ] Response matches schema above (all required fields)
- [ ] Latency < 100ms consistently
- [ ] FPS metric accurate
- [ ] `emergencyMode` calculated correctly
- [ ] `warningCount` increments on multi-factor issues
- [ ] `/recognize-driver` returns known drivers
- [ ] `/recognize-driver` returns matched=false for unknowns
- [ ] CORS headers present
- [ ] Error responses include error message
- [ ] No crashes on invalid images

---

## Common Questions

**Q: What if face detection fails?**  
A: Return `faceDetected: false`. Frontend shows "Scanning Driver..." and continues polling.

**Q: Multiple faces in frame?**  
A: Analyze the primary/largest face, return `faceCount > 1`. Frontend ignores for now.

**Q: How often is `/detect-face` called?**  
A: Every ~33ms (30 FPS). Optimize for this throughput.

**Q: Can I skip some frames?**  
A: No. Frontend expects continuous monitoring for safety-critical application.

**Q: What if backend is slow?**  
A: Frontend will queue requests. Ideally, respond faster than request interval.

**Q: Do I need authentication?**  
A: Not required for MVP. Add later if multi-tenant support needed.

---

## Summary

To integrate with this frontend, backend must:

1. **Implement `/detect-face`**: Real-time driver monitoring (continuous)
2. **Implement `/recognize-driver`**: Driver face recognition (periodic)
3. **Return exact JSON schema**: All fields required for UI to function
4. **Maintain performance**: <100ms latency, 24-30 FPS
5. **Handle errors gracefully**: Return error details, maintain availability
6. **Configure CORS**: Allow frontend domain to access APIs
7. **Calculate warnings**: warningCount, emergencyMode logic
8. **Provide telemetry**: fps, latency, tracking confidence

**Questions?** Refer to `PROJECT_DOCUMENTATION.md` for architectural context or contact frontend team.

---

**Version**: 1.0  
**For Backend Team**: FastAPI developers integrating with this React frontend  
**Created**: 2026-06-24
