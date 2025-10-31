import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import tempfile

class ImageProcessor:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def apply_operations(self, image_path: str, operations: List[Dict[str, Any]]) -> Optional[str]:
        """Apply cosmetic operations to the image"""
        if not operations:
            print(f"[DEBUG] No operations to apply")
            return None
        
        print(f"[DEBUG] Applying {len(operations)} operations: {operations}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"[DEBUG] Failed to load image from {image_path}")
            return None
        
        print(f"[DEBUG] Loaded image: {image.shape}")
        
        # Create a copy for processing
        processed_image = image.copy()
        
        # Apply each operation
        for i, operation in enumerate(operations):
            print(f"[DEBUG] Applying operation {i+1}/{len(operations)}: {operation.get('region')} - {operation.get('type')}")
            original_sum = processed_image.sum()
            processed_image = self._apply_single_operation(processed_image, operation)
            new_sum = processed_image.sum()
            changed = abs(original_sum - new_sum) > 100  # Threshold to detect changes
            print(f"[DEBUG] Operation {i+1} result: Changed={changed}, Original sum={original_sum}, New sum={new_sum}")
        
        # Verify image actually changed
        diff = cv2.absdiff(image, processed_image)
        change_amount = np.sum(diff > 10)  # Count pixels that changed significantly
        print(f"[DEBUG] Total pixels changed: {change_amount} out of {image.size}")
        
        if change_amount < 100:  # Very few pixels changed
            print(f"[WARNING] Very few pixels changed - operations may not be working!")
        
        # Save processed image
        output_path = self._save_processed_image(processed_image, image_path)
        print(f"[DEBUG] Saved processed image to: {output_path}")
        return output_path
    
    def _apply_single_operation(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Apply a single cosmetic operation to the image"""
        region = operation.get("region", "")
        op_type = operation.get("type", "")
        
        print(f"[DEBUG] _apply_single_operation: region={region}, type={op_type}")
        
        result = image
        if region == "nose" and op_type == "shrink_width":
            result = self._shrink_nose_width(image, operation)
        elif region == "nose" and op_type == "refine_tip":
            result = self._refine_nose_tip(image, operation)
        elif region == "nose" and op_type == "refine_bridge":
            result = self._refine_nose_bridge(image, operation)
        elif region == "jaw" and op_type == "balance":
            result = self._balance_jaw(image, operation)
        elif region == "face" and op_type == "symmetry":
            result = self._improve_symmetry(image, operation)
        elif region == "chin" and op_type == "enhance":
            result = self._enhance_chin(image, operation)
        elif region == "face" and "third" in op_type:
            result = self._adjust_facial_third(image, operation)
        else:
            print(f"[WARNING] Unknown operation: region={region}, type={op_type}")
        
        # Verify result changed
        if np.array_equal(result, image):
            print(f"[WARNING] Operation {region}-{op_type} returned unchanged image!")
        else:
            diff = np.sum(np.abs(result.astype(float) - image.astype(float)))
            print(f"[DEBUG] Operation {region}-{op_type} changed image by {diff:.0f} pixels")
        
        return result
    
    def _shrink_nose_width(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Comprehensive nose width reduction - main rhinoplasty operation"""
        factor = operation.get("factor", 0.9)
        
        print(f"[DEBUG] _shrink_nose_width: factor={factor}")
        
        # Ensure factor is reasonable - allow up to 30% reduction
        if factor >= 1.0 or factor < 0.70:
            print(f"[WARNING] Nose shrink factor {factor} out of range, skipping")
            return image
        
        height, width = image.shape[:2]
        nose_center_x = width // 2
        nose_center_y = int(height * 0.35)
        nose_width = int(width * 0.16)  # Wider capture area for better results
        nose_height = int(height * 0.20)  # Taller to include full nose structure
        
        # More pronounced taper for elegant nose shape
        # Bridge (top) is wider, tip (bottom) is narrower naturally
        bridge_width = nose_width
        mid_width = int(nose_width * 0.90)  # Middle section
        tip_width = int(nose_width * 0.80)  # Tip is narrower
        
        # Create more sophisticated warping points - 4 point perspective
        src_points = np.float32([
            [nose_center_x - bridge_width//2, nose_center_y - nose_height//2],  # Top left (bridge)
            [nose_center_x + bridge_width//2, nose_center_y - nose_height//2],  # Top right (bridge)
            [nose_center_x + tip_width//2, nose_center_y + nose_height//2],  # Bottom right (tip)
            [nose_center_x - tip_width//2, nose_center_y + nose_height//2]  # Bottom left (tip)
        ])
        
        # Apply reduction factor more aggressively for impressive results
        reduction_multiplier = 1.0 - (1.0 - factor) * 1.2  # 20% more reduction for impact
        new_bridge_width = int(bridge_width * reduction_multiplier)
        new_mid_width = int(mid_width * reduction_multiplier)
        new_tip_width = int(tip_width * reduction_multiplier)
        
        width_diff = bridge_width - new_bridge_width
        print(f"[DEBUG] Nose width change: {width_diff} pixels (bridge: {bridge_width} -> {new_bridge_width})")
        if width_diff < 2:
            print(f"[WARNING] Width diff too small ({width_diff}), skipping")
            return image
        
        # Create destination points - significantly narrower for impressive change
        dst_points = np.float32([
            [nose_center_x - new_bridge_width//2, nose_center_y - nose_height//2],
            [nose_center_x + new_bridge_width//2, nose_center_y - nose_height//2],
            [nose_center_x + new_tip_width//2, nose_center_y + nose_height//2],
            [nose_center_x - new_tip_width//2, nose_center_y + nose_height//2]
        ])
        
        # Create refined mask - more precise nose shape
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        avg_width = (new_bridge_width + new_tip_width) // 2
        
        # Elliptical mask that follows nose shape
        cv2.ellipse(mask, 
                   (nose_center_x, nose_center_y),
                   (avg_width//2 + 10, nose_height//2 + 12),
                   0, 0, 360, 255, -1)
        
        # Smooth but not too blurry - preserve sharpness
        mask = cv2.GaussianBlur(mask, (19, 19), 0)
        mask = mask.astype(np.float32) / 255.0
        mask = np.stack([mask] * 3, axis=2)
        
        # Apply transform with high-quality interpolation
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height), 
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        # Blend for natural but noticeable result
        result = image * (1 - mask) + warped * mask
        return result.astype(np.uint8)
    
    def _refine_nose_tip(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Refine nose tip - make it more defined and elegant"""
        factor = operation.get("factor", 0.85)
        
        if factor >= 1.0 or factor < 0.80:
            return image
        
        height, width = image.shape[:2]
        nose_center_x = width // 2
        nose_tip_y = int(height * 0.45)  # Tip is lower on face
        tip_width = int(width * 0.08)   # Narrow tip area
        tip_height = int(height * 0.10)
        
        # Create source points for tip region
        src_points = np.float32([
            [nose_center_x - tip_width//2, nose_tip_y - tip_height//2],
            [nose_center_x + tip_width//2, nose_tip_y - tip_height//2],
            [nose_center_x + tip_width//2, nose_tip_y + tip_height//2],
            [nose_center_x - tip_width//2, nose_tip_y + tip_height//2]
        ])
        
        # Narrow the tip more
        new_tip_width = int(tip_width * factor)
        if new_tip_width >= tip_width:
            return image
        
        dst_points = np.float32([
            [nose_center_x - new_tip_width//2, nose_tip_y - tip_height//2],
            [nose_center_x + new_tip_width//2, nose_tip_y - tip_height//2],
            [nose_center_x + new_tip_width//2, nose_tip_y + tip_height//2],
            [nose_center_x - new_tip_width//2, nose_tip_y + tip_height//2]
        ])
        
        # Precise tip mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.ellipse(mask, 
                   (nose_center_x, nose_tip_y),
                   (new_tip_width//2 + 5, tip_height//2 + 5),
                   0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (13, 13), 0)
        mask = mask.astype(np.float32) / 255.0
        mask = np.stack([mask] * 3, axis=2)
        
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        result = image * (1 - mask) + warped * mask
        return result.astype(np.uint8)
    
    def _refine_nose_bridge(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Refine nose bridge - make it narrower and more elegant"""
        factor = operation.get("factor", 0.90)
        
        if factor >= 1.0 or factor < 0.85:
            return image
        
        height, width = image.shape[:2]
        nose_center_x = width // 2
        bridge_y = int(height * 0.28)  # Bridge is higher
        bridge_width = int(width * 0.10)  # Narrow bridge region
        bridge_height = int(height * 0.12)
        
        # Create source points for bridge region
        src_points = np.float32([
            [nose_center_x - bridge_width//2, bridge_y - bridge_height//2],
            [nose_center_x + bridge_width//2, bridge_y - bridge_height//2],
            [nose_center_x + bridge_width//2, bridge_y + bridge_height//2],
            [nose_center_x - bridge_width//2, bridge_y + bridge_height//2]
        ])
        
        # Narrow the bridge
        new_bridge_width = int(bridge_width * factor)
        if new_bridge_width >= bridge_width:
            return image
        
        dst_points = np.float32([
            [nose_center_x - new_bridge_width//2, bridge_y - bridge_height//2],
            [nose_center_x + new_bridge_width//2, bridge_y - bridge_height//2],
            [nose_center_x + new_bridge_width//2, bridge_y + bridge_height//2],
            [nose_center_x - new_bridge_width//2, bridge_y + bridge_height//2]
        ])
        
        # Precise bridge mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.ellipse(mask,
                   (nose_center_x, bridge_y),
                   (new_bridge_width//2 + 4, bridge_height//2 + 4),
                   0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (11, 11), 0)
        mask = mask.astype(np.float32) / 255.0
        mask = np.stack([mask] * 3, axis=2)
        
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        result = image * (1 - mask) + warped * mask
        return result.astype(np.uint8)
    
    def _balance_jaw(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Balance jaw asymmetry using localized warping"""
        mm_correction = operation.get("mm", 0)
        
        if mm_correction == 0 or mm_correction > 2.0:
            return image
        
        height, width = image.shape[:2]
        
        # Convert mm to pixels (rough estimate: 1mm ≈ 1% of face width)
        face_width_estimate = width * 0.6
        pixel_correction = int(mm_correction * face_width_estimate / 100)
        
        if abs(pixel_correction) < 2:
            return image
        
        # Define jaw region (lower sides of face)
        jaw_y = int(height * 0.7)
        jaw_height = int(height * 0.2)
        jaw_center_x = width // 2
        jaw_side_width = int(width * 0.2)
        
        # Create a subtle warp to balance asymmetry
        # Apply correction to the side that's more prominent
        if pixel_correction > 0:
            # Right side needs correction - shift toward center
            jaw_left = jaw_center_x
            jaw_right = min(jaw_center_x + jaw_side_width, width)
        else:
            # Left side needs correction - shift toward center  
            jaw_left = max(0, jaw_center_x - jaw_side_width)
            jaw_right = jaw_center_x
        
        # Create transformation points
        src_points = np.float32([
            [jaw_left, jaw_y],
            [jaw_right, jaw_y],
            [jaw_right, jaw_y + jaw_height],
            [jaw_left, jaw_y + jaw_height]
        ])
        
        # Shift toward center - make more visible
        shift = abs(pixel_correction) * 0.7  # Increased from 0.5 to 0.7 for more visibility
        if pixel_correction > 0:
            dst_points = np.float32([
                [jaw_left + shift, jaw_y],
                [jaw_right - shift, jaw_y],
                [jaw_right - shift, jaw_y + jaw_height],
                [jaw_left + shift, jaw_y + jaw_height]
            ])
        else:
            dst_points = np.float32([
                [jaw_left - shift, jaw_y],
                [jaw_right + shift, jaw_y],
                [jaw_right + shift, jaw_y + jaw_height],
                [jaw_left - shift, jaw_y + jaw_height]
            ])
        
        # Create mask for jaw region
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, [src_points.astype(int)], 255)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
        
        # Apply perspective transform
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        # Blend only the jaw region
        result = image * (1 - mask_3d) + warped * mask_3d
        return result.astype(np.uint8)
    
    def _improve_symmetry(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Improve facial symmetry using localized warping"""
        amount = operation.get("amount", 0)
        
        if amount == 0 or amount > 0.15:
            return image
        
        height, width = image.shape[:2]
        
        # Only modify the central face region to avoid edge blurring
        face_center_x = width // 2
        face_center_y = height // 2
        face_region_width = int(width * 0.6)
        face_region_height = int(height * 0.7)
        
        # Create a mask for the face region
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.ellipse(mask, 
                   (face_center_x, face_center_y),
                   (face_region_width//2, face_region_height//2),
                   0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (25, 25), 0)
        
        # Apply very subtle symmetry correction using local affine transform
        # Split only the inner face region
        inner_left = int(face_center_x - face_region_width * 0.25)
        inner_right = int(face_center_x + face_region_width * 0.25)
        
        if inner_left > 0 and inner_right < width:
            # Create mirrored version of center region
            center_region = image[:, inner_left:inner_right].copy()
            mirrored = cv2.flip(center_region, 1)
            
            # More visible blend for noticeable symmetry improvement
            blend_strength = min(amount * 0.4, 0.2)  # Increased from 0.2/0.1 to 0.4/0.2
            blended = cv2.addWeighted(center_region, 1 - blend_strength, 
                                     mirrored, blend_strength, 0)
            
            # Apply only to center region with mask
            result = image.copy()
            center_mask = mask[:, inner_left:inner_right]
            center_mask_3d = np.stack([center_mask] * 3, axis=2).astype(np.float32) / 255.0
            
            result[:, inner_left:inner_right] = (
                result[:, inner_left:inner_right] * (1 - center_mask_3d) + 
                blended * center_mask_3d
            ).astype(np.uint8)
            
            return result
        
        return image
    
    def _enhance_chin(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Enhance chin projection using localized forward warping"""
        amount = operation.get("amount", 0)
        
        if amount == 0 or amount > 0.2:
            return image
        
        height, width = image.shape[:2]
        
        # Define chin region (lower portion of face)
        chin_start_y = int(height * 0.75)
        chin_height = int(height * 0.15)
        chin_center_x = width // 2
        chin_width = int(width * 0.4)
        
        # Create transformation to push chin forward slightly
        # Use local affine transformation for better quality
        src_points = np.float32([
            [chin_center_x - chin_width//2, chin_start_y],
            [chin_center_x + chin_width//2, chin_start_y],
            [chin_center_x + chin_width//2, chin_start_y + chin_height],
            [chin_center_x - chin_width//2, chin_start_y + chin_height]
        ])
        
        # Push forward by stretching downward - make more visible
        stretch_y = int(chin_height * amount * 0.5)  # Increased from 0.3 to 0.5 for more visibility
        if stretch_y < 1:
            return image
            
        dst_points = np.float32([
            [chin_center_x - chin_width//2, chin_start_y],
            [chin_center_x + chin_width//2, chin_start_y],
            [chin_center_x + chin_width//2, chin_start_y + chin_height + stretch_y],
            [chin_center_x - chin_width//2, chin_start_y + chin_height + stretch_y]
        ])
        
        # Create mask for chin region
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, [dst_points.astype(int)], 255)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
        
        # Apply perspective transform
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        # Blend only the chin region
        result = image * (1 - mask_3d) + warped * mask_3d
        return result.astype(np.uint8)
    
    def _adjust_facial_third(self, image: np.ndarray, operation: Dict[str, Any]) -> np.ndarray:
        """Adjust facial third proportions using localized vertical warping"""
        op_type = operation.get("type", "")
        current = operation.get("current", 0)
        target = operation.get("target", 0)
        
        # Calculate how much to adjust
        deviation = target - current
        if abs(deviation) < 0.01:  # Less than 1% change, skip
            return image
        
        height, width = image.shape[:2]
        face_height = height  # Approximate
        
        # Determine which third to adjust
        if "upper" in op_type:
            # Upper third: Hairline to brow
            # Botox can lift brows, but we simulate subtle vertical adjustment
            return self._adjust_upper_third(image, deviation, face_height)
        elif "middle" in op_type:
            # Middle third: Brow to base of nose
            # Very limited adjustment (mostly surgical)
            return self._adjust_middle_third(image, deviation, face_height)
        elif "lower" in op_type:
            # Lower third: Base of nose to chin
            # Can use fillers for chin augmentation (already handled by chin enhancement)
            # But can also adjust lip-to-chin distance
            return self._adjust_lower_third(image, deviation, face_height)
        
        return image
    
    def _adjust_upper_third(self, image: np.ndarray, deviation: float, face_height: int) -> np.ndarray:
        """
        Adjust upper third - VERY LIMITED with Botox
        Botox can only lift brows 1-3mm (minimal effect)
        For significant changes, requires surgical brow lift
        """
        height, width = image.shape[:2]
        upper_start = 0
        upper_end = int(height * 0.33)
        
        # Botox can only achieve 1-3mm brow lift = ~1-2% of face height
        max_botox_effect = 0.02  # Maximum 2% change achievable with Botox
        
        if abs(deviation) > max_botox_effect:
            # Beyond Botox capability - would require surgery
            # Return original or very minimal effect
            return image
        
        if abs(deviation) < 0.01:  # Too subtle even for Botox
            return image
        
        # Very subtle compression to simulate minimal brow lift
        # Botox brow lift: relaxes muscles, lifts brows 1-3mm
        brow_lift_y = int(height * 0.25)  # Approximate brow position
        lift_amount = int(abs(deviation) * height * 0.3)  # Conservative, realistic amount
        
        if lift_amount < 1:
            return image
        
        # Create subtle upward shift of brow region only
        mask = np.zeros((height, width), dtype=np.uint8)
        brow_region_height = int(height * 0.08)  # Small brow region
        cv2.rectangle(mask, (0, brow_lift_y - brow_region_height//2), 
                     (width, brow_lift_y + brow_region_height//2), 255, -1)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
        
        # Subtle upward translation
        M = np.float32([[1, 0, 0], [0, 1, -lift_amount]])
        warped = cv2.warpAffine(image, M, (width, height),
                               flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REPLICATE)
        
        # Blend very subtly
        result = image * (1 - mask_3d * 0.4) + warped * mask_3d * 0.4
        return result.astype(np.uint8)
    
    def _adjust_middle_third(self, image: np.ndarray, deviation: float, face_height: int) -> np.ndarray:
        """
        Adjust middle third - BEST CANDIDATE for non-surgical enhancement
        Cheek/midface fillers are very effective for this region
        NOT achievable with Botox alone - requires fillers
        """
        height, width = image.shape[:2]
        middle_start = int(height * 0.33)  # Brow level
        middle_end = int(height * 0.66)    # Nose base
        
        if abs(deviation) < 0.02:
            return image
        
        # Middle third enhancement = cheek augmentation with fillers
        # This adds volume/forward projection to midface
        center_x = width // 2
        cheek_width = int(width * 0.35)  # Cheek region width
        cheek_center_y = (middle_start + middle_end) // 2
        
        if deviation > 0:  # Increase middle third (most common - add volume)
            # Simulate cheek filler augmentation
            # Creates forward projection and adds volume to midface
            src_points = np.float32([
                [center_x - cheek_width//2, middle_start],
                [center_x + cheek_width//2, middle_start],
                [center_x + cheek_width//2, middle_end],
                [center_x - cheek_width//2, middle_end]
            ])
            
            # Forward projection simulates filler volume
            projection = int(abs(deviation) * width * 0.15)  # Realistic filler effect
            
            dst_points = np.float32([
                [center_x - cheek_width//2 - projection//3, middle_start],
                [center_x + cheek_width//2 + projection//3, middle_start],
                [center_x + cheek_width//2 + projection//4, middle_end],
                [center_x - cheek_width//2 - projection//4, middle_end]
            ])
            
            # Create mask for cheek/midface region
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.ellipse(mask, 
                       (center_x, cheek_center_y),
                       (cheek_width//2 + 10, (middle_end - middle_start)//2 + 5),
                       0, 0, 360, 255, -1)
            mask = cv2.GaussianBlur(mask, (23, 23), 0)
            mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
            
            # Apply transformation
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            warped = cv2.warpPerspective(image, matrix, (width, height),
                                        flags=cv2.INTER_LINEAR,
                                        borderMode=cv2.BORDER_REPLICATE)
            
            result = image * (1 - mask_3d) + warped * mask_3d
            return result.astype(np.uint8)
        
        return image  # Reducing middle third typically requires surgery
    
    def _adjust_lower_third(self, image: np.ndarray, deviation: float, face_height: int) -> np.ndarray:
        """Adjust lower third (nose base to chin) - can use fillers"""
        height, width = image.shape[:2]
        
        lower_start = int(height * 0.66)
        lower_end = height
        lower_height = lower_end - lower_start
        
        if abs(deviation) < 0.02:
            return image
        
        # More significant adjustment possible (fillers can add volume)
        stretch_factor = 1.0 + (deviation * 0.6)  # 60% of deviation
        new_height = int(lower_height * stretch_factor)
        
        if abs(new_height - lower_height) < 3:
            return image
        
        center_x = width // 2
        
        src_points = np.float32([
            [0, lower_start],
            [width, lower_start],
            [width, lower_end],
            [0, lower_end]
        ])
        
        new_end = min(lower_start + new_height, height)
        
        dst_points = np.float32([
            [0, lower_start],
            [width, lower_start],
            [width, new_end],
            [0, new_end]
        ])
        
        # Create mask for lower face
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, [dst_points.astype(int)], 255)
        mask = cv2.GaussianBlur(mask, (23, 23), 0)
        mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
        
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(image, matrix, (width, height),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)
        
        result = image * (1 - mask_3d) + warped * mask_3d
        return result.astype(np.uint8)
    
    def _save_processed_image(self, image: np.ndarray, original_path: str) -> str:
        """Save the processed image and return the path"""
        original_name = Path(original_path).stem
        output_filename = f"after_{original_name}.jpg"
        output_path = self.upload_dir / output_filename
        
        # Save with high quality
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return str(output_path)
    
    def create_face_mask(self, image: np.ndarray) -> np.ndarray:
        """Create a face mask for more precise editing"""
        # This would use face parsing in a production system
        # For now, return a simple oval mask
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Create oval mask
        center = (width // 2, height // 2)
        axes = (width // 3, height // 2)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        
        return mask
