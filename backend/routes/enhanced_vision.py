"""
Enhanced Vision Quality Assessment Routes
Advanced computer vision-based quality assessment using deep learning
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add ai directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))

try:
    from enhanced_vision import EnhancedVisionAnalyzer, PYTORCH_AVAILABLE
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced vision module not available: {e}")
    VISION_AVAILABLE = False
    PYTORCH_AVAILABLE = False

from models import QualityTest, ProductionBatch, User
from extensions import db

enhanced_vision_bp = Blueprint('enhanced_vision', __name__)

# Initialize vision analyzer
if VISION_AVAILABLE:
    vision_analyzer = EnhancedVisionAnalyzer()
else:
    vision_analyzer = None

@enhanced_vision_bp.route('/analyze/image', methods=['POST'])
@jwt_required()
def analyze_quality_image():
    """Analyze rice quality from image using enhanced AI computer vision"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'image' not in data:
            return jsonify({'error': 'Image data required'}), 400
        
        image_data = data['image']
        rice_variety = data.get('variety', 'basmati')
        batch_id = data.get('batch_id')
        sample_type = data.get('sample_type', 'final_product')
        
        # Perform enhanced AI analysis
        if not VISION_AVAILABLE:
            return jsonify({'error': 'Enhanced vision analysis not available'}), 501
        
        analysis_result = vision_analyzer.analyze_rice_sample(image_data, rice_variety)
        
        if not analysis_result['success']:
            return jsonify(analysis_result), 400
        
        # Create quality test record
        test_id = f"QT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        quality_test = QualityTest(
            test_id=test_id,
            batch_id=batch_id,
            sample_type=sample_type,
            test_date=datetime.utcnow(),
            tested_by=user_id,
            test_method='enhanced_ai_vision',
            test_results=analysis_result['analysis'],
            quality_score=analysis_result['analysis'].get('quality_score', 0),
            grade=analysis_result['analysis'].get('overall_grade', 'D')
        )
        
        db.session.add(quality_test)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'analysis': analysis_result['analysis'],
            'timestamp': analysis_result['timestamp'],
            'message': 'Quality analysis completed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@enhanced_vision_bp.route('/analyze/batch', methods=['POST'])
@jwt_required()
def analyze_batch_images():
    """Analyze multiple rice quality images in batch"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        images = data.get('images', [])
        rice_variety = data.get('variety', 'basmati')
        batch_id = data.get('batch_id')
        
        if not images:
            return jsonify({'error': 'At least one image required'}), 400
        
        if not VISION_AVAILABLE:
            return jsonify({'error': 'Enhanced vision analysis not available'}), 501
        
        # Analyze all images
        results = []
        total_score = 0
        
        for i, image_data in enumerate(images):
            analysis_result = vision_analyzer.analyze_rice_sample(image_data, rice_variety)
            
            if analysis_result['success']:
                results.append({
                    'image_index': i,
                    'analysis': analysis_result['analysis'],
                    'timestamp': analysis_result['timestamp']
                })
                total_score += analysis_result['analysis'].get('quality_score', 0)
            else:
                results.append({
                    'image_index': i,
                    'error': analysis_result.get('error', 'Analysis failed')
                })
        
        # Calculate batch average
        avg_score = total_score / len([r for r in results if 'analysis' in r]) if results else 0
        
        # Determine batch grade
        if avg_score >= 90:
            batch_grade = 'A+'
        elif avg_score >= 80:
            batch_grade = 'A'
        elif avg_score >= 70:
            batch_grade = 'B'
        elif avg_score >= 60:
            batch_grade = 'C'
        else:
            batch_grade = 'D'
        
        return jsonify({
            'success': True,
            'batch_results': results,
            'batch_average_score': avg_score,
            'batch_grade': batch_grade,
            'total_images': len(images),
            'message': 'Batch analysis completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Batch analysis failed: {str(e)}'}), 500

@enhanced_vision_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for enhanced vision service"""
    return jsonify({
        'service': 'enhanced_vision_analysis',
        'vision_available': VISION_AVAILABLE,
        'pytorch_available': PYTORCH_AVAILABLE if 'PYTORCH_AVAILABLE' in globals() else False,
        'status': 'healthy' if VISION_AVAILABLE else 'degraded'
    }), 200
