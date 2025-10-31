from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path

from face_analysis import FaceAnalyzer
from beauty_rules import BeautyRulesEngine
from image_processor import ImageProcessor

app = FastAPI(title="Rhinovate AI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
face_analyzer = FaceAnalyzer()
beauty_engine = BeautyRulesEngine()
image_processor = ImageProcessor()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class AnalyzeResponse(BaseModel):
    symmetry_score: float
    facial_harmony_score: int
    measurements: dict
    recommendations: List[str]
    operations: List[dict]
    before_url: Optional[str] = None
    after_url: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="Rhinovate AI is running")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_face(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Analyze face and get measurements
        landmarks, measurements = face_analyzer.analyze_face(str(file_path))
        
        if landmarks is None:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # 2. Apply beauty rules to get recommendations
        operations = beauty_engine.plan_changes(measurements)
        recommendations = beauty_engine.get_readable_recommendations(operations)
        
        # 3. Calculate facial harmony score (0-100) - comprehensive scoring
        facial_harmony_score = beauty_engine.calculate_harmony_score(measurements, operations)
        
        # 4. Generate edited image
        after_path = None
        if operations:
            after_path = image_processor.apply_operations(str(file_path), operations)
            if after_path:
                after_url = f"/uploads/{Path(after_path).name}"
            else:
                after_url = None
        else:
            after_url = None
        
        # 5. Generate before URL
        before_url = f"/uploads/{file_path.name}"
        
        # Clean up temp file
        if after_path and after_path != str(file_path):
            os.rename(str(file_path), str(UPLOAD_DIR / f"before_{file.filename}"))
            before_url = f"/uploads/before_{file.filename}"
        
        return AnalyzeResponse(
            symmetry_score=measurements["symmetry_score"],
            facial_harmony_score=facial_harmony_score,
            measurements=measurements,
            recommendations=recommendations,
            operations=operations,
            before_url=before_url,
            after_url=after_url
        )
        
    except Exception as e:
        # Clean up on error
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
