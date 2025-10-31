import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Dict, Optional
import math

class FaceAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def analyze_face(self, image_path: str) -> Tuple[Optional[np.ndarray], Dict]:
        """Analyze face and return landmarks and measurements"""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None, {}
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            return None, {}
        
        # Get face landmarks
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark])
        
        # Calculate measurements
        measurements = self._calculate_measurements(landmarks, image.shape)
        
        return landmarks, measurements
    
    def _calculate_measurements(self, landmarks: np.ndarray, image_shape: Tuple[int, int, int]) -> Dict:
        """Calculate facial measurements and ratios"""
        height, width = image_shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        landmarks_px = landmarks.copy()
        landmarks_px[:, 0] *= width
        landmarks_px[:, 1] *= height
        
        # Key landmark indices (MediaPipe face mesh)
        # These are approximate indices - you may need to adjust based on actual face mesh
        LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        NOSE_TIP = 1
        NOSE_BRIDGE = 6
        CHIN = 152
        LEFT_MOUTH = 61
        RIGHT_MOUTH = 291
        
        # Calculate symmetry score
        symmetry_score = self._calculate_symmetry(landmarks_px)
        
        # Calculate facial thirds
        facial_thirds = self._calculate_facial_thirds(landmarks_px)
        
        # Calculate nose to IPD ratio
        nose_width = self._get_nose_width(landmarks_px)
        ipd = self._get_interpupillary_distance(landmarks_px)
        nose_to_ipd_ratio = nose_width / ipd if ipd > 0 else 1.0
        
        # Calculate chin projection
        chin_projection = self._calculate_chin_projection(landmarks_px)
        
        # Calculate jaw asymmetry
        jaw_asymmetry = self._calculate_jaw_asymmetry(landmarks_px)
        
        return {
            "symmetry_score": symmetry_score,
            "facial_thirds": facial_thirds,
            "nose_to_ipd_ratio": nose_to_ipd_ratio,
            "chin_projection": chin_projection,
            "jaw_asymmetry": jaw_asymmetry,
            "nose_width": nose_width,
            "ipd": ipd
        }
    
    def _calculate_symmetry(self, landmarks: np.ndarray) -> float:
        """Calculate facial symmetry score (0-1)"""
        # Get key facial points
        face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        # Calculate left and right side distances
        left_points = landmarks[face_oval[:len(face_oval)//2]]
        right_points = landmarks[face_oval[len(face_oval)//2:]]
        
        # Mirror right points
        right_points_mirrored = right_points.copy()
        right_points_mirrored[:, 0] = -right_points_mirrored[:, 0]  # Flip x-coordinate
        
        # Calculate average distance between corresponding points
        distances = np.linalg.norm(left_points - right_points_mirrored, axis=1)
        avg_distance = np.mean(distances)
        
        # Normalize to 0-1 scale (higher is more symmetric)
        max_expected_distance = 50  # Adjust based on your image scale
        symmetry_score = max(0, 1 - (avg_distance / max_expected_distance))
        
        return min(1.0, symmetry_score)
    
    def _calculate_facial_thirds(self, landmarks: np.ndarray) -> Dict:
        """Calculate facial thirds proportions"""
        # Key points for facial thirds
        hairline = landmarks[10]  # Top of forehead
        glabella = landmarks[6]   # Between eyebrows
        subnasale = landmarks[2]  # Base of nose
        menton = landmarks[152]   # Chin
        
        upper_third = np.linalg.norm(glabella - hairline)
        middle_third = np.linalg.norm(subnasale - glabella)
        lower_third = np.linalg.norm(menton - subnasale)
        
        total_height = upper_third + middle_third + lower_third
        
        return {
            "upper": upper_third / total_height if total_height > 0 else 0.33,
            "middle": middle_third / total_height if total_height > 0 else 0.33,
            "lower": lower_third / total_height if total_height > 0 else 0.33
        }
    
    def _get_nose_width(self, landmarks: np.ndarray) -> float:
        """Calculate nose width"""
        # Nose width points
        left_nostril = landmarks[174]
        right_nostril = landmarks[398]
        return np.linalg.norm(right_nostril - left_nostril)
    
    def _get_interpupillary_distance(self, landmarks: np.ndarray) -> float:
        """Calculate interpupillary distance"""
        # Eye center points (approximate)
        left_eye_center = np.mean(landmarks[[33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]], axis=0)
        right_eye_center = np.mean(landmarks[[362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]], axis=0)
        return np.linalg.norm(right_eye_center - left_eye_center)
    
    def _calculate_chin_projection(self, landmarks: np.ndarray) -> float:
        """Calculate chin projection relative to face"""
        chin = landmarks[152]
        nose_tip = landmarks[1]
        # Simple projection calculation
        return abs(chin[0] - nose_tip[0])
    
    def _calculate_jaw_asymmetry(self, landmarks: np.ndarray) -> float:
        """Calculate jaw asymmetry in mm"""
        # Jaw points
        left_jaw = landmarks[172]
        right_jaw = landmarks[397]
        chin = landmarks[152]
        
        # Calculate asymmetry
        left_distance = np.linalg.norm(left_jaw - chin)
        right_distance = np.linalg.norm(right_jaw - chin)
        
        return abs(left_distance - right_distance)
