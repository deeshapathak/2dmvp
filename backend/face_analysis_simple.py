import cv2
import numpy as np
from typing import Tuple, Dict, Optional
import math

class FaceAnalyzer:
    def __init__(self):
        # Initialize OpenCV face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    def analyze_face(self, image_path: str) -> Tuple[Optional[np.ndarray], Dict]:
        """Analyze face and return landmarks and measurements"""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None, {}
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None, {}
        
        # Get the first face
        (x, y, w, h) = faces[0]
        
        # Create a simple face region
        face_region = gray[y:y+h, x:x+w]
        
        # Detect eyes within the face
        eyes = self.eye_cascade.detectMultiScale(face_region)
        
        # Create simple landmarks based on face detection
        landmarks = self._create_simple_landmarks(x, y, w, h, eyes)
        
        # Calculate measurements
        measurements = self._calculate_measurements(landmarks, image.shape)
        
        return landmarks, measurements
    
    def _create_simple_landmarks(self, x, y, w, h, eyes):
        """Create simple facial landmarks based on face detection"""
        landmarks = []
        
        # Face center
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Basic facial points
        landmarks.append([center_x, center_y, 0])  # Face center
        landmarks.append([center_x, y + h * 0.3, 0])  # Forehead
        landmarks.append([center_x, y + h * 0.7, 0])  # Chin
        landmarks.append([x + w * 0.3, center_y, 0])  # Left cheek
        landmarks.append([x + w * 0.7, center_y, 0])  # Right cheek
        
        # Eye positions (simplified)
        if len(eyes) >= 2:
            # Sort eyes by x position
            eyes = sorted(eyes, key=lambda eye: eye[0])
            left_eye = eyes[0]
            right_eye = eyes[1]
            
            # Left eye center
            left_eye_x = x + left_eye[0] + left_eye[2] // 2
            left_eye_y = y + left_eye[1] + left_eye[3] // 2
            landmarks.append([left_eye_x, left_eye_y, 0])
            
            # Right eye center
            right_eye_x = x + right_eye[0] + right_eye[2] // 2
            right_eye_y = y + right_eye[1] + right_eye[3] // 2
            landmarks.append([right_eye_x, right_eye_y, 0])
        else:
            # Default eye positions
            landmarks.append([x + w * 0.35, y + h * 0.4, 0])  # Left eye
            landmarks.append([x + w * 0.65, y + h * 0.4, 0])  # Right eye
        
        # Nose (center of face)
        landmarks.append([center_x, y + h * 0.5, 0])
        
        # Mouth (lower third)
        landmarks.append([center_x, y + h * 0.8, 0])
        
        return np.array(landmarks)
    
    def _calculate_measurements(self, landmarks: np.ndarray, image_shape: Tuple[int, int, int]) -> Dict:
        """Calculate facial measurements and ratios"""
        height, width = image_shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        landmarks_px = landmarks.copy()
        
        # Calculate symmetry score (simplified)
        symmetry_score = self._calculate_symmetry(landmarks_px)
        
        # Calculate basic ratios
        if len(landmarks_px) >= 7:  # Ensure we have enough points
            # Eye distance
            left_eye = landmarks_px[5] if len(landmarks_px) > 5 else landmarks_px[0]
            right_eye = landmarks_px[6] if len(landmarks_px) > 6 else landmarks_px[1]
            eye_distance = np.linalg.norm(right_eye - left_eye)
            
            # Face width (approximate)
            face_width = width * 0.6  # Rough estimate
            
            # Nose width (simplified)
            nose_width = eye_distance * 0.8
            
            # Nose to IPD ratio
            nose_to_ipd_ratio = nose_width / eye_distance if eye_distance > 0 else 1.0
            
            # Chin projection (simplified)
            chin_projection = abs(landmarks_px[2][0] - landmarks_px[0][0])  # Chin vs center
            
            # Jaw asymmetry (simplified)
            jaw_asymmetry = abs(landmarks_px[3][0] - landmarks_px[4][0])  # Left vs right cheek
        else:
            eye_distance = width * 0.2
            nose_to_ipd_ratio = 0.8
            chin_projection = width * 0.1
            jaw_asymmetry = width * 0.05
        
        return {
            "symmetry_score": symmetry_score,
            "nose_to_ipd_ratio": nose_to_ipd_ratio,
            "chin_projection": chin_projection,
            "jaw_asymmetry": jaw_asymmetry,
            "eye_distance": eye_distance,
            "face_width": face_width
        }
    
    def _calculate_symmetry(self, landmarks: np.ndarray) -> float:
        """Calculate facial symmetry score (0-1) - simplified version"""
        if len(landmarks) < 7:
            return 0.8  # Default good symmetry
        
        # Get face center
        face_center = landmarks[0]
        
        # Calculate left and right side distances from center
        left_points = landmarks[3:5]  # Left cheek and left eye
        right_points = landmarks[4:6]  # Right cheek and right eye
        
        if len(left_points) == 0 or len(right_points) == 0:
            return 0.8
        
        # Calculate average distance from center
        left_distances = [np.linalg.norm(point - face_center) for point in left_points]
        right_distances = [np.linalg.norm(point - face_center) for point in right_points]
        
        # Calculate symmetry based on distance differences
        if len(left_distances) > 0 and len(right_distances) > 0:
            avg_left = np.mean(left_distances)
            avg_right = np.mean(right_distances)
            symmetry_diff = abs(avg_left - avg_right) / max(avg_left, avg_right)
            symmetry_score = max(0, 1 - symmetry_diff)
        else:
            symmetry_score = 0.8
        
        return min(1.0, symmetry_score)
