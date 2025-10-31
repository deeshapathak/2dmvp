# Rhinovate AI - 2D MVP

An AI-powered plastic surgery simulator that shows people what they would look like with realistic cosmetic procedures like rhinoplasty, lip filler, botox, etc.

## Features

- **AI-Powered Analysis**: Advanced facial analysis using MediaPipe face mesh
- **Beauty Rules Engine**: Medical-grade beauty standards and facial harmony principles
- **Realistic Image Processing**: Simulated cosmetic procedures with before/after comparison
- **Modern UI**: Beautiful, medical-style interface with drag-and-drop upload
- **Instant Results**: Get personalized analysis and preview in seconds

## Architecture

### Backend (FastAPI)
- `main.py` - FastAPI application with CORS and file upload handling
- `face_analysis.py` - MediaPipe-based facial landmark detection and measurements
- `beauty_rules.py` - Beauty standards engine for generating recommendations
- `image_processor.py` - Image editing and cosmetic procedure simulation

### Frontend (React)
- Modern React app with styled-components
- Drag-and-drop image upload
- Before/after image comparison
- Medical-style UI with facial harmony scoring
- Share and download functionality

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r ../requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000`

## API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Upload image and get analysis results

## How It Works

1. **Upload**: User uploads a clear front-facing photo
2. **Analysis**: MediaPipe analyzes facial landmarks and calculates measurements
3. **Rules Engine**: Beauty rules engine identifies enhancement opportunities
4. **Image Processing**: AI applies cosmetic changes based on recommendations
5. **Results**: User sees before/after comparison with medical-style recommendations

## Beauty Standards

The system analyzes:
- Facial symmetry (0-100 score)
- Nose-to-IPD ratio
- Chin projection
- Jaw asymmetry
- Facial thirds proportions

## Guardrails

- Maximum change limits per region (25% nose reduction, 30% chin enhancement, etc.)
- Identity preservation (same person conditioning)
- No skin tone or ethnicity changes
- Medical-grade terminology and recommendations

## Disclaimer

This is a demonstration tool for educational purposes. Results are simulated and should not be considered as medical advice. Consult with qualified professionals for actual cosmetic procedures.
