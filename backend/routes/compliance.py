from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.compliance_service import ComplianceService

compliance_bp = Blueprint('compliance', __name__)
compliance_service = ComplianceService()

@compliance_bp.route('/assessments', methods=['POST'])
@jwt_required()
def create_assessment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    assessment = compliance_service.create_assessment(user, data)
    
    return jsonify({
        'success': True,
        'assessment': {
            'id': assessment.id,
            'name': assessment.assessment_name,
            'status': assessment.status
        }
    }), 201

@compliance_bp.route('/assessments/<int:assessment_id>/results', methods=['PUT'])
@jwt_required()
def update_assessment_results(assessment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    assessment = compliance_service.update_assessment_results(assessment_id, data, user)
    
    return jsonify({
        'success': True,
        'assessment': {
            'id': assessment.id,
            'status': assessment.status,
            'compliance_percentage': assessment.compliance_percentage
        }
    })

@compliance_bp.route('/documents', methods=['POST'])
@jwt_required()
def create_document():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    document = compliance_service.create_regulatory_document(user, data)
    
    return jsonify({
        'success': True,
        'document': {
            'id': document.id,
            'name': document.document_name,
            'type': document.document_type
        }
    }), 201

@compliance_bp.route('/action-items/<int:action_item_id>/progress', methods=['PUT'])
@jwt_required()
def update_action_progress(action_item_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    action_item = compliance_service.update_action_item_progress(action_item_id, data, user)
    
    return jsonify({
        'success': True,
        'action_item': {
            'id': action_item.id,
            'status': action_item.status,
            'progress_percentage': action_item.progress_percentage
        }
    })

@compliance_bp.route('/dashboard')
@jwt_required()
def get_compliance_dashboard():
    dashboard_data = compliance_service.get_compliance_dashboard()
    return jsonify(dashboard_data)

@compliance_bp.route('/reports/compliance')
@jwt_required()
def generate_compliance_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    framework_id = request.args.get('framework_id', type=int)
    
    report = compliance_service.generate_compliance_report(start_date, end_date, framework_id)
    return jsonify(report)

@compliance_bp.route('/alerts/check-expiring')
@jwt_required()
def check_expiring_documents():
    alerts_created = compliance_service.check_expiring_documents()
    return jsonify({
        'success': True,
        'alerts_created': alerts_created
    })