"""
Advanced Computer Vision Service for Rice Quality Assessment
Real-time quality analysis with defect detection and grading automation
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image, ImageEnhance, ImageFilter
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiceQualityVisionAnalyzer:
    """Advanced computer vision analyzer for rice quality assessment"""
    
    def __init__(self):
        self.quality_standards = self._load_quality_standards()
        self.defect_classifiers = self._initialize_defect_classifiers()
        self.color_profiles = self._load_color_profiles()
        
    def _load_quality_standards(self) -> Dict:
        """Load rice quality standards and thresholds"""
        return {
            'grain_size': {
                'long': {'min': 6.0, 'max': 8.0},  # mm
                'medium': {'min': 5.0, 'max': 6.0},
                'short': {'min': 3.0, 'max': 5.0}
            },
            'color_standards': {
                'white': {'hue_range': (0, 180), 'saturation_max': 30, 'value_min': 200},
                'brown': {'hue_range': (10, 25), 'saturation_min': 50, 'value_min': 100},
                'red': {'hue_range': (0, 10), 'saturation_min': 100, 'value_min': 150}
            },
            'defect_thresholds': {
                'broken_grains_max': 5.0,  # percentage
                'chalky_grains_max': 6.0,
                'foreign_matter_max': 1.0,
                'damaged_grains_max': 4.0,
                'discolored_grains_max': 3.0
            },
            'grade_criteria': {
                'A+': {'broken': 2.0, 'chalky': 3.0, 'foreign': 0.5, 'damaged': 2.0},
                'A': {'broken': 5.0, 'chalky': 6.0, 'foreign': 1.0, 'damaged': 4.0},
                'B': {'broken': 10.0, 'chalky': 10.0, 'foreign': 2.0, 'damaged': 8.0},
                'C': {'broken': 15.0, 'chalky': 15.0, 'foreign': 3.0, 'damaged': 12.0}
            }
        }
    
    def _initialize_defect_classifiers(self) -> Dict:
        """Initialize defect detection classifiers"""
        return {
            'broken_grain_detector': self._create_broken_grain_detector(),
            'chalky_grain_detector': self._create_chalky_grain_detector(),
            'foreign_matter_detector': self._create_foreign_matter_detector(),
            'discoloration_detector': self._create_discoloration_detector()
        }
    
    def _load_color_profiles(self) -> Dict:
        """Load color profiles for different rice varieties"""
        return {
            'basmati': {
                'expected_hue': (15, 25),
                'expected_saturation': (10, 40),
                'expected_value': (180, 255)
            },
            'jasmine': {
                'expected_hue': (20, 30),
                'expected_saturation': (15, 45),
                'expected_value': (190, 255)
            },
            'sona_masuri': {
                'expected_hue': (10, 20),
                'expected_saturation': (5, 35),
                'expected_value': (200, 255)
            }
        }
    
    def analyze_rice_sample(self, image_data: str, variety: str = 'basmati') -> Dict:
        """
        Comprehensive rice quality analysis from image
        
        Args:
            image_data: Base64 encoded image string
            variety: Rice variety for specific analysis
            
        Returns:
            Comprehensive quality analysis results
        """
        try:
            # Decode and preprocess image
            image = self._decode_image(image_data)
            if image is None:
                return self._error_response("Failed to decode image")
            
            # Preprocess image for analysis
            processed_image = self._preprocess_image(image)
            
            # Segment individual grains
            grain_contours = self._segment_grains(processed_image)
            
            if len(grain_contours) < 10:
                return self._error_response("Insufficient grains detected for reliable analysis")
            
            # Analyze each grain
            grain_analyses = []
            for contour in grain_contours:
                grain_analysis = self._analyze_single_grain(processed_image, contour, variety)
                grain_analyses.append(grain_analysis)
            
            # Compile overall analysis
            overall_analysis = self._compile_overall_analysis(grain_analyses, variety)
            
            # Generate quality grade
            quality_grade = self._calculate_quality_grade(overall_analysis)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(overall_analysis)
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'variety': variety,
                'total_grains_analyzed': len(grain_analyses),
                'overall_analysis': overall_analysis,
                'quality_grade': quality_grade,
                'recommendations': recommendations,
                'detailed_metrics': self._calculate_detailed_metrics(grain_analyses),
                'confidence_score': self._calculate_confidence_score(grain_analyses)
            }
            
        except Exception as e:
            logger.error(f"Error in rice analysis: {str(e)}")
            return self._error_response(f"Analysis failed: {str(e)}")
    
    def _decode_image(self, image_data: str) -> Optional[np.ndarray]:
        """Decode base64 image data"""
        try:
            # Remove data URL prefix if present
            if 'data:image' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            logger.error(f"Image decoding error: {str(e)}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for optimal grain detection"""
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Enhance contrast
        pil_image = Image.fromarray(rgb_image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.2)
        
        # Apply slight blur to reduce noise
        blurred = enhanced.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Convert back to OpenCV format
        processed = cv2.cvtColor(np.array(blurred), cv2.COLOR_RGB2BGR)
        
        return processed
    
    def _segment_grains(self, image: np.ndarray) -> List:
        """Segment individual rice grains from the image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size (grain-like objects)
        grain_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 2000:  # Reasonable grain size range
                grain_contours.append(contour)
        
        return grain_contours
    
    def _analyze_single_grain(self, image: np.ndarray, contour, variety: str) -> Dict:
        """Analyze a single grain for defects and characteristics"""
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        grain_roi = image[y:y+h, x:x+w]
        
        # Calculate basic measurements
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Calculate grain dimensions
        length = max(w, h)
        width = min(w, h)
        aspect_ratio = length / width if width > 0 else 0
        
        # Analyze color properties
        color_analysis = self._analyze_grain_color(grain_roi, variety)
        
        # Detect defects
        defects = self._detect_grain_defects(grain_roi, contour)
        
        # Calculate shape metrics
        shape_metrics = self._calculate_shape_metrics(contour, area, perimeter)
        
        return {
            'area': area,
            'length': length,
            'width': width,
            'aspect_ratio': aspect_ratio,
            'color_analysis': color_analysis,
            'defects': defects,
            'shape_metrics': shape_metrics,
            'is_broken': defects['is_broken'],
            'is_chalky': defects['is_chalky'],
            'is_discolored': defects['is_discolored'],
            'is_foreign_matter': defects['is_foreign_matter']
        }
    
    def _analyze_grain_color(self, grain_roi: np.ndarray, variety: str) -> Dict:
        """Analyze color properties of a grain"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(grain_roi, cv2.COLOR_BGR2HSV)
        
        # Calculate mean color values
        mean_hue = np.mean(hsv[:, :, 0])
        mean_saturation = np.mean(hsv[:, :, 1])
        mean_value = np.mean(hsv[:, :, 2])
        
        # Get expected color profile for variety
        expected_profile = self.color_profiles.get(variety, self.color_profiles['basmati'])
        
        # Check if color is within expected range
        hue_in_range = expected_profile['expected_hue'][0] <= mean_hue <= expected_profile['expected_hue'][1]
        saturation_in_range = expected_profile['expected_saturation'][0] <= mean_saturation <= expected_profile['expected_saturation'][1]
        value_in_range = expected_profile['expected_value'][0] <= mean_value <= expected_profile['expected_value'][1]
        
        return {
            'mean_hue': float(mean_hue),
            'mean_saturation': float(mean_saturation),
            'mean_value': float(mean_value),
            'color_uniformity': self._calculate_color_uniformity(hsv),
            'is_normal_color': hue_in_range and saturation_in_range and value_in_range,
            'color_deviation_score': self._calculate_color_deviation(
                (mean_hue, mean_saturation, mean_value), expected_profile
            )
        }
    
    def _detect_grain_defects(self, grain_roi: np.ndarray, contour) -> Dict:
        """Detect various defects in a grain"""
        # Broken grain detection (based on shape irregularity)
        is_broken = self._detect_broken_grain(contour)
        
        # Chalky grain detection (based on color and texture)
        is_chalky = self._detect_chalky_grain(grain_roi)
        
        # Discoloration detection
        is_discolored = self._detect_discoloration(grain_roi)
        
        # Foreign matter detection (based on color and shape)
        is_foreign_matter = self._detect_foreign_matter(grain_roi, contour)
        
        return {
            'is_broken': is_broken,
            'is_chalky': is_chalky,
            'is_discolored': is_discolored,
            'is_foreign_matter': is_foreign_matter,
            'defect_score': sum([is_broken, is_chalky, is_discolored, is_foreign_matter])
        }
    
    def _detect_broken_grain(self, contour) -> bool:
        """Detect if grain is broken based on shape analysis"""
        # Calculate shape metrics
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return True
        
        # Circularity (4π*area/perimeter²)
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Convex hull analysis
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Broken grains typically have low circularity and solidity
        return circularity < 0.3 or solidity < 0.7
    
    def _detect_chalky_grain(self, grain_roi: np.ndarray) -> bool:
        """Detect chalky grains based on color and texture"""
        # Convert to grayscale
        gray = cv2.cvtColor(grain_roi, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture metrics
        texture_variance = np.var(gray)
        mean_brightness = np.mean(gray)
        
        # Chalky grains are typically very bright with low texture variance
        return mean_brightness > 200 and texture_variance < 100
    
    def _detect_discoloration(self, grain_roi: np.ndarray) -> bool:
        """Detect discolored grains"""
        # Convert to HSV
        hsv = cv2.cvtColor(grain_roi, cv2.COLOR_BGR2HSV)
        
        # Check for unusual hue values (brown, yellow, red spots)
        hue = hsv[:, :, 0]
        saturation = hsv[:, :, 1]
        
        # Count pixels with unusual colors
        unusual_color_pixels = np.sum(
            ((hue < 10) | (hue > 170)) & (saturation > 50)
        )
        
        total_pixels = hue.size
        unusual_ratio = unusual_color_pixels / total_pixels
        
        return unusual_ratio > 0.1  # More than 10% unusual colored pixels
    
    def _detect_foreign_matter(self, grain_roi: np.ndarray, contour) -> bool:
        """Detect foreign matter based on color and shape"""
        # Shape analysis - foreign matter often has very different shapes
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        
        # Color analysis - foreign matter often has very different colors
        hsv = cv2.cvtColor(grain_roi, cv2.COLOR_BGR2HSV)
        mean_hue = np.mean(hsv[:, :, 0])
        mean_saturation = np.mean(hsv[:, :, 1])
        
        # Foreign matter typically has extreme aspect ratios or unusual colors
        extreme_shape = aspect_ratio > 5 or aspect_ratio < 0.2
        unusual_color = mean_saturation > 100 or mean_hue < 5 or mean_hue > 175
        
        return extreme_shape or unusual_color
    
    def _calculate_shape_metrics(self, contour, area: float, perimeter: float) -> Dict:
        """Calculate various shape metrics for the grain"""
        if perimeter == 0:
            return {'circularity': 0, 'solidity': 0, 'extent': 0}
        
        # Circularity
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Solidity (area/convex_hull_area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Extent (area/bounding_rectangle_area)
        x, y, w, h = cv2.boundingRect(contour)
        extent = area / (w * h) if (w * h) > 0 else 0
        
        return {
            'circularity': float(circularity),
            'solidity': float(solidity),
            'extent': float(extent)
        }
    
    def _calculate_color_uniformity(self, hsv: np.ndarray) -> float:
        """Calculate color uniformity score"""
        # Calculate standard deviation of hue and saturation
        hue_std = np.std(hsv[:, :, 0])
        saturation_std = np.std(hsv[:, :, 1])
        
        # Lower standard deviation means more uniform color
        uniformity_score = 100 / (1 + hue_std + saturation_std)
        
        return float(min(uniformity_score, 100))
    
    def _calculate_color_deviation(self, actual_color: Tuple, expected_profile: Dict) -> float:
        """Calculate deviation from expected color profile"""
        hue, saturation, value = actual_color
        expected_hue = np.mean(expected_profile['expected_hue'])
        expected_saturation = np.mean(expected_profile['expected_saturation'])
        expected_value = np.mean(expected_profile['expected_value'])
        
        # Calculate normalized deviations
        hue_deviation = abs(hue - expected_hue) / 180
        saturation_deviation = abs(saturation - expected_saturation) / 255
        value_deviation = abs(value - expected_value) / 255
        
        # Combined deviation score
        total_deviation = (hue_deviation + saturation_deviation + value_deviation) / 3
        
        return float(total_deviation * 100)
    
    def _compile_overall_analysis(self, grain_analyses: List[Dict], variety: str) -> Dict:
        """Compile overall analysis from individual grain analyses"""
        total_grains = len(grain_analyses)
        
        if total_grains == 0:
            return {}
        
        # Count defects
        broken_count = sum(1 for grain in grain_analyses if grain['is_broken'])
        chalky_count = sum(1 for grain in grain_analyses if grain['is_chalky'])
        discolored_count = sum(1 for grain in grain_analyses if grain['is_discolored'])
        foreign_matter_count = sum(1 for grain in grain_analyses if grain['is_foreign_matter'])
        
        # Calculate percentages
        broken_percentage = (broken_count / total_grains) * 100
        chalky_percentage = (chalky_count / total_grains) * 100
        discolored_percentage = (discolored_count / total_grains) * 100
        foreign_matter_percentage = (foreign_matter_count / total_grains) * 100
        
        # Calculate average measurements
        avg_length = np.mean([grain['length'] for grain in grain_analyses])
        avg_width = np.mean([grain['width'] for grain in grain_analyses])
        avg_aspect_ratio = np.mean([grain['aspect_ratio'] for grain in grain_analyses])
        
        # Calculate color metrics
        avg_color_uniformity = np.mean([
            grain['color_analysis']['color_uniformity'] for grain in grain_analyses
        ])
        avg_color_deviation = np.mean([
            grain['color_analysis']['color_deviation_score'] for grain in grain_analyses
        ])
        
        return {
            'total_grains': total_grains,
            'broken_grains': {
                'count': broken_count,
                'percentage': round(broken_percentage, 2)
            },
            'chalky_grains': {
                'count': chalky_count,
                'percentage': round(chalky_percentage, 2)
            },
            'discolored_grains': {
                'count': discolored_count,
                'percentage': round(discolored_percentage, 2)
            },
            'foreign_matter': {
                'count': foreign_matter_count,
                'percentage': round(foreign_matter_percentage, 2)
            },
            'average_measurements': {
                'length': round(avg_length, 2),
                'width': round(avg_width, 2),
                'aspect_ratio': round(avg_aspect_ratio, 2)
            },
            'color_metrics': {
                'uniformity_score': round(avg_color_uniformity, 2),
                'deviation_score': round(avg_color_deviation, 2)
            }
        }
    
    def _calculate_quality_grade(self, analysis: Dict) -> Dict:
        """Calculate quality grade based on analysis results"""
        if not analysis:
            return {'grade': 'Unknown', 'score': 0, 'reasoning': 'Insufficient data'}
        
        broken_pct = analysis['broken_grains']['percentage']
        chalky_pct = analysis['chalky_grains']['percentage']
        foreign_pct = analysis['foreign_matter']['percentage']
        discolored_pct = analysis['discolored_grains']['percentage']
        
        # Check against grade criteria
        criteria = self.quality_standards['grade_criteria']
        
        for grade in ['A+', 'A', 'B', 'C']:
            grade_criteria = criteria[grade]
            if (broken_pct <= grade_criteria['broken'] and
                chalky_pct <= grade_criteria['chalky'] and
                foreign_pct <= grade_criteria['foreign'] and
                discolored_pct <= grade_criteria['damaged']):
                
                # Calculate quality score (0-100)
                score = self._calculate_quality_score(analysis, grade)
                
                return {
                    'grade': grade,
                    'score': score,
                    'reasoning': f'Meets {grade} grade criteria',
                    'criteria_met': {
                        'broken_grains': broken_pct <= grade_criteria['broken'],
                        'chalky_grains': chalky_pct <= grade_criteria['chalky'],
                        'foreign_matter': foreign_pct <= grade_criteria['foreign'],
                        'discolored_grains': discolored_pct <= grade_criteria['damaged']
                    }
                }
        
        # If no grade criteria met
        return {
            'grade': 'D',
            'score': 30,
            'reasoning': 'Does not meet minimum quality standards',
            'criteria_met': {
                'broken_grains': False,
                'chalky_grains': False,
                'foreign_matter': False,
                'discolored_grains': False
            }
        }
    
    def _calculate_quality_score(self, analysis: Dict, grade: str) -> int:
        """Calculate numerical quality score (0-100)"""
        base_scores = {'A+': 95, 'A': 85, 'B': 75, 'C': 65, 'D': 30}
        base_score = base_scores.get(grade, 30)
        
        # Adjust based on specific metrics
        broken_pct = analysis['broken_grains']['percentage']
        chalky_pct = analysis['chalky_grains']['percentage']
        color_uniformity = analysis['color_metrics']['uniformity_score']
        
        # Penalties for defects
        penalty = (broken_pct * 0.5) + (chalky_pct * 0.3)
        
        # Bonus for good color uniformity
        bonus = (color_uniformity - 50) * 0.1 if color_uniformity > 50 else 0
        
        final_score = base_score - penalty + bonus
        return max(0, min(100, int(final_score)))
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        if not analysis:
            return ["Unable to generate recommendations - insufficient data"]
        
        broken_pct = analysis['broken_grains']['percentage']
        chalky_pct = analysis['chalky_grains']['percentage']
        foreign_pct = analysis['foreign_matter']['percentage']
        color_deviation = analysis['color_metrics']['deviation_score']
        
        if broken_pct > 5:
            recommendations.append(
                f"High broken grain percentage ({broken_pct:.1f}%). "
                "Consider adjusting milling parameters or improving handling procedures."
            )
        
        if chalky_pct > 6:
            recommendations.append(
                f"Elevated chalky grain percentage ({chalky_pct:.1f}%). "
                "Review drying and storage conditions to prevent chalk formation."
            )
        
        if foreign_pct > 1:
            recommendations.append(
                f"Foreign matter detected ({foreign_pct:.1f}%). "
                "Improve cleaning and sorting processes before milling."
            )
        
        if color_deviation > 30:
            recommendations.append(
                "Significant color variation detected. "
                "Check for proper variety segregation and storage conditions."
            )
        
        if not recommendations:
            recommendations.append("Quality meets standards. Continue current processing methods.")
        
        return recommendations
    
    def _calculate_detailed_metrics(self, grain_analyses: List[Dict]) -> Dict:
        """Calculate detailed metrics for reporting"""
        if not grain_analyses:
            return {}
        
        # Size distribution
        lengths = [grain['length'] for grain in grain_analyses]
        widths = [grain['width'] for grain in grain_analyses]
        
        # Shape distribution
        aspect_ratios = [grain['aspect_ratio'] for grain in grain_analyses]
        circularities = [grain['shape_metrics']['circularity'] for grain in grain_analyses]
        
        return {
            'size_distribution': {
                'length': {
                    'min': float(np.min(lengths)),
                    'max': float(np.max(lengths)),
                    'mean': float(np.mean(lengths)),
                    'std': float(np.std(lengths))
                },
                'width': {
                    'min': float(np.min(widths)),
                    'max': float(np.max(widths)),
                    'mean': float(np.mean(widths)),
                    'std': float(np.std(widths))
                }
            },
            'shape_distribution': {
                'aspect_ratio': {
                    'min': float(np.min(aspect_ratios)),
                    'max': float(np.max(aspect_ratios)),
                    'mean': float(np.mean(aspect_ratios)),
                    'std': float(np.std(aspect_ratios))
                },
                'circularity': {
                    'min': float(np.min(circularities)),
                    'max': float(np.max(circularities)),
                    'mean': float(np.mean(circularities)),
                    'std': float(np.std(circularities))
                }
            }
        }
    
    def _calculate_confidence_score(self, grain_analyses: List[Dict]) -> float:
        """Calculate confidence score for the analysis"""
        if not grain_analyses:
            return 0.0
        
        # Base confidence on number of grains analyzed
        grain_count_score = min(len(grain_analyses) / 100, 1.0) * 40
        
        # Image quality indicators
        avg_area = np.mean([grain['area'] for grain in grain_analyses])
        area_score = min(avg_area / 500, 1.0) * 30  # Larger grains = better image quality
        
        # Color analysis quality
        color_uniformities = [
            grain['color_analysis']['color_uniformity'] for grain in grain_analyses
        ]
        color_score = np.mean(color_uniformities) / 100 * 30
        
        total_confidence = grain_count_score + area_score + color_score
        return round(total_confidence, 2)
    
    def _error_response(self, message: str) -> Dict:
        """Generate error response"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
    
    # Placeholder methods for defect classifiers (would be ML models in production)
    def _create_broken_grain_detector(self):
        """Create broken grain detection classifier"""
        return lambda x: False  # Placeholder
    
    def _create_chalky_grain_detector(self):
        """Create chalky grain detection classifier"""
        return lambda x: False  # Placeholder
    
    def _create_foreign_matter_detector(self):
        """Create foreign matter detection classifier"""
        return lambda x: False  # Placeholder
    
    def _create_discoloration_detector(self):
        """Create discoloration detection classifier"""
        return lambda x: False  # Placeholder

# Global instance
rice_vision_analyzer = RiceQualityVisionAnalyzer()
