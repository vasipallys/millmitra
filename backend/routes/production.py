from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.production import ProductionBatch, QualityTest, ProductionStep, ProductionSchedule, MaintenanceLog
from models.inventory import PaddyStock, ProductStock
from models.user import User
from services.production_service import ProductionService
from services.ai_production_service import AIProductionService
from extensions import db
from datetime import datetime, timedelta
import json

production_bp = Blueprint('production', __name__)
production_service = ProductionService()
ai_production = AIProductionService()

@production_bp.route('/batches', methods=['GET'])
@jwt_required()
def get_batches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    variety = request.args.get('variety')
    
    query = ProductionBatch.query
    
    if status:
        query = query.filter(ProductionBatch.status == status)
    if variety:
        query = query.filter(ProductionBatch.paddy_variety == variety)
    
    batches = query.order_by(ProductionBatch.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'batches': [batch.to_dict() for batch in batches.items],
        'total': batches.total,
        'pages': batches.pages,
        'current_page': page
    })

@production_bp.route('/batches', methods=['POST'])
@jwt_required()
def create_batch():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI optimization for batch parameters
    optimized_params = ai_production.optimize_batch_parameters(data)
    
    # Merge AI recommendations with user data
    batch_data = {**data, **optimized_params.get('optimized_parameters', {})}
    
    batch = production_service.create_batch(user, batch_data)
    
    return jsonify({
        'success': True,
        'batch': batch.to_dict(),
        'ai_recommendations': optimized_params.get('recommendations', [])
    }), 201

@production_bp.route('/batches/<int:batch_id>', methods=['GET'])
@jwt_required()
def get_batch_details(batch_id):
    batch = ProductionBatch.query.get_or_404(batch_id)
    
    # Get batch steps
    steps = ProductionStep.query.filter(
        ProductionStep.batch_id == batch_id
    ).order_by(ProductionStep.step_order).all()
    
    # Get quality tests
    quality_tests = QualityTest.query.filter(
        QualityTest.batch_id == batch_id
    ).order_by(QualityTest.test_date.desc()).all()
    
    # AI insights for the batch
    ai_insights = ai_production.get_batch_insights(batch)
    
    return jsonify({
        'batch': batch.to_dict(),
        'steps': [step.to_dict() for step in steps],
        'quality_tests': [test.to_dict() for test in quality_tests],
        'ai_insights': ai_insights
    })

@production_bp.route('/batches/<int:batch_id>/start', methods=['POST'])
@jwt_required()
def start_batch(batch_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    batch = ProductionBatch.query.get_or_404(batch_id)
    
    # AI pre-start checks
    pre_checks = ai_production.perform_pre_start_checks(batch)
    
    if not pre_checks['can_start']:
        return jsonify({
            'success': False,
            'message': 'Pre-start checks failed',
            'issues': pre_checks['issues']
        }), 400
    
    result = production_service.start_batch(batch, user)
    
    return jsonify(result)

@production_bp.route('/batches/<int:batch_id>/complete', methods=['POST'])
@jwt_required()
def complete_batch(batch_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    batch = ProductionBatch.query.get_or_404(batch_id)
    data = request.get_json()
    
    # AI quality prediction before completion
    quality_prediction = ai_production.predict_final_quality(batch, data)
    
    result = production_service.complete_batch(batch, user, data)
    
    return jsonify({
        **result,
        'quality_prediction': quality_prediction
    })

@production_bp.route('/batches/<int:batch_id>/steps', methods=['POST'])
@jwt_required()
def add_production_step():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    batch_id = request.view_args['batch_id']
    batch = ProductionBatch.query.get_or_404(batch_id)
    
    data = request.get_json()
    
    # AI step optimization
    optimized_step = ai_production.optimize_step_parameters(batch, data)
    
    step = production_service.add_production_step(batch, user, optimized_step)
    
    return jsonify({
        'success': True,
        'step': step.to_dict(),
        'ai_recommendations': optimized_step.get('recommendations', [])
    })

@production_bp.route('/quality-tests', methods=['POST'])
@jwt_required()
def create_quality_test():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    batch_id = data.get('batch_id')
    
    batch = ProductionBatch.query.get_or_404(batch_id)
    
    # AI quality analysis
    ai_analysis = ai_production.analyze_quality_parameters(data)
    
    quality_test = production_service.create_quality_test(batch, user, data, ai_analysis)
    
    return jsonify({
        'success': True,
        'quality_test': quality_test.to_dict(),
        'ai_analysis': ai_analysis
    })

@production_bp.route('/quality-tests', methods=['GET'])
@jwt_required()
def get_quality_tests():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    batch_id = request.args.get('batch_id', type=int)
    test_type = request.args.get('test_type')
    
    query = QualityTest.query
    
    if batch_id:
        query = query.filter(QualityTest.batch_id == batch_id)
    if test_type:
        query = query.filter(QualityTest.test_type == test_type)
    
    tests = query.order_by(QualityTest.test_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'quality_tests': [test.to_dict() for test in tests.items],
        'total': tests.total,
        'pages': tests.pages,
        'current_page': page
    })

@production_bp.route('/current-status', methods=['GET'])
@jwt_required()
def get_current_status():
    user_id = get_jwt_identity()
    
    status = production_service.get_current_production_status()
    
    # AI real-time insights
    ai_insights = ai_production.get_real_time_insights(status)
    
    return jsonify({
        'status': status,
        'ai_insights': ai_insights
    })

@production_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_production_schedules():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    shift = request.args.get('shift')
    
    query = ProductionSchedule.query
    
    if start_date:
        query = query.filter(ProductionSchedule.schedule_date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(ProductionSchedule.schedule_date <= datetime.fromisoformat(end_date).date())
    if shift:
        query = query.filter(ProductionSchedule.shift == shift)
    
    schedules = query.order_by(ProductionSchedule.schedule_date.desc()).all()
    
    return jsonify({
        'schedules': [schedule.to_dict() for schedule in schedules]
    })

@production_bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_production_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI schedule optimization
    optimized_schedule = ai_production.optimize_production_schedule(data)
    
    schedule_data = {**data, **optimized_schedule.get('optimized_parameters', {})}
    schedule = production_service.create_production_schedule(user, schedule_data)
    
    return jsonify({
        'success': True,
        'schedule': schedule.to_dict(),
        'optimization': optimized_schedule
    }), 201

@production_bp.route('/optimize', methods=['POST'])
@jwt_required()
def optimize_production():
    user_id = get_jwt_identity()
    
    data = request.get_json()
    optimization_type = data.get('type', 'efficiency')
    
    # AI-powered production optimization
    optimization = ai_production.optimize_production_schedule(data, optimization_type)
    
    return jsonify(optimization)

@production_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_production_analytics():
    user_id = get_jwt_identity()
    
    days = request.args.get('days', 30, type=int)
    analytics = production_service.get_production_analytics(days)
    
    # AI-enhanced analytics
    ai_analytics = ai_production.enhance_analytics(analytics)
    
    return jsonify({
        'analytics': analytics,
        'ai_insights': ai_analytics
    })

@production_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_ai_recommendations():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get AI recommendations based on current state
    recommendations = ai_production.get_production_recommendations(user)
    
    return jsonify({'recommendations': recommendations})

@production_bp.route('/maintenance', methods=['GET'])
@jwt_required()
def get_maintenance_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    machine_id = request.args.get('machine_id')
    maintenance_type = request.args.get('maintenance_type')
    
    query = MaintenanceLog.query
    
    if machine_id:
        query = query.filter(MaintenanceLog.machine_id == machine_id)
    if maintenance_type:
        query = query.filter(MaintenanceLog.maintenance_type == maintenance_type)
    
    logs = query.order_by(MaintenanceLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'maintenance_logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })

@production_bp.route('/maintenance', methods=['POST'])
@jwt_required()
def log_maintenance():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI maintenance prediction
    ai_prediction = ai_production.predict_maintenance_needs(data)
    
    maintenance_data = {**data, **ai_prediction}
    maintenance = production_service.log_maintenance(user, maintenance_data)
    
    return jsonify({
        'success': True,
        'maintenance': maintenance.to_dict(),
        'ai_prediction': ai_prediction
    }), 201

@production_bp.route('/maintenance/predictions', methods=['GET'])
@jwt_required()
def get_maintenance_predictions():
    # AI-powered predictive maintenance
    predictions = ai_production.get_predictive_maintenance_schedule()
    
    return jsonify({'predictions': predictions})

@production_bp.route('/efficiency/analysis', methods=['GET'])
@jwt_required()
def get_efficiency_analysis():
    days = request.args.get('days', 30, type=int)
    variety = request.args.get('variety')
    
    # AI efficiency analysis
    analysis = ai_production.analyze_production_efficiency(days, variety)
    
    return jsonify(analysis)

@production_bp.route('/batches/<int:batch_id>/pause', methods=['POST'])
@jwt_required()
def pause_batch(batch_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    batch = ProductionBatch.query.get_or_404(batch_id)
    data = request.get_json()
    
    if batch.status != 'in_progress':
        return jsonify({
            'success': False,
            'message': 'Batch is not in progress'
        }), 400
    
    # Pause current step
    current_step = ProductionStep.query.filter(
        ProductionStep.batch_id == batch_id,
        ProductionStep.status == 'in_progress'
    ).first()
    
    if current_step:
        current_step.status = 'paused'
        current_step.notes = f"{current_step.notes or ''}\nPaused: {data.get('reason', 'No reason provided')}"
    
    batch.status = 'paused'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Batch paused successfully',
        'batch': batch.to_dict()
    })

@production_bp.route('/batches/<int:batch_id>/resume', methods=['POST'])
@jwt_required()
def resume_batch(batch_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    batch = ProductionBatch.query.get_or_404(batch_id)
    
    if batch.status != 'paused':
        return jsonify({
            'success': False,
            'message': 'Batch is not paused'
        }), 400
    
    # Resume current step
    current_step = ProductionStep.query.filter(
        ProductionStep.batch_id == batch_id,
        ProductionStep.status == 'paused'
    ).first()
    
    if current_step:
        current_step.status = 'in_progress'
        current_step.notes = f"{current_step.notes or ''}\nResumed at {datetime.utcnow()}"
    
    batch.status = 'in_progress'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Batch resumed successfully',
        'batch': batch.to_dict()
    })

@production_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_production_dashboard():
    # Comprehensive production dashboard data
    current_status = production_service.get_current_production_status()
    analytics = production_service.get_production_analytics(7)  # Last 7 days
    ai_insights = ai_production.get_dashboard_insights()
    
    return jsonify({
        'current_status': current_status,
        'weekly_analytics': analytics,
        'ai_insights': ai_insights,
        'timestamp': datetime.utcnow().isoformat()
    })
