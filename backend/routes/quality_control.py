"""
Quality Control Routes
API endpoints for quality control and testing
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from services.quality_control_service import QualityControlService
from models import QualityTest, ProductionBatch
from extensions import db

quality_control_bp = Blueprint('quality_control', __name__)
quality_service = QualityControlService()

@quality_control_bp.route('/tests/create', methods=['POST'])
@jwt_required()
def create_quality_test():
    """Create a new quality test"""
    try:
        data = request.get_json()
        
        batch_id = data.get('batch_id')
        test_type = data.get('test_type')
        test_parameters = data.get('test_parameters', {})
        
        if not batch_id or not test_type:
            return jsonify({'error': 'Batch ID and test type are required'}), 400
        
        result = quality_service.create_quality_test(batch_id, test_type, test_parameters)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality test creation failed: {str(e)}'}), 500

@quality_control_bp.route('/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_quality_test(test_id):
    """Get quality test details"""
    try:
        result = quality_service.get_quality_test_details(test_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get quality test: {str(e)}'}), 500

@quality_control_bp.route('/tests', methods=['GET'])
@jwt_required()
def list_quality_tests():
    """List quality tests with filters"""
    try:
        # Get query parameters
        batch_id = request.args.get('batch_id')
        test_type = request.args.get('test_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        filters = {}
        if batch_id:
            filters['batch_id'] = batch_id
        if test_type:
            filters['test_type'] = test_type
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        result = quality_service.get_quality_tests(filters, limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to list quality tests: {str(e)}'}), 500

@quality_control_bp.route('/tests/<int:test_id>/update', methods=['PUT'])
@jwt_required()
def update_quality_test(test_id):
    """Update quality test results"""
    try:
        data = request.get_json()
        
        test_results = data.get('test_results', {})
        notes = data.get('notes', '')
        
        result = quality_service.update_quality_test(test_id, test_results, notes)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality test update failed: {str(e)}'}), 500

@quality_control_bp.route('/analyze/image', methods=['POST'])
@jwt_required()
def analyze_quality_image():
    """Analyze rice quality from image"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data')
        batch_id = data.get('batch_id')
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        result = quality_service.analyze_quality_image(image_data, batch_id, analysis_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Image analysis failed: {str(e)}'}), 500

@quality_control_bp.route('/standards/check', methods=['POST'])
@jwt_required()
def check_quality_standards():
    """Check quality against standards"""
    try:
        data = request.get_json()
        
        quality_metrics = data.get('quality_metrics', {})
        standard_type = data.get('standard_type', 'export')
        
        if not quality_metrics:
            return jsonify({'error': 'Quality metrics are required'}), 400
        
        result = quality_service.check_quality_standards(quality_metrics, standard_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Standards check failed: {str(e)}'}), 500

@quality_control_bp.route('/batch/<batch_id>/quality-summary', methods=['GET'])
@jwt_required()
def get_batch_quality_summary(batch_id):
    """Get quality summary for a batch"""
    try:
        result = quality_service.get_batch_quality_summary(batch_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get batch quality summary: {str(e)}'}), 500

@quality_control_bp.route('/reports/quality-trends', methods=['GET'])
@jwt_required()
def get_quality_trends():
    """Get quality trends report"""
    try:
        # Get query parameters
        period = request.args.get('period', '30')  # days
        metric = request.args.get('metric', 'overall_score')
        
        result = quality_service.generate_quality_trends_report(int(period), metric)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality trends report failed: {str(e)}'}), 500

@quality_control_bp.route('/alerts/quality', methods=['GET'])
@jwt_required()
def get_quality_alerts():
    """Get quality alerts"""
    try:
        result = quality_service.get_quality_alerts()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to get quality alerts: {str(e)}'}), 500

@quality_control_bp.route('/recommendations/generate', methods=['POST'])
@jwt_required()
def generate_quality_recommendations():
    """Generate quality improvement recommendations"""
    try:
        data = request.get_json()
        
        quality_data = data.get('quality_data', {})
        analysis_period = data.get('analysis_period', 30)
        
        result = quality_service.generate_quality_recommendations(quality_data, analysis_period)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Recommendation generation failed: {str(e)}'}), 500

@quality_control_bp.route('/calibration/equipment', methods=['POST'])
@jwt_required()
def calibrate_equipment():
    """Calibrate quality testing equipment"""
    try:
        data = request.get_json()
        
        equipment_id = data.get('equipment_id')
        calibration_type = data.get('calibration_type')
        reference_values = data.get('reference_values', {})
        
        if not equipment_id or not calibration_type:
            return jsonify({'error': 'Equipment ID and calibration type are required'}), 400
        
        result = quality_service.calibrate_equipment(equipment_id, calibration_type, reference_values)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Equipment calibration failed: {str(e)}'}), 500

@quality_control_bp.route('/export/quality-data', methods=['POST'])
@jwt_required()
def export_quality_data():
    """Export quality data"""
    try:
        data = request.get_json()
        
        export_format = data.get('format', 'csv')
        date_range = data.get('date_range', {})
        filters = data.get('filters', {})
        
        result = quality_service.export_quality_data(export_format, date_range, filters)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality data export failed: {str(e)}'}), 500

@quality_control_bp.route('/dashboard/quality', methods=['GET'])
@jwt_required()
def get_quality_dashboard():
    """Get quality control dashboard data"""
    try:
        result = quality_service.get_quality_dashboard_data()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality dashboard failed: {str(e)}'}), 500

@quality_control_bp.route('/standards/list', methods=['GET'])
@jwt_required()
def list_quality_standards():
    """List available quality standards"""
    try:
        standards = quality_service.quality_standards
        
        return jsonify({
            'success': True,
            'standards': standards,
            'standard_count': len(standards)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list standards: {str(e)}'}), 500

@quality_control_bp.route('/metrics/definitions', methods=['GET'])
@jwt_required()
def get_quality_metrics_definitions():
    """Get quality metrics definitions"""
    try:
        metrics_definitions = {
            'moisture_content': {
                'unit': 'percentage',
                'acceptable_range': [10, 14],
                'optimal_range': [11, 13],
                'description': 'Water content in rice grains'
            },
            'broken_percentage': {
                'unit': 'percentage',
                'acceptable_range': [0, 5],
                'optimal_range': [0, 3],
                'description': 'Percentage of broken rice grains'
            },
            'foreign_matter': {
                'unit': 'percentage',
                'acceptable_range': [0, 1],
                'optimal_range': [0, 0.5],
                'description': 'Non-rice material in the sample'
            },
            'chalky_kernels': {
                'unit': 'percentage',
                'acceptable_range': [0, 3],
                'optimal_range': [0, 2],
                'description': 'Percentage of chalky or opaque kernels'
            },
            'grain_length': {
                'unit': 'mm',
                'acceptable_range': [5.0, 7.0],
                'optimal_range': [5.5, 6.5],
                'description': 'Average length of rice grains'
            },
            'grain_width': {
                'unit': 'mm',
                'acceptable_range': [1.8, 2.8],
                'optimal_range': [2.0, 2.5],
                'description': 'Average width of rice grains'
            }
        }
        
        return jsonify({
            'success': True,
            'metrics_definitions': metrics_definitions
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get metrics definitions: {str(e)}'}), 500
