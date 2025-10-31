from typing import List, Dict, Any
import json

class BeautyRulesEngine:
    def __init__(self):
        # Beauty rules configuration
        self.BEAUTY_RULES = {
            "global": {
                "target_symmetry": 0.9,
                "max_symmetry_delta": 0.15
            },
            "nose": {
                "max_reduction": 0.30,   # 30% - more impressive but still realistic
                "ideal_nose_to_ipd": 0.75,
                "tip_refinement": 0.15,  # Additional tip narrowing
                "bridge_refinement": 0.10  # Bridge narrowing
            },
            "chin": {
                "max_projection_increase": 0.3,
                "max_projection_decrease": 0.2
            },
            "jaw": {
                "max_narrowing": 0.2,
                "max_asymmetry_correction": 2.0  # mm
            },
            "lips": {
                "max_augmentation": 0.35
            },
            "facial_thirds": {
                "ideal_upper": 0.33,
                "ideal_middle": 0.33,
                "ideal_lower": 0.34,
                "tolerance": 0.05
            }
        }
    
    def plan_changes(self, measurements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan cosmetic changes based on facial measurements"""
        operations = []
        
        # 1) Symmetry correction
        current_symmetry = measurements.get("symmetry_score", 1.0)
        target_symmetry = self.BEAUTY_RULES["global"]["target_symmetry"]
        
        if current_symmetry < target_symmetry:
            delta = min(target_symmetry - current_symmetry, 
                       self.BEAUTY_RULES["global"]["max_symmetry_delta"])
            operations.append({
                "region": "face", 
                "type": "symmetry", 
                "amount": delta,
                "priority": 1
            })
        
        # 2) Nose width correction - comprehensive rhinoplasty
        nose_ratio = measurements.get("nose_to_ipd_ratio", 1.0)
        ideal_nose_ratio = self.BEAUTY_RULES["nose"]["ideal_nose_to_ipd"]
        
        if nose_ratio > ideal_nose_ratio:
            # Nose is too wide - significant reduction needed
            excess = nose_ratio / ideal_nose_ratio - 1.0
            shrink_factor = min(excess, self.BEAUTY_RULES["nose"]["max_reduction"])
            
            # Main width reduction
            operations.append({
                "region": "nose", 
                "type": "shrink_width", 
                "factor": 1 - shrink_factor,
                "priority": 2
            })
            
            # Additional tip refinement for more polished look
            if shrink_factor > 0.15:  # If significant reduction needed
                operations.append({
                    "region": "nose",
                    "type": "refine_tip",
                    "factor": 1 - self.BEAUTY_RULES["nose"]["tip_refinement"],
                    "priority": 2
                })
            
            # Bridge refinement for narrower, more elegant bridge
            if shrink_factor > 0.12:
                operations.append({
                    "region": "nose",
                    "type": "refine_bridge",
                    "factor": 1 - self.BEAUTY_RULES["nose"]["bridge_refinement"],
                    "priority": 2
                })
        elif nose_ratio < ideal_nose_ratio * 0.85:
            # Nose is significantly narrower than ideal - still apply subtle refinement for elegance
            # Even narrow noses can benefit from tip/bridge refinement
            operations.append({
                "region": "nose",
                "type": "refine_tip",
                "factor": 1 - self.BEAUTY_RULES["nose"]["tip_refinement"] * 0.5,  # Half strength
                "priority": 2
            })
            operations.append({
                "region": "nose",
                "type": "refine_bridge",
                "factor": 1 - self.BEAUTY_RULES["nose"]["bridge_refinement"] * 0.5,  # Half strength
                "priority": 2
            })
        else:
            # Nose is close to ideal but can still benefit from subtle refinement
            # Apply light tip refinement for polished appearance
            operations.append({
                "region": "nose",
                "type": "refine_tip",
                "factor": 1 - self.BEAUTY_RULES["nose"]["tip_refinement"] * 0.7,  # 70% strength
                "priority": 2
            })
        
        # 3) Jaw asymmetry correction
        jaw_asymmetry = measurements.get("jaw_asymmetry", 0)
        max_correction = self.BEAUTY_RULES["jaw"]["max_asymmetry_correction"]
        
        if jaw_asymmetry > 1.0:  # Only correct if asymmetry > 1mm
            correction = min(jaw_asymmetry, max_correction)
            operations.append({
                "region": "jaw", 
                "type": "balance", 
                "mm": correction,
                "priority": 3
            })
        
        # 4) Chin projection adjustment
        chin_projection = measurements.get("chin_projection", 0)
        # This is a simplified check - in reality you'd compare against ideal proportions
        if chin_projection > 0:
            # Suggest slight enhancement if projection is low
            if chin_projection < 20:  # Arbitrary threshold
                operations.append({
                    "region": "chin", 
                    "type": "enhance", 
                    "amount": 0.15,
                    "priority": 4
                })
        
        # 5) Facial thirds adjustment
        facial_thirds = measurements.get("facial_thirds", {})
        if facial_thirds:
            thirds_ops = self._analyze_facial_thirds(facial_thirds)
            operations.extend(thirds_ops)
        
        # Sort by priority
        operations.sort(key=lambda x: x.get("priority", 99))
        
        return operations
    
    def _analyze_facial_thirds(self, facial_thirds: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze facial thirds and suggest improvements"""
        operations = []
        rules = self.BEAUTY_RULES["facial_thirds"]
        tolerance = rules["tolerance"]
        
        # Check each third
        for third_name, ideal in [("upper", rules["ideal_upper"]), 
                                 ("middle", rules["ideal_middle"]), 
                                 ("lower", rules["ideal_lower"])]:
            current = facial_thirds.get(third_name, ideal)
            deviation = abs(current - ideal)
            
            if deviation > tolerance:
                operations.append({
                    "region": "face",
                    "type": f"adjust_{third_name}_third",
                    "current": current,
                    "target": ideal,
                    "priority": 5
                })
        
        return operations
    
    def get_readable_recommendations(self, operations: List[Dict[str, Any]]) -> List[str]:
        """Convert operations to human-readable recommendations - ensures full disclosure"""
        recommendations = []
        
        # Track which operations are being applied
        nose_ops = []
        other_ops = []
        
        for op in operations:
            region = op.get("region", "")
            op_type = op.get("type", "")
            
            if region == "face" and op_type == "symmetry":
                amount = op.get("amount", 0)
                percentage = int(amount * 100) if amount > 0 else 0
                recommendations.append(
                    f"Facial Symmetry Correction: Balance left/right facial features "
                    f"({percentage}% AI-enhanced symmetry adjustment) - improves overall facial harmony"
                )
            
            elif region == "nose":
                if op_type == "shrink_width":
                    factor = op.get("factor", 1.0)
                    reduction = int((1 - factor) * 100)
                    nose_ops.append(f"{reduction}% overall nasal width reduction")
                elif op_type == "refine_tip":
                    nose_ops.append("nasal tip refinement and definition")
                elif op_type == "refine_bridge":
                    nose_ops.append("nasal bridge narrowing")
            
            elif region == "jaw" and op_type == "balance":
                mm = op.get("mm", 0)
                recommendations.append(
                    f"Jawline Contouring: Correct jaw asymmetry "
                    f"({mm:.1f}mm lateral adjustment) - improves facial symmetry and balance"
                )
            
            elif region == "chin" and op_type == "enhance":
                amount = op.get("amount", 0)
                percentage = int(amount * 100)
                recommendations.append(
                    f"Chin Enhancement: Increase chin projection "
                    f"({percentage}% forward projection) - improves profile definition"
                )
            
            elif region == "face" and "third" in op_type:
                third_name = op_type.replace("adjust_", "").replace("_third", "")
                current = op.get("current", 0)
                target = op.get("target", 0)
                deviation = target - current
                change_pct = abs(deviation) * 100
                
                # Describe realistic treatment methods based on what's actually achievable
                if "upper" in op_type:
                    if abs(deviation) <= 0.02:
                        recommendations.append(
                            f"Upper Third Optimization: Minimal Botox brow lift effect "
                            f"({current:.1%} → {target:.1%}, ~{change_pct:.1f}% change) - "
                            f"very subtle, Botox can only lift brows 1-3mm maximum"
                        )
                    else:
                        recommendations.append(
                            f"Upper Third Optimization: Requires surgical brow lift or forehead reduction "
                            f"({current:.1%} → {target:.1%}) - beyond Botox capability, would need surgery"
                        )
                elif "middle" in op_type:
                    # Middle third: BEST candidate for fillers (NOT Botox)
                    recommendations.append(
                        f"Middle Third Enhancement: Cheek/midface augmentation with dermal fillers "
                        f"({current:.1%} → {target:.1%}, ~{change_pct:.1f}% change) - "
                        f"adds volume and forward projection to midface (NOT achievable with Botox alone)"
                    )
                else:  # lower
                    # Lower third: Already partially handled by chin enhancement
                    recommendations.append(
                        f"Lower Third Optimization: Combined jaw and chin contouring "
                        f"({current:.1%} → {target:.1%}) - complements existing chin enhancement procedures"
                    )
        
        # Combine nose operations into comprehensive recommendation
        if nose_ops:
            nose_desc = ", ".join(nose_ops)
            recommendations.insert(0, 
                f"Comprehensive Rhinoplasty: {nose_desc} - "
                f"creates more refined, elegant nasal proportions for enhanced facial harmony"
            )
        
        # Ensure ALL operations are disclosed
        if not recommendations:
            recommendations.append("Your facial features are already well-balanced!")
            recommendations.append("No enhancements recommended - your facial harmony is optimal")
        
        return recommendations
    
    def get_procedure_labels(self, operations: List[Dict[str, Any]]) -> List[str]:
        """Get medical procedure labels for operations"""
        labels = []
        
        for op in operations:
            region = op.get("region", "")
            op_type = op.get("type", "")
            
            if region == "nose":
                if op_type == "shrink_width":
                    labels.append("Comprehensive rhinoplasty (AI)")
                    labels.append("Nasal width reduction (AI)")
                elif op_type == "refine_tip":
                    labels.append("Tip refinement & definition (AI)")
                elif op_type == "refine_bridge":
                    labels.append("Bridge narrowing & refinement (AI)")
            
            elif region == "jaw":
                if op_type == "balance":
                    labels.append("Jawline contouring (AI)")
            
            elif region == "chin":
                if op_type == "enhance":
                    labels.append("Chin augmentation (filler simulation)")
            
            elif region == "face" and op_type == "symmetry":
                labels.append("Facial symmetry correction (AI)")
        
        return labels
    
    def calculate_harmony_score(self, measurements: Dict[str, Any], operations: List[Dict[str, Any]]) -> int:
        """Calculate comprehensive facial harmony score (0-100) based on multiple factors"""
        scores = []
        
        # 1. Symmetry score (0-1) - weight: 40%
        symmetry_score = measurements.get("symmetry_score", 0.8)
        scores.append(("symmetry", symmetry_score, 0.40))
        
        # 2. Nose-to-IPD ratio - weight: 20%
        # Ideal ratio is around 0.75, penalize if too far from ideal
        ideal_nose_ratio = self.BEAUTY_RULES["nose"]["ideal_nose_to_ipd"]
        nose_ratio = measurements.get("nose_to_ipd_ratio", ideal_nose_ratio)
        nose_deviation = abs(nose_ratio - ideal_nose_ratio) / ideal_nose_ratio
        nose_score = max(0, 1 - nose_deviation * 2)  # Penalize deviations
        scores.append(("nose_proportion", nose_score, 0.20))
        
        # 3. Jaw asymmetry - weight: 15%
        # Lower asymmetry is better (convert to score)
        jaw_asymmetry = measurements.get("jaw_asymmetry", 0)
        max_asymmetry = 10.0  # Maximum expected asymmetry in pixels/mm
        jaw_score = max(0, 1 - (jaw_asymmetry / max_asymmetry))
        scores.append(("jaw_balance", jaw_score, 0.15))
        
        # 4. Chin projection - weight: 10%
        # Score based on whether chin projection is in reasonable range
        chin_projection = measurements.get("chin_projection", 0)
        # Normalize based on expected range (this is simplified)
        chin_score = min(1.0, chin_projection / 20.0) if chin_projection > 0 else 0.7
        scores.append(("chin_projection", chin_score, 0.10))
        
        # 5. Number of recommended operations - weight: 15%
        # Fewer operations needed = higher score
        num_operations = len(operations)
        if num_operations == 0:
            operations_score = 1.0  # Perfect - no changes needed
        elif num_operations == 1:
            operations_score = 0.85  # Good - minor enhancement
        elif num_operations == 2:
            operations_score = 0.70  # Moderate - some improvements
        else:
            operations_score = max(0.5, 1.0 - (num_operations - 2) * 0.1)  # More operations = lower score
        scores.append(("enhancement_potential", operations_score, 0.15))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Convert to 0-100 scale and round
        harmony_score = int(total_score * 100)
        
        return max(0, min(100, harmony_score))  # Clamp between 0-100