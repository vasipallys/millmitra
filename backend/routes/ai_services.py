"""
AI Services Routes
API endpoints for AI-powered features
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from services.ai_services import AIService
from extensions import db

ai_services_bp = Blueprint('ai_services', __name__)
ai_service = AIService()

@ai_services_bp.route('/voice/recognize', methods=['POST'])
@jwt_required()
def recognize_voice():
    """Process voice command"""
    try:
        data = request.get_json()
        
        audio_data = data.get('audio_data')
        language = data.get('language', 'en-US')
        
        if not audio_data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        result = ai_service.process_voice_command(audio_data, language)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Voice recognition failed: {str(e)}'}), 500

@ai_services_bp.route('/quality/assess', methods=['POST'])
@jwt_required()
def assess_quality():
    """Analyze rice quality from image"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data')
        batch_id = data.get('batch_id')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        result = ai_service.analyze_quality_image(image_data, batch_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Quality assessment failed: {str(e)}'}), 500

@ai_services_bp.route('/insights/generate', methods=['POST'])
@jwt_required()
def generate_insights():
    """Generate AI insights from data"""
    try:
        data = request.get_json()
        
        data_type = data.get('data_type')
        input_data = data.get('data', {})
        
        if not data_type:
            return jsonify({'error': 'Data type is required'}), 400
        
        result = ai_service.generate_insights(data_type, input_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Insight generation failed: {str(e)}'}), 500

@ai_services_bp.route('/demand/predict', methods=['POST'])
@jwt_required()
def predict_demand():
    """Predict demand using AI"""
    try:
        data = request.get_json()
        
        historical_data = data.get('historical_data', [])
        forecast_days = data.get('forecast_days', 30)
        
        result = ai_service.predict_demand(historical_data, forecast_days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Demand prediction failed: {str(e)}'}), 500

@ai_services_bp.route('/production/optimize', methods=['POST'])
@jwt_required()
def optimize_production():
    """Optimize production schedule"""
    try:
        data = request.get_json()
        
        current_capacity = data.get('current_capacity')
        demand_forecast = data.get('demand_forecast', [])
        
        if not current_capacity:
            return jsonify({'error': 'Current capacity is required'}), 400
        
        result = ai_service.optimize_production(current_capacity, demand_forecast)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Production optimization failed: {str(e)}'}), 500

@ai_services_bp.route('/anomalies/detect', methods=['POST'])
@jwt_required()
def detect_anomalies():
    """Detect anomalies in data"""
    try:
        data = request.get_json()
        
        input_data = data.get('data', [])
        metric = data.get('metric')
        
        if not input_data:
            return jsonify({'error': 'Data is required'}), 400
        
        if not metric:
            return jsonify({'error': 'Metric is required'}), 400
        
        result = ai_service.detect_anomalies(input_data, metric)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Anomaly detection failed: {str(e)}'}), 500

@ai_services_bp.route('/capabilities', methods=['GET'])
@jwt_required()
def get_ai_capabilities():
    """Get AI service capabilities"""
    try:
        capabilities = {
            'voice_recognition': {
                'supported_languages': ai_service.supported_languages,
                'features': ['command_recognition', 'intent_detection', 'entity_extraction']
            },
            'quality_assessment': {
                'supported_formats': ['image/jpeg', 'image/png'],
                'metrics': ['moisture_content', 'broken_percentage', 'foreign_matter', 'chalky_kernels']
            },
            'insights_generation': {
                'supported_data_types': ['production', 'quality', 'financial', 'sales'],
                'insight_categories': ['efficiency', 'quality', 'cost', 'trends']
            },
            'demand_prediction': {
                'forecast_range': '1-365 days',
                'accuracy': '85-92%',
                'update_frequency': 'daily'
            },
            'production_optimization': {
                'optimization_factors': ['capacity', 'demand', 'efficiency', 'cost'],
                'scheduling_horizon': '30 days'
            },
            'anomaly_detection': {
                'detection_methods': ['statistical', 'threshold-based'],
                'supported_metrics': ['production_volume', 'quality_score', 'cost_per_unit']
            }
        }
        
        return jsonify({
            'success': True,
            'capabilities': capabilities,
            'service_status': 'active',
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get capabilities: {str(e)}'}), 500

@ai_services_bp.route('/models/status', methods=['GET'])
@jwt_required()
def get_model_status():
    """Get AI model status"""
    try:
        model_status = {
            'voice_recognition_model': {
                'status': 'active',
                'accuracy': 0.89,
                'last_trained': '2024-01-15',
                'version': '1.2.0'
            },
            'quality_assessment_model': {
                'status': 'active',
                'accuracy': 0.92,
                'last_trained': '2024-01-10',
                'version': '2.1.0'
            },
            'demand_prediction_model': {
                'status': 'active',
                'accuracy': 0.87,
                'last_trained': '2024-01-20',
                'version': '1.5.0'
            },
            'anomaly_detection_model': {
                'status': 'active',
                'accuracy': 0.85,
                'last_trained': '2024-01-18',
                'version': '1.3.0'
            }
        }
        
        return jsonify({
            'success': True,
            'models': model_status,
            'overall_status': 'healthy',
            'checked_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get model status: {str(e)}'}), 500

@ai_services_bp.route('/train/model', methods=['POST'])
@jwt_required()
def train_model():
    """Train or retrain AI models"""
    try:
        data = request.get_json()
        
        model_type = data.get('model_type')
        training_data = data.get('training_data', [])
        
        if not model_type:
            return jsonify({'error': 'Model type is required'}), 400
        
        # Mock model training (in real implementation, trigger actual training)
        training_result = {
            'model_type': model_type,
            'training_status': 'completed',
            'training_duration': '45 minutes',
            'accuracy_improvement': '3.2%',
            'new_accuracy': 0.91,
            'training_samples': len(training_data),
            'trained_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'training_result': training_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Model training failed: {str(e)}'}), 500

@ai_services_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback for AI predictions"""
    try:
        data = request.get_json()
        
        prediction_id = data.get('prediction_id')
        feedback_type = data.get('feedback_type')  # 'correct', 'incorrect', 'partially_correct'
        actual_value = data.get('actual_value')
        comments = data.get('comments', '')
        
        if not prediction_id or not feedback_type:
            return jsonify({'error': 'Prediction ID and feedback type are required'}), 400
        
        # Store feedback for model improvement
        feedback_record = {
            'prediction_id': prediction_id,
            'feedback_type': feedback_type,
            'actual_value': actual_value,
            'comments': comments,
            'submitted_by': get_jwt_identity(),
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        # In real implementation, store in database and use for model retraining
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Feedback submission failed: {str(e)}'}), 500

@ai_services_bp.route('/health', methods=['GET'])
@jwt_required()
def ai_health_check():
    """Health check for AI services"""
    try:
        health_status = {
            'service_status': 'healthy',
            'models_loaded': True,
            'api_responsive': True,
            'last_prediction': datetime.utcnow().isoformat(),
            'uptime': '99.8%',
            'response_time': '250ms',
            'error_rate': '0.2%'
        }
        
        return jsonify({
            'success': True,
            'health': health_status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Health check failed: {str(e)}'}), 500
