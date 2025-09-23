# Enhanced Computer Vision Module

## Overview

The Enhanced Computer Vision Module is an advanced AI-powered system for rice quality assessment. It combines traditional computer vision techniques with deep learning models to provide comprehensive analysis of rice quality characteristics.

## Features

1. **Grain Analysis**
   - Total grain counting
   - Broken grain detection
   - Grain size and dimension analysis
   - Uniformity scoring

2. **Defect Detection**
   - Chalky grain detection
   - Discolored grain detection
   - Damaged grain detection
   - Insect damage detection
   - Defect severity assessment

3. **Color Analysis**
   - Color uniformity measurement
   - Whiteness index calculation
   - Color grade determination

4. **Size Distribution**
   - Grain size categorization (small, medium, large)
   - Size uniformity scoring
   - Statistical analysis of grain dimensions

5. **Foreign Matter Detection**
   - Foreign object identification
   - Cleanliness scoring
   - Contamination percentage calculation

6. **Moisture Estimation**
   - Visual moisture content estimation
   - Confidence scoring

7. **Quality Grading**
   - Overall quality scoring
   - Grade classification (A+, A, B, C, D)
   - Individual component scoring

8. **AI Recommendations**
   - Processing improvement suggestions
   - Priority-based recommendations
   - Expected improvement estimates

## API Endpoints

### Health Check

```
GET /api/enhanced-vision/health
```

Returns the status of the enhanced vision service.

### Single Image Analysis

```
POST /api/enhanced-vision/analyze/image
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "image": "base64_encoded_image_data",
  "variety": "basmati",
  "batch_id": "optional_batch_id",
  "sample_type": "final_product"
}
```

Analyzes a single rice sample image and returns comprehensive quality metrics.

### Batch Image Analysis

```
POST /api/enhanced-vision/analyze/batch
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "images": ["base64_encoded_image_data_1", "base64_encoded_image_data_2", ...],
  "variety": "basmati",
  "batch_id": "optional_batch_id"
}
```

Analyzes multiple rice sample images and returns batch-level quality metrics.

## Implementation Details

### EnhancedVisionAnalyzer Class

The core of the enhanced vision module is the `EnhancedVisionAnalyzer` class, which provides all the analysis functionality.

#### Initialization

```python
analyzer = EnhancedVisionAnalyzer()
```

#### Main Analysis Method

```python
result = analyzer.analyze_rice_sample(image_data, rice_variety='basmati')
```

### Deep Learning Models

The module uses ResNet-18 based models for quality assessment and defect detection:

1. **Quality Assessment Model** - Classifies rice quality grades (A+, A, B, C, D)
2. **Defect Detection Model** - Identifies 6 types of defects

Models are loaded from `models/rice_quality_model.pth` and `models/rice_defect_model.pth` respectively.

### Fallback Mechanism

When PyTorch is not available or models cannot be loaded, the system gracefully falls back to traditional computer vision techniques for all analyses.

## Quality Standards

The system implements variety-specific quality standards:

1. **Basmati** - Premium long-grain rice
2. **Jasmine** - Fragrant long-grain rice
3. **Brown** - Unmilled rice

Each variety has specific requirements for:
- Minimum grain length
- Maximum broken grain percentage
- Maximum moisture content
- Maximum foreign matter percentage
- Minimum head rice percentage

## Testing

The module includes comprehensive unit tests in `tests/test_ai_vision.py` covering:
- Core vision analysis functionality
- API endpoint validation
- Error handling
- Fallback mechanism verification

## Dependencies

- OpenCV (cv2)
- NumPy
- PIL/Pillow
- PyTorch (optional, with fallback)
- FAISS (for similarity search)

## Installation

To install the required dependencies:

```bash
pip install -r requirements-ai.txt
```

## Usage Example

```python
from ai.enhanced_vision import EnhancedVisionAnalyzer

# Initialize analyzer
analyzer = EnhancedVisionAnalyzer()

# Analyze rice sample
with open('rice_sample.jpg', 'rb') as f:
    image_data = f.read()
    
# Convert to base64
import base64
encoded_image = base64.b64encode(image_data).decode('utf-8')

# Perform analysis
result = analyzer.analyze_rice_sample(encoded_image, 'basmati')

if result['success']:
    print(f"Quality Score: {result['analysis']['quality_score']}")
    print(f"Grade: {result['analysis']['overall_grade']}")
    print(f"Recommendations: {result['analysis']['recommendations']}")
else:
    print(f"Analysis failed: {result['error']}")
```
