from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import ProductionBatch, QualityTest, PaddyStock, ProductStock, User
from extensions import db
from services.tenant_scope import tq, t_get, t_get_or_404
from datetime import datetime, timedelta
from utils import current_user, current_user_id, parse_datetime
import uuid

production_bp = Blueprint('production', __name__)


def _generate_batch_number():
    today = datetime.utcnow().strftime('%Y%m%d')
    count = tq(ProductionBatch).filter(
        ProductionBatch.batch_number.like(f'B{today}%')
    ).count() + 1
    return f'B{today}{count:03d}'


def _generate_test_id():
    return f'QT{datetime.utcnow().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}'


def _find_paddy_stock(data):
    stock_id = data.get('paddy_stock_id') or data.get('source_reference_id')
    if stock_id:
        try:
            stock = t_get(PaddyStock, int(stock_id))
            if stock:
                return stock
        except (TypeError, ValueError):
            pass

    variety = data.get('paddy_variety')
    query = tq(PaddyStock).filter(
        (PaddyStock.remaining_quantity > 0) | (PaddyStock.remaining_quantity.is_(None))
    )
    if variety:
        query = query.filter(PaddyStock.variety.ilike(f'%{variety}%'))
    return query.order_by(PaddyStock.purchase_date.asc()).first()


def _parse_quantity(data):
    raw = data.get('paddy_input_quantity', data.get('input_quantity', 0))
    try:
        return float(raw or 0)
    except (TypeError, ValueError):
        return 0.0


def _empty_analytics(days=30):
    return {
        'days': days,
        'total_batches': 0,
        'completed_batches': 0,
        'total_input': 0,
        'total_output': 0,
        'average_yield': 0,
        'average_efficiency': 0,
        'daily_production': []
    }


@production_bp.route('/batches', methods=['GET'])
@jwt_required()
def get_batches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    variety = request.args.get('variety')

    query = tq(ProductionBatch)

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
    user = current_user()
    data = request.get_json() or {}

    quantity = _parse_quantity(data)
    if quantity <= 0:
        return jsonify({'success': False, 'message': 'Input quantity must be greater than 0'}), 400

    paddy_stock = _find_paddy_stock(data)
    if not paddy_stock:
        return jsonify({
            'success': False,
            'message': 'No available paddy stock found. Add paddy inventory before creating a batch.'
        }), 400

    available = paddy_stock.remaining_quantity if paddy_stock.remaining_quantity is not None else paddy_stock.quantity
    if quantity > available:
        return jsonify({
            'success': False,
            'message': f'Requested {quantity} kg exceeds available stock ({available} kg)'
        }), 400

    start_time = parse_datetime(data.get('planned_start_time') or data.get('start_time'), datetime.utcnow())

    batch = ProductionBatch(
        batch_number=_generate_batch_number(),
        paddy_stock_id=paddy_stock.id,
        start_time=start_time,
        machine_id=data.get('machine_id'),
        operator_id=user.id if user else None,
        shift=data.get('shift'),
        paddy_input_quantity=quantity,
        paddy_variety=data.get('paddy_variety') or paddy_stock.variety,
        paddy_quality_grade=data.get('quality_grade') or data.get('paddy_quality_grade') or paddy_stock.quality_grade,
        status='planned',
        completion_percentage=0.0,
        created_by=user.id if user else None
    )
    if data.get('machine_settings'):
        batch.set_machine_settings(data.get('machine_settings'))
    if data.get('notes') or data.get('special_instructions'):
        batch.set_optimization_suggestions([data.get('notes') or data.get('special_instructions')])

    db.session.add(batch)
    db.session.commit()

    return jsonify({
        'success': True,
        'batch': batch.to_dict(),
        'ai_recommendations': [
            f'Use FIFO stock {paddy_stock.stock_id} ({paddy_stock.variety})',
            'Typical rice yield for this variety is about 65-70%'
        ]
    }), 201


@production_bp.route('/batches/<int:batch_id>', methods=['GET'])
@jwt_required()
def get_batch_details(batch_id):
    batch = t_get_or_404(ProductionBatch, batch_id)

    quality_tests = tq(QualityTest).filter(
        QualityTest.batch_id == batch_id
    ).order_by(QualityTest.test_date.desc()).all()

    return jsonify({
        'batch': batch.to_dict(),
        'steps': [],
        'quality_tests': [test.to_dict() for test in quality_tests],
        'ai_insights': batch.analyze_performance()
    })


@production_bp.route('/batches/<int:batch_id>/start', methods=['POST'])
@jwt_required()
def start_batch(batch_id):
    user = current_user()
    batch = t_get_or_404(ProductionBatch, batch_id)

    if batch.status not in ('planned', 'paused'):
        return jsonify({
            'success': False,
            'message': f'Batch cannot be started from status "{batch.status}"'
        }), 400

    paddy_stock = t_get(PaddyStock, batch.paddy_stock_id)
    if paddy_stock:
        available = paddy_stock.remaining_quantity if paddy_stock.remaining_quantity is not None else paddy_stock.quantity
        if batch.paddy_input_quantity > available and batch.status == 'planned':
            return jsonify({
                'success': False,
                'message': 'Insufficient paddy stock remaining to start this batch'
            }), 400
        if batch.status == 'planned':
            paddy_stock.remaining_quantity = available - batch.paddy_input_quantity
            paddy_stock.processed_quantity = (paddy_stock.processed_quantity or 0) + batch.paddy_input_quantity
            paddy_stock.status = 'processed' if paddy_stock.remaining_quantity <= 0 else 'processing'

    batch.status = 'in_progress'
    batch.start_time = datetime.utcnow()
    if user:
        batch.operator_id = user.id
    db.session.commit()
    from services.notification_service import batch_started
    batch_started(batch)

    return jsonify({
        'success': True,
        'message': 'Batch started successfully',
        'batch': batch.to_dict()
    })


@production_bp.route('/batches/<int:batch_id>/complete', methods=['POST'])
@jwt_required()
def complete_batch(batch_id):
    user = current_user()
    batch = t_get_or_404(ProductionBatch, batch_id)
    data = request.get_json() or {}

    if batch.status not in ('in_progress', 'paused', 'started'):
        return jsonify({
            'success': False,
            'message': 'Batch is not in progress'
        }), 400

    rice_output = float(data.get('rice_output', data.get('output_quantity', 0)) or 0)
    broken = float(data.get('broken_rice_output', data.get('waste_quantity', 0)) or 0)
    bran = float(data.get('bran_output', data.get('byproduct_quantity', 0)) or 0)
    husk = float(data.get('husk_output', 0) or 0)

    batch.rice_output = rice_output
    batch.broken_rice_output = broken
    batch.bran_output = bran
    batch.husk_output = husk
    batch.update_totals()
    batch.status = 'completed'
    batch.end_time = datetime.utcnow()
    batch.completion_percentage = 100.0
    if user:
        batch.operator_id = batch.operator_id or user.id

    if rice_output > 0:
        product = tq(ProductStock).filter_by(
            product_type='rice',
            variety=batch.paddy_variety,
            grade=batch.output_quality_grade or batch.paddy_quality_grade or 'A'
        ).first()
        if product:
            product.quantity = (product.quantity or 0) + rice_output
        else:
            product = ProductStock(
                product_id=f'PRD{datetime.utcnow().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}',
                product_name=f'{batch.paddy_variety or "Rice"} milled',
                product_type='rice',
                variety=batch.paddy_variety,
                grade=batch.output_quality_grade or batch.paddy_quality_grade or 'A',
                quantity=rice_output,
                warehouse_id='WH001',
                production_date=datetime.utcnow(),
                created_by=user.id if user else None
            )
            db.session.add(product)

    db.session.commit()
    from services.notification_service import batch_completed
    batch_completed(batch)

    return jsonify({
        'success': True,
        'message': 'Batch completed successfully',
        'batch': batch.to_dict(),
        'quality_prediction': {
            'expected_grade': batch.paddy_quality_grade or 'A',
            'yield_percentage': batch.yield_percentage
        }
    })


@production_bp.route('/batches/<int:batch_id>/steps', methods=['POST'])
@jwt_required()
def add_production_step(batch_id):
    batch = t_get_or_404(ProductionBatch, batch_id)
    data = request.get_json() or {}
    notes = data.get('notes') or data.get('step_name') or 'Step recorded'
    flags = batch.get_anomaly_flags() or []
    flags.append({
        'step': data.get('step_name', 'process'),
        'notes': notes,
        'at': datetime.utcnow().isoformat()
    })
    batch.set_anomaly_flags(flags)
    if data.get('completion_percentage') is not None:
        batch.completion_percentage = float(data.get('completion_percentage'))
    db.session.commit()

    return jsonify({
        'success': True,
        'step': {
            'batch_id': batch.id,
            'step_name': data.get('step_name', 'process'),
            'status': 'recorded',
            'notes': notes
        },
        'ai_recommendations': []
    })


@production_bp.route('/quality-tests', methods=['POST'])
@jwt_required()
def create_quality_test():
    user = current_user()
    data = request.get_json() or {}
    batch_id = data.get('batch_id') or data.get('batchId')
    params = data.get('test_parameters') or data

    if not batch_id:
        return jsonify({'success': False, 'message': 'batch_id is required'}), 400

    batch = t_get_or_404(ProductionBatch, int(batch_id))

    moisture = params.get('moisture_content')
    broken = params.get('broken_percentage')
    foreign = params.get('foreign_matter')
    chalky = params.get('chalky_percentage', params.get('chalky_kernels'))

    test = QualityTest(
        test_id=_generate_test_id(),
        batch_id=batch.id,
        sample_type=data.get('sample_type', data.get('test_type', 'output_rice')),
        test_date=datetime.utcnow(),
        tested_by=user.id if user else None,
        test_method=data.get('test_method', 'manual'),
        moisture_content=float(moisture) if moisture not in (None, '') else None,
        foreign_matter=float(foreign) if foreign not in (None, '') else None,
        broken_percentage=float(broken) if broken not in (None, '') else None,
        chalky_percentage=float(chalky) if chalky not in (None, '') else None,
        grain_length=float(params['grain_length']) if params.get('grain_length') else None,
        grain_width=float(params['grain_width']) if params.get('grain_width') else None,
        created_by=user.id if user else None
    )
    test.grade = test.determine_grade()
    test.grade_confidence = test.calculate_quality_score()
    db.session.add(test)

    batch.output_quality_grade = test.grade
    batch.moisture_content_output = test.moisture_content
    batch.broken_percentage_output = test.broken_percentage
    db.session.commit()

    return jsonify({
        'success': True,
        'quality_test': test.to_dict(),
        'ai_analysis': {
            'grade': test.grade,
            'quality_score': test.grade_confidence,
            'recommendations': test.get_quality_recommendations()
        }
    })


@production_bp.route('/quality-tests', methods=['GET'])
@jwt_required()
def get_quality_tests():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    batch_id = request.args.get('batch_id', type=int)
    test_type = request.args.get('test_type')

    query = tq(QualityTest)

    if batch_id:
        query = query.filter(QualityTest.batch_id == batch_id)
    if test_type:
        query = query.filter(
            (QualityTest.sample_type == test_type) | (QualityTest.test_method == test_type)
        )

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
    active_batches = tq(ProductionBatch).filter(
        ProductionBatch.status.in_(['in_progress', 'started', 'paused'])
    ).all()
    planned_batches = tq(ProductionBatch).filter(ProductionBatch.status == 'planned').all()
    recent_batches = tq(ProductionBatch).order_by(
        ProductionBatch.created_at.desc()
    ).limit(12).all()

    machines = {b.machine_id for b in active_batches if b.machine_id}

    payload = {
        'active_batches': len(active_batches) + len(planned_batches),
        'in_progress': len(active_batches),
        'planned': len(planned_batches),
        'machines_in_use': len(machines),
        'batches': [batch.to_dict() for batch in recent_batches if batch.status in ('in_progress', 'started', 'paused', 'planned')],
        'recent_batches': [batch.to_dict() for batch in recent_batches],
        'total_output_today': sum(batch.total_output or 0 for batch in active_batches),
        'status': 'operational'
    }

    return jsonify({
        **payload,
        'status_detail': payload,
        'ai_insights': {
            'efficiency': 'Good',
            'recommendations': ['Monitor active batches', 'Maintain quality standards'],
            'alerts': []
        }
    })


@production_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_production_schedules():
    planned = tq(ProductionBatch).filter(
        ProductionBatch.status == 'planned'
    ).order_by(ProductionBatch.start_time.asc()).all()
    return jsonify({
        'schedules': [
            {
                'id': batch.id,
                'batch_number': batch.batch_number,
                'schedule_date': batch.start_time.date().isoformat() if batch.start_time else None,
                'shift': batch.shift,
                'variety': batch.paddy_variety,
                'quantity': batch.paddy_input_quantity,
                'status': batch.status
            }
            for batch in planned
        ]
    })


@production_bp.route('/schedules', methods=['POST'])
@jwt_required()
def create_production_schedule():
    return create_batch()


@production_bp.route('/optimize', methods=['POST'])
@jwt_required()
def optimize_production():
    data = request.get_json() or {}
    quantity = _parse_quantity(data) or 1000
    return jsonify({
        'success': True,
        'type': data.get('type', 'efficiency'),
        'optimized_parameters': {
            'recommended_batch_size': min(max(quantity, 200), 5000),
            'expected_yield_percentage': 67.0,
            'estimated_hours': round(quantity / 250, 1) if quantity else 4
        },
        'recommendations': [
            'Process higher-moisture paddy first to reduce storage risk',
            'Keep milling moisture near 14% for better head rice yield'
        ]
    })


@production_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_production_analytics():
    days = request.args.get('days', 30, type=int)
    start = datetime.utcnow() - timedelta(days=days)
    batches = tq(ProductionBatch).filter(ProductionBatch.start_time >= start).all()
    completed = [b for b in batches if b.status == 'completed']

    total_input = sum(b.paddy_input_quantity or 0 for b in completed)
    total_output = sum(b.total_output or 0 for b in completed)
    avg_yield = (
        sum(b.yield_percentage or 0 for b in completed) / len(completed)
        if completed else 0
    )
    avg_eff = (
        sum(b.efficiency_percentage or 0 for b in completed) / len(completed)
        if completed else 0
    )

    analytics = {
        'days': days,
        'total_batches': len(batches),
        'completed_batches': len(completed),
        'total_input': total_input,
        'total_output': total_output,
        'average_yield': avg_yield,
        'average_efficiency': avg_eff,
        'daily_production': []
    }

    return jsonify({
        'analytics': analytics,
        'ai_insights': {
            'summary': f'{len(completed)} batches completed in the last {days} days',
            'yield': avg_yield
        }
    })


@production_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_ai_recommendations():
    active_batches = tq(ProductionBatch).filter(
        ProductionBatch.status.in_(['in_progress', 'started'])
    ).count()

    recent_quality = tq(QualityTest).order_by(
        QualityTest.test_date.desc()
    ).limit(5).all()
    avg_quality = (
        sum(test.grade_confidence or 0 for test in recent_quality) / len(recent_quality)
        if recent_quality else 0
    )

    recommendations = [
        'Monitor active batch progress',
        'Maintain optimal processing moisture',
        'Schedule quality checks at cleaning and milling stages'
    ]
    if avg_quality:
        recommendations.append(f'Current quality average: {avg_quality:.1f}%')

    return jsonify({
        'recommendations': recommendations,
        'priority': 'medium',
        'active_batches': active_batches
    })


@production_bp.route('/ai/recommendations', methods=['POST'])
@jwt_required()
def post_ai_recommendations():
    data = request.get_json() or {}
    variety = data.get('paddy_variety', 'paddy')
    quantity = _parse_quantity(data) or 1000
    return jsonify({
        'recommendations': [
            f'Expected yield for {variety}: ~67%',
            f'Plan about {round(quantity / 250, 1)} milling hours for {quantity} kg'
        ],
        'optimized_settings': {
            'cleaning': {'air_flow': 'medium'},
            'milling': {'pressure': 'standard'}
        }
    })


@production_bp.route('/maintenance', methods=['GET'])
@jwt_required()
def get_maintenance_logs():
    return jsonify({
        'maintenance_logs': [],
        'total': 0,
        'pages': 0,
        'current_page': 1
    })


@production_bp.route('/maintenance', methods=['POST'])
@jwt_required()
def log_maintenance():
    data = request.get_json() or {}
    return jsonify({
        'success': True,
        'maintenance': {
            'id': None,
            'machine_id': data.get('machine_id'),
            'notes': data.get('notes'),
            'status': 'recorded'
        },
        'ai_prediction': {'next_service_days': 30}
    }), 201


@production_bp.route('/maintenance/predictions', methods=['GET'])
@jwt_required()
def get_maintenance_predictions():
    return jsonify({'predictions': []})


@production_bp.route('/efficiency/analysis', methods=['GET'])
@jwt_required()
def get_efficiency_analysis():
    days = request.args.get('days', 30, type=int)
    start = datetime.utcnow() - timedelta(days=days)
    completed = tq(ProductionBatch).filter(
        ProductionBatch.start_time >= start,
        ProductionBatch.status == 'completed'
    ).all()
    avg_eff = (
        sum(b.efficiency_percentage or 0 for b in completed) / len(completed)
        if completed else 0
    )
    return jsonify({
        'days': days,
        'average_efficiency': avg_eff,
        'batch_count': len(completed)
    })


@production_bp.route('/batches/<int:batch_id>/pause', methods=['POST'])
@jwt_required()
def pause_batch(batch_id):
    batch = t_get_or_404(ProductionBatch, batch_id)
    data = request.get_json() or {}

    if batch.status != 'in_progress':
        return jsonify({
            'success': False,
            'message': 'Batch is not in progress'
        }), 400

    batch.status = 'paused'
    flags = batch.get_anomaly_flags() or []
    flags.append({'event': 'paused', 'reason': data.get('reason', 'No reason provided')})
    batch.set_anomaly_flags(flags)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Batch paused successfully',
        'batch': batch.to_dict()
    })


@production_bp.route('/batches/<int:batch_id>/resume', methods=['POST'])
@jwt_required()
def resume_batch(batch_id):
    batch = t_get_or_404(ProductionBatch, batch_id)

    if batch.status != 'paused':
        return jsonify({
            'success': False,
            'message': 'Batch is not paused'
        }), 400

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
    active = tq(ProductionBatch).filter(
        ProductionBatch.status.in_(['in_progress', 'started', 'paused', 'planned'])
    ).all()
    week_start = datetime.utcnow() - timedelta(days=7)
    weekly = tq(ProductionBatch).filter(ProductionBatch.start_time >= week_start).all()
    completed = [b for b in weekly if b.status == 'completed']

    daily = {}
    for batch in weekly:
        if not batch.start_time:
            continue
        day = batch.start_time.date().isoformat()
        daily.setdefault(day, {'date': day, 'output': 0, 'efficiency': 0, 'count': 0})
        daily[day]['output'] += batch.total_output or 0
        daily[day]['efficiency'] += batch.efficiency_percentage or 0
        daily[day]['count'] += 1
    daily_production = []
    for item in daily.values():
        if item['count']:
            item['efficiency'] = item['efficiency'] / item['count']
        daily_production.append(item)

    current_status = {
        'active_batches': [b.to_dict() for b in active],
        'active_count': len(active),
        'in_progress': len([b for b in active if b.status in ('in_progress', 'started')])
    }
    weekly_analytics = {
        'daily_production': daily_production or [{'date': datetime.utcnow().date().isoformat(), 'output': 0, 'efficiency': 0}],
        'completed_batches': len(completed),
        'total_output': sum(b.total_output or 0 for b in completed)
    }

    return jsonify({
        'current_status': current_status,
        'weekly_analytics': weekly_analytics,
        'ai_insights': {'message': 'Production dashboard loaded'},
        'timestamp': datetime.utcnow().isoformat()
    })
