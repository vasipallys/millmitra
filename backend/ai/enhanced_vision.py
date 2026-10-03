"""
Enhanced Computer Vision for Rice Quality Assessment

This module implements advanced computer vision techniques using deep learning models
for more accurate rice quality assessment.
"""

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
import json
from datetime import datetime

# Try to import PyTorch with error handling
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision.models import resnet18, ResNet18_Weights
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    torch = None
    nn = None
    print("Warning: PyTorch not available, using traditional computer vision only")
except Exception as e:
    PYTORCH_AVAILABLE = False
    torch = None
    nn = None
    print(f"Warning: PyTorch import failed: {e}")


if PYTORCH_AVAILABLE:
    class RiceQualityCNN(nn.Module):
        """CNN model for rice quality assessment"""
        def __init__(self, num_classes=5):
            super(RiceQualityCNN, self).__init__()
            self.resnet = resnet18(weights=ResNet18_Weights.DEFAULT)
            self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)

        def forward(self, x):
            return self.resnet(x)
else:
    class RiceQualityCNN:
        """Placeholder when PyTorch is not installed."""
        def __init__(self, num_classes=5):
            pass

        def forward(self, x):
            return None


class EnhancedVisionAnalyzer:
    """Enhanced computer vision analyzer for rice quality assessment"""
    
    def __init__(self):
        """Initialize the enhanced vision analyzer"""
        if PYTORCH_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = 'cpu'
        
        # Initialize models
        self.quality_model = self._initialize_quality_model()
        self.defect_model = self._initialize_defect_model()
        
        # Image transforms
        if PYTORCH_AVAILABLE:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
        else:
            self.transform = None
        
        # Quality standards
        self.quality_standards = {
            'basmati': {
                'min_length': 6.0,  # mm
                'max_broken_percentage': 5.0,
                'max_moisture': 14.0,
                'max_foreign_matter': 1.0,
                'min_head_rice': 85.0
            },
            'jasmine': {
                'min_length': 5.5,
                'max_broken_percentage': 7.0,
                'max_moisture': 14.0,
                'max_foreign_matter': 1.5,
                'min_head_rice': 80.0
            },
            'brown': {
                'min_length': 4.5,
                'max_broken_percentage': 10.0,
                'max_moisture': 14.0,
                'max_foreign_matter': 2.0,
                'min_head_rice': 75.0
            }
        }
    
    def _initialize_quality_model(self) -> Optional[nn.Module]:
        """Initialize the quality assessment model"""
        if not PYTORCH_AVAILABLE:
            return None
            
        try:
            model = RiceQualityCNN(num_classes=5)
            model.load_state_dict(torch.load('models/rice_quality_model.pth', 
                                           map_location=self.device))
            model.to(self.device)
            model.eval()
            return model
        except Exception as e:
            print(f"Warning: Could not load quality model: {e}")
            return None
    
    def _initialize_defect_model(self) -> Optional[nn.Module]:
        """Initialize the defect detection model"""
        if not PYTORCH_AVAILABLE:
            return None
            
        try:
            model = RiceQualityCNN(num_classes=6)  # 6 defect types
            model.load_state_dict(torch.load('models/rice_defect_model.pth', 
                                           map_location=self.device))
            model.to(self.device)
            model.eval()
            return model
        except Exception as e:
            print(f"Warning: Could not load defect model: {e}")
            return None
    
    def analyze_rice_sample(self, image_data: str, rice_variety: str = 'basmati') -> Dict:
        """Comprehensive AI-powered rice quality analysis"""
        try:
            # Decode and preprocess image
            image = self._decode_image(image_data)
            if image is None:
                return {'success': False, 'error': 'Invalid image data'}
            
            # Convert to PIL for transforms
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Perform enhanced analysis
            analysis_results = {
                'grain_analysis': self._enhanced_grain_analysis(image),
                'defect_detection': self._enhanced_defect_detection(pil_image),
                'color_analysis': self._enhanced_color_analysis(image),
                'size_distribution': self._enhanced_size_distribution(image),
                'foreign_matter': self._enhanced_foreign_matter_detection(image),
                'moisture_estimation': self._enhanced_moisture_estimation(image),
                'overall_grade': None,
                'quality_score': 0.0,
                'recommendations': []
            }
            
            # Calculate overall quality metrics
            quality_metrics = self._calculate_enhanced_quality_metrics(analysis_results, rice_variety)
            analysis_results.update(quality_metrics)
            
            # Generate AI recommendations
            recommendations = self._generate_enhanced_recommendations(analysis_results, rice_variety)
            analysis_results['recommendations'] = recommendations
            
            return {
                'success': True,
                'analysis': analysis_results,
                'timestamp': datetime.utcnow().isoformat(),
                'variety': rice_variety
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Analysis failed: {str(e)}'}
    
    def _decode_image(self, image_data: str) -> Optional[np.ndarray]:
        """Decode base64 image data"""
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Image decode error: {e}")
            return None
    
    def _enhanced_grain_analysis(self, image: np.ndarray) -> Dict:
        """Enhanced grain analysis using computer vision and ML"""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding to segment grains
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours (individual grains)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            grain_data = []
            total_grains = 0
            broken_grains = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter out noise (too small areas)
                if area < 50:
                    continue
                
                total_grains += 1
                
                # Calculate grain dimensions
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                length = max(width, height)
                width = min(width, height)
                
                # Calculate aspect ratio
                aspect_ratio = length / width if width > 0 else 0
                
                # Detect broken grains (low aspect ratio or irregular shape)
                if aspect_ratio < 2.5 or area < 100:
                    broken_grains += 1
                
                grain_data.append({
                    'length': length * 0.1,  # Convert pixels to mm (approximate)
                    'width': width * 0.1,
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'is_broken': aspect_ratio < 2.5
                })
            
            # Calculate statistics
            if grain_data:
                lengths = [g['length'] for g in grain_data]
                widths = [g['width'] for g in grain_data]
                
                avg_length = np.mean(lengths)
                avg_width = np.mean(widths)
                broken_percentage = (broken_grains / total_grains) * 100 if total_grains > 0 else 0
                
                return {
                    'total_grains': total_grains,
                    'broken_grains': broken_grains,
                    'broken_percentage': broken_percentage,
                    'average_length': avg_length,
                    'average_width': avg_width,
                    'length_std': np.std(lengths),
                    'width_std': np.std(widths),
                    'uniformity_score': 100 - (np.std(lengths) / avg_length * 100) if avg_length > 0 else 0
                }
            else:
                return {
                    'total_grains': 0,
                    'broken_grains': 0,
                    'broken_percentage': 0,
                    'average_length': 0,
                    'average_width': 0,
                    'length_std': 0,
                    'width_std': 0,
                    'uniformity_score': 0
                }
                
        except Exception as e:
            print(f"Enhanced grain analysis error: {e}")
            return {'error': str(e)}
    
    def _enhanced_defect_detection(self, pil_image: Image.Image) -> Dict:
        """Enhanced defect detection using deep learning model"""
        try:
            # Check if PyTorch and model are available
            if not PYTORCH_AVAILABLE or self.defect_model is None:
                # Fallback to traditional CV if model not available
                return self._traditional_defect_detection(pil_image)
            
            # Preprocess image
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.defect_model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                predicted_class = torch.argmax(probabilities).item()
                confidence = probabilities[predicted_class].item()
            
            # Map class indices to defect types
            defect_types = ['chalky', 'discolored', 'damaged', 'insect_damage', 'normal', 'mixed']
            defect_type = defect_types[predicted_class] if predicted_class < len(defect_types) else 'unknown'
            
            return {
                'defect_type': defect_type,
                'confidence': confidence,
                'defect_severity': self._calculate_defect_severity(defect_type),
                'defect_percentage': self._estimate_defect_percentage(defect_type, confidence)
            }
            
        except Exception as e:
            print(f"Enhanced defect detection error: {e}")
            # Fallback to traditional CV on error
            return self._traditional_defect_detection(pil_image)
    
    def _traditional_defect_detection(self, pil_image: Image.Image) -> Dict:
        """Traditional computer vision defect detection (fallback)"""
        try:
            # Convert PIL to OpenCV
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to different color spaces for defect detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            defects = {
                'chalky_grains': 0,
                'discolored_grains': 0,
                'damaged_grains': 0,
                'insect_damage': 0,
                'total_defective': 0
            }
            
            # Detect chalky grains (high brightness, low saturation)
            chalky_mask = cv2.inRange(hsv, (0, 0, 200), (180, 50, 255))
            chalky_contours, _ = cv2.findContours(chalky_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            defects['chalky_grains'] = len([c for c in chalky_contours if cv2.contourArea(c) > 50])
            
            # Detect discolored grains (unusual hue values)
            discolored_mask = cv2.inRange(hsv, (20, 50, 50), (40, 255, 255))  # Yellow/brown tones
            discolored_contours, _ = cv2.findContours(discolored_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            defects['discolored_grains'] = len([c for c in discolored_contours if cv2.contourArea(c) > 50])
            
            # Detect damaged grains (irregular shapes, dark spots)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            damaged_mask = cv2.inRange(gray, 0, 80)  # Very dark regions
            damaged_contours, _ = cv2.findContours(damaged_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            defects['damaged_grains'] = len([c for c in damaged_contours if cv2.contourArea(c) > 30])
            
            # Calculate total defective percentage
            total_grains = self._count_total_grains(image)
            defects['total_defective'] = sum([defects['chalky_grains'], defects['discolored_grains'], defects['damaged_grains']])
            defects['defect_percentage'] = (defects['total_defective'] / total_grains * 100) if total_grains > 0 else 0
            
            return defects
            
        except Exception as e:
            print(f"Traditional defect detection error: {e}")
            return {'error': str(e)}
    
    def _enhanced_color_analysis(self, image: np.ndarray) -> Dict:
        """Enhanced color analysis for quality assessment"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Calculate color statistics
            h_mean = np.mean(hsv[:, :, 0])
            s_mean = np.mean(hsv[:, :, 1])
            v_mean = np.mean(hsv[:, :, 2])
            
            l_mean = np.mean(lab[:, :, 0])
            a_mean = np.mean(lab[:, :, 1])
            b_mean = np.mean(lab[:, :, 2])
            
            # Calculate color uniformity
            h_std = np.std(hsv[:, :, 0])
            color_uniformity = 100 - (h_std / 180 * 100)  # Higher is better
            
            # Determine color grade
            color_grade = self._determine_color_grade(h_mean, s_mean, v_mean)
            
            return {
                'hue_mean': h_mean,
                'saturation_mean': s_mean,
                'value_mean': v_mean,
                'lightness_mean': l_mean,
                'color_uniformity': color_uniformity,
                'color_grade': color_grade,
                'whiteness_index': v_mean  # Higher values indicate whiter rice
            }
            
        except Exception as e:
            print(f"Enhanced color analysis error: {e}")
            return {'error': str(e)}
    
    def _enhanced_size_distribution(self, image: np.ndarray) -> Dict:
        """Enhanced grain size distribution analysis"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            sizes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # Filter noise
                    sizes.append(area)
            
            if sizes:
                # Enhanced size categorization
                sizes_array = np.array(sizes)
                size_mean = np.mean(sizes_array)
                size_std = np.std(sizes_array)

                # Categorize based on standard deviations
                small_threshold = size_mean - size_std
                large_threshold = size_mean + size_std

                small_count = np.sum(sizes_array < small_threshold)
                large_count = np.sum(sizes_array > large_threshold)
                medium_count = len(sizes) - small_count - large_count

                total = len(sizes)
                
                return {
                    'small_grains_percentage': (small_count / total) * 100,
                    'medium_grains_percentage': (medium_count / total) * 100,
                    'large_grains_percentage': (large_count / total) * 100,
                    'size_uniformity': 100 - (np.std(sizes) / np.mean(sizes) * 100),
                    'average_size': np.mean(sizes),
                    'size_variance': np.var(sizes)
                }
            else:
                return {
                    'small_grains_percentage': 0,
                    'medium_grains_percentage': 0,
                    'large_grains_percentage': 0,
                    'size_uniformity': 0,
                    'average_size': 0,
                    'size_variance': 0
                }
                
        except Exception as e:
            print(f"Enhanced size distribution error: {e}")
            return {'error': str(e)}
    
    def _enhanced_foreign_matter_detection(self, image: np.ndarray) -> Dict:
        """Enhanced foreign matter detection"""
        try:
            # Convert to HSV for better color segmentation
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define rice color range (adjust based on variety)
            rice_lower = np.array([0, 0, 180])
            rice_upper = np.array([180, 50, 255])
            
            # Create mask for rice grains
            rice_mask = cv2.inRange(hsv, rice_lower, rice_upper)
            
            # Invert to get foreign matter mask
            foreign_mask = cv2.bitwise_not(rice_mask)
            
            # Remove noise
            kernel = np.ones((3, 3), np.uint8)
            foreign_mask = cv2.morphologyEx(foreign_mask, cv2.MORPH_OPEN, kernel)
            
            # Find foreign matter contours
            contours, _ = cv2.findContours(foreign_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            foreign_matter_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 20)
            total_area = image.shape[0] * image.shape[1]
            
            foreign_matter_percentage = (foreign_matter_area / total_area) * 100
            
            return {
                'foreign_matter_percentage': foreign_matter_percentage,
                'foreign_objects_count': len([c for c in contours if cv2.contourArea(c) > 20]),
                'cleanliness_score': max(0, 100 - foreign_matter_percentage * 10)
            }
            
        except Exception as e:
            print(f"Enhanced foreign matter detection error: {e}")
            return {'error': str(e)}
    
    def _enhanced_moisture_estimation(self, image: np.ndarray) -> Dict:
        """Enhanced moisture content estimation"""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Analyze lightness and color properties
            l_channel = lab[:, :, 0]
            a_channel = lab[:, :, 1]
            b_channel = lab[:, :, 2]
            
            # Calculate features that correlate with moisture
            lightness_mean = np.mean(l_channel)
            lightness_std = np.std(l_channel)
            
            # Enhanced moisture estimation model
            moisture_indicator = (100 - lightness_mean) / 100
            estimated_moisture = 10 + (moisture_indicator * 8)  # Range: 10-18%
            
            return {
                'estimated_moisture_percentage': estimated_moisture,
                'moisture_confidence': 0.75,  # Confidence in estimation
                'visual_indicators': {
                    'lightness': lightness_mean,
                    'uniformity': 100 - (lightness_std / lightness_mean * 100) if lightness_mean > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"Enhanced moisture estimation error: {e}")
            return {'error': str(e)}
    
    def _calculate_enhanced_quality_metrics(self, analysis: Dict, variety: str) -> Dict:
        """Calculate enhanced quality metrics and grade"""
        try:
            standards = self.quality_standards.get(variety, self.quality_standards['basmati'])
            
            scores = {}
            
            # Grain characteristics score
            grain_analysis = analysis.get('grain_analysis', {})
            if 'broken_percentage' in grain_analysis:
                broken_score = max(0, 100 - (grain_analysis['broken_percentage'] / standards['max_broken_percentage'] * 100))
                scores['broken_score'] = broken_score
            
            # Length score
            if 'average_length' in grain_analysis:
                length_score = min(100, (grain_analysis['average_length'] / standards['min_length']) * 100)
                scores['length_score'] = length_score
            
            # Defect score
            defect_analysis = analysis.get('defect_detection', {})
            if 'defect_percentage' in defect_analysis:
                defect_score = max(0, 100 - defect_analysis['defect_percentage'] * 2)
                scores['defect_score'] = defect_score
            
            # Color score
            color_analysis = analysis.get('color_analysis', {})
            if 'color_uniformity' in color_analysis:
                scores['color_score'] = color_analysis['color_uniformity']
            
            # Foreign matter score
            foreign_analysis = analysis.get('foreign_matter', {})
            if 'cleanliness_score' in foreign_analysis:
                scores['cleanliness_score'] = foreign_analysis['cleanliness_score']
            
            # Moisture score
            moisture_analysis = analysis.get('moisture_estimation', {})
            if 'estimated_moisture_percentage' in moisture_analysis:
                moisture_diff = abs(moisture_analysis['estimated_moisture_percentage'] - 14)
                moisture_score = max(0, 100 - moisture_diff * 5)
                scores['moisture_score'] = moisture_score
            
            # Calculate overall quality score
            if scores:
                overall_score = np.mean(list(scores.values()))
            else:
                overall_score = 0
            
            # Determine grade
            if overall_score >= 90:
                grade = 'A+'
            elif overall_score >= 80:
                grade = 'A'
            elif overall_score >= 70:
                grade = 'B'
            elif overall_score >= 60:
                grade = 'C'
            else:
                grade = 'D'
            
            return {
                'quality_score': overall_score,
                'overall_grade': grade,
                'individual_scores': scores,
                'grade_confidence': min(100, overall_score + 10)
            }
            
        except Exception as e:
            print(f"Enhanced quality metrics calculation error: {e}")
            return {'quality_score': 0, 'overall_grade': 'D', 'error': str(e)}
    
    def _generate_enhanced_recommendations(self, analysis: Dict, variety: str) -> List[Dict]:
        """Generate enhanced AI-powered quality improvement recommendations"""
        recommendations = []
        
        try:
            # Analyze broken percentage
            grain_analysis = analysis.get('grain_analysis', {})
            if grain_analysis.get('broken_percentage', 0) > 10:
                recommendations.append({
                    'category': 'processing',
                    'priority': 'high',
                    'issue': 'High broken rice percentage',
                    'recommendation': 'Adjust milling parameters to reduce grain breakage. Check rubber roll pressure and clearance.',
                    'expected_improvement': '15-25% reduction in broken grains'
                })
            
            # Analyze moisture content
            moisture_analysis = analysis.get('moisture_estimation', {})
            moisture = moisture_analysis.get('estimated_moisture_percentage', 14)
            if moisture > 14.5:
                recommendations.append({
                    'category': 'drying',
                    'priority': 'high',
                    'issue': 'High moisture content',
                    'recommendation': 'Improve drying process. Extend drying time or increase temperature gradually.',
                    'expected_improvement': 'Better storage life and quality retention'
                })
            
            # Analyze foreign matter
            foreign_analysis = analysis.get('foreign_matter', {})
            if foreign_analysis.get('foreign_matter_percentage', 0) > 2:
                recommendations.append({
                    'category': 'cleaning',
                    'priority': 'medium',
                    'issue': 'High foreign matter content',
                    'recommendation': 'Improve pre-cleaning process. Check destoner and separator efficiency.',
                    'expected_improvement': '50-70% reduction in foreign matter'
                })
            
            # Analyze color uniformity
            color_analysis = analysis.get('color_analysis', {})
            if color_analysis.get('color_uniformity', 100) < 80:
                recommendations.append({
                    'category': 'sorting',
                    'priority': 'medium',
                    'issue': 'Poor color uniformity',
                    'recommendation': 'Implement color sorting or improve optical sorting parameters.',
                    'expected_improvement': 'Better visual appeal and market value'
                })
            
            # Analyze defects
            defect_analysis = analysis.get('defect_detection', {})
            if defect_analysis.get('defect_percentage', 0) > 5:
                recommendations.append({
                    'category': 'quality_control',
                    'priority': 'high',
                    'issue': 'High defect percentage',
                    'recommendation': 'Implement stricter quality control at input stage. Check storage conditions.',
                    'expected_improvement': 'Significant improvement in overall grade'
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Enhanced recommendation generation error: {e}")
            return []
    
    def _calculate_defect_severity(self, defect_type: str) -> str:
        """Calculate defect severity based on type"""
        severity_map = {
            'normal': 'low',
            'chalky': 'low',
            'discolored': 'medium',
            'damaged': 'high',
            'insect_damage': 'high',
            'mixed': 'medium'
        }
        return severity_map.get(defect_type, 'medium')
    
    def _estimate_defect_percentage(self, defect_type: str, confidence: float) -> float:
        """Estimate defect percentage based on type and confidence"""
        base_percentage = {
            'normal': 0.0,
            'chalky': 2.0,
            'discolored': 3.0,
            'damaged': 5.0,
            'insect_damage': 7.0,
            'mixed': 4.0
        }
        
        base = base_percentage.get(defect_type, 2.0)
        return base * confidence
    
    def _count_total_grains(self, image: np.ndarray) -> int:
        """Count total number of grains in image"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return len([c for c in contours if cv2.contourArea(c) > 50])
        except:
            return 0
    
    def _determine_color_grade(self, hue: float, saturation: float, value: float) -> str:
        """Determine color grade based on HSV values"""
        if value > 200 and saturation < 30:
            return 'Excellent'
        elif value > 180 and saturation < 50:
            return 'Good'
        elif value > 160:
            return 'Average'
        else:
            return 'Poor'


def main():
    """Test the enhanced vision analyzer"""
    print("Testing Enhanced Vision Analyzer...")
    
    # Create analyzer
    analyzer = EnhancedVisionAnalyzer()
    
    # Test with a sample (this would normally be a real image)
    # For demonstration, we'll create a dummy base64 string
    dummy_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBAQE"  # Truncated
    
    # Analyze sample
    result = analyzer.analyze_rice_sample(dummy_image, 'basmati')
    print(f"Analysis result: {result}")

if __name__ == "__main__":
    main()
