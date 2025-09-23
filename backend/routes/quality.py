from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.quality import QualityStandard, QualityTestTemplate, QualityInspection, QualityAlert, QualityTrend
from services.quality_service import QualityService
from ai.quality_ai import QualityAI
from extensions import db

quality_bp = Blueprint('quality', __name__)
quality_service = QualityService()
ai_quality = QualityAI()

@quality_bp.route('/standards', methods=['GET'])
@jwt_required()
def get_quality_standards():
    """Get all quality standards"""
    standards = QualityStandard.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'standards': [standard.to_dict() for standard in standards]
    })

@quality_bp.route('/standards', methods=['POST'])
@jwt_required()
def create_quality_standard():
    """Create new quality standard"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI validation of standard parameters
    validation_result = ai_quality.validate_quality_standard(data)
    
    if not validation_result.get('valid', True):
        return jsonify({
            'success': False,
            'errors': validation_result.get('errors', [])
        }), 400
    
    standard = quality_service.create_quality_standard(user, data)
    
    return jsonify({
        'success': True,
        'standard': standard.to_dict(),
        'ai_validation': validation_result
    }), 201

@quality_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_test_templates():
    """Get all test templates"""
    templates = QualityTestTemplate.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'templates': [template.to_dict() for template in templates]
    })

@quality_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_test_template():
    """Create new test template"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    template = quality_service.create_test_template(user, data)
    
    return jsonify({
        'success': True,
        'template': template.to_dict()
    }), 201

@quality_bp.route('/inspections', methods=['GET'])
@jwt_required()
def get_inspections():
    """Get quality inspections with filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    inspection_type = request.args.get('type')
    status = request.args.get('status')
    
    query = QualityInspection.query
    
    if inspection_type:
        query = query.filter_by(inspection_type=inspection_type)
    if status:
        query = query.filter_by(status=status)
    
    inspections = query.order_by(QualityInspection.inspection_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'inspections': [inspection.to_dict() for inspection in inspections.items],
        'pagination': {
            'page': page,
            'pages': inspections.pages,
            'per_page': per_page,
            'total': inspections.total
        }
    })

@quality_bp.route('/inspections', methods=['POST'])
@jwt_required()
def create_inspection():
    """Create new quality inspection"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI analysis of test results
    ai_analysis = ai_quality.analyze_quality_test(data.get('test_results', {}))
    
    # Create inspection with AI insights
    inspection = quality_service.create_inspection(user, data, ai_analysis)
    
    # Check for quality alerts
    alert_check = ai_quality.check_quality_alerts(inspection.to_dict())
    if alert_check.get('create_alert'):
        quality_service.create_quality_alert(alert_check['alert_data'])
    
    return jsonify({
        'success': True,
        'inspection': inspection.to_dict(),
        'ai_analysis': ai_analysis,
        'alert_triggered': alert_check.get('create_alert', False)
    }), 201

@quality_bp.route('/inspections/<int:inspection_id>', methods=['GET'])
@jwt_required()
def get_inspection(inspection_id):
    """Get specific inspection details"""
    inspection = QualityInspection.query.get_or_404(inspection_id)
    
    # Generate AI insights for this inspection
    ai_insights = ai_quality.generate_quality_report(inspection.to_dict())
    
    return jsonify({
        'success': True,
        'inspection': inspection.to_dict(),
        'ai_insights': ai_insights
    })

@quality_bp.route('/inspections/<int:inspection_id>/approve', methods=['POST'])
@jwt_required()
def approve_inspection(inspection_id):
    """Approve quality inspection"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    inspection = QualityInspection.query.get_or_404(inspection_id)
    data = request.get_json()
    
    result = quality_service.approve_inspection(inspection, user, data)
    
    return jsonify(result)

@quality_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_quality_alerts():
    """Get quality alerts"""
    status = request.args.get('status', 'open')
    severity = request.args.get('severity')
    
    query = QualityAlert.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(QualityAlert.created_at.desc()).limit(50).all()
    
    return jsonify({
        'success': True,
        'alerts': [alert.to_dict() for alert in alerts]
    })

@quality_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_quality_alert(alert_id):
    """Resolve quality alert"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    alert = QualityAlert.query.get_or_404(alert_id)
    data = request.get_json()
    
    result = quality_service.resolve_alert(alert, user, data)
    
    return jsonify(result)

@quality_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_quality_trends():
    """Get quality trends analysis"""
    days = request.args.get('days', 30, type=int)
    product_type = request.args.get('product_type')
    parameter = request.args.get('parameter')
    
    trends_data = quality_service.get_quality_trends(days, product_type, parameter)
    
    # AI trend analysis
    ai_trends = ai_quality.predict_quality_trends(trends_data)
    
    return jsonify({
        'success': True,
        'trends_data': trends_data,
        'ai_analysis': ai_trends
    })

@quality_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_quality_dashboard():
    """Get quality dashboard data"""
    days = request.args.get('days', 30, type=int)
    
    dashboard_data = quality_service.get_dashboard_data(days)
    
    # AI insights for dashboard
    ai_insights = ai_quality.generate_dashboard_insights(dashboard_data)
    
    return jsonify({
        'success': True,
        'dashboard': dashboard_data,
        'ai_insights': ai_insights
    })

@quality_bp.route('/equipment-health', methods=['GET'])
@jwt_required()
def check_equipment_health():
    """Check equipment health based on quality patterns"""
    days = request.args.get('days', 14, type=int)
    
    quality_data = quality_service.get_recent_quality_data(days)
    
    # AI equipment health analysis
    equipment_analysis = ai_quality.detect_equipment_issues(quality_data)
    
    return jsonify({
        'success': True,
        'equipment_health': equipment_analysis
    })

@quality_bp.route('/batch-analysis', methods=['POST'])
@jwt_required()
def analyze_batch_quality():
    """Analyze quality for a specific batch"""
    data = request.get_json()
    batch_id = data.get('batch_id')
    
    if not batch_id:
        return jsonify({
            'success': False,
            'message': 'Batch ID is required'
        }), 400
    
    # Get batch quality data
    batch_quality_data = quality_service.get_batch_quality_data(batch_id)
    
    # AI analysis
    ai_analysis = ai_quality.analyze_batch_quality(batch_quality_data)
    
    return jsonify({
        'success': True,
        'batch_analysis': ai_analysis
    })

@quality_bp.route('/compliance-report', methods=['GET'])
@jwt_required()
def generate_compliance_report():
    """Generate compliance report"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    product_type = request.args.get('product_type')
    
    compliance_data = quality_service.get_compliance_data(start_date, end_date, product_type)
    
    # AI compliance analysis
    ai_compliance = ai_quality.analyze_compliance(compliance_data)
    
    return jsonify({
        'success': True,
        'compliance_report': compliance_data,
        'ai_analysis': ai_compliance
    })

@quality_bp.route('/predict-quality', methods=['POST'])
@jwt_required()
def predict_quality():
    """Predict quality based on input parameters"""
    data = request.get_json()
    
    # AI quality prediction
    prediction = ai_quality.predict_quality_outcome(data)
    
    return jsonify({
        'success': True,
        'prediction': prediction
    })

@quality_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_quality_recommendations():
    """Get AI-powered quality recommendations"""
    context = request.args.get('context', 'general')
    
    recommendations = ai_quality.get_quality_recommendations(context)
    
    return jsonify({
        'success': True,
        'recommendations': recommendations
    })