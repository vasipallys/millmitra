from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import uuid

class ProductionBatch(db.Model):
    __tablename__ = 'production_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Input details
    paddy_variety = db.Column(db.String(50), nullable=False)
    input_quantity = db.Column(db.Float, nullable=False)  # in quintals
    input_source = db.Column(db.String(20), default='procurement')  # procurement, inventory
    source_reference_id = db.Column(db.Integer)  # procurement_id or stock_id
    
    # Production planning
    planned_start_time = db.Column(db.DateTime)
    planned_end_time = db.Column(db.DateTime)
    planned_output_quantity = db.Column(db.Float)
    target_rice_variety = db.Column(db.String(50))
    
    # Machine settings (AI optimized)
    machine_settings = db.Column(JSON)
    
    # Actual production
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    output_quantity = db.Column(db.Float)  # actual output
    waste_quantity = db.Column(db.Float, default=0)
    byproduct_quantity = db.Column(db.Float, default=0)  # husk, bran
    
    # Quality and efficiency
    efficiency_score = db.Column(db.Float)  # AI calculated
    quality_grade = db.Column(db.String(5))
    yield_percentage = db.Column(db.Float)
    
    # Status and tracking
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, cancelled
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    
    # Personnel
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    started_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Notes and observations
    production_notes = db.Column(db.Text)
    completion_notes = db.Column(db.Text)
    ai_recommendations = db.Column(JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('ProductionStep', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    quality_tests = db.relationship('QualityTest', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.batch_number:
            self.batch_number = self._generate_batch_number()
    
    def _generate_batch_number(self):
        prefix = f"B{datetime.now().strftime('%Y%m')}"
        count = ProductionBatch.query.filter(
            ProductionBatch.batch_number.like(f"{prefix}%")
        ).count() + 1
        return f"{prefix}{count:04d}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_number': self.batch_number,
            'paddy_variety': self.paddy_variety,
            'input_quantity': self.input_quantity,
            'output_quantity': self.output_quantity,
            'waste_quantity': self.waste_quantity,
            'efficiency_score': self.efficiency_score,
            'quality_grade': self.quality_grade,
            'yield_percentage': self.yield_percentage,
            'status': self.status,
            'priority': self.priority,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat(),
            'machine_settings': self.machine_settings,
            'ai_recommendations': self.ai_recommendations
        }

class ProductionStep(db.Model):
    __tablename__ = 'production_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), nullable=False)
    
    # Step details
    step_name = db.Column(db.String(50), nullable=False)  # cleaning, dehusking, polishing, sorting
    step_order = db.Column(db.Integer, default=1)
    
    # Timing
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    expected_duration = db.Column(db.Integer)  # minutes
    actual_duration = db.Column(db.Integer)  # calculated
    
    # Parameters and settings
    parameters = db.Column(JSON)  # step-specific parameters
    machine_id = db.Column(db.String(50))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Quality and output
    input_quantity = db.Column(db.Float)
    output_quantity = db.Column(db.Float)
    waste_quantity = db.Column(db.Float, default=0)
    step_efficiency = db.Column(db.Float)
    
    # Status and notes
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    notes = db.Column(db.Text)
    issues = db.Column(JSON)  # any issues encountered
    
    # AI insights
    ai_optimization = db.Column(JSON)
    performance_score = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'step_name': self.step_name,
            'step_order': self.step_order,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'expected_duration': self.expected_duration,
            'actual_duration': self.actual_duration,
            'input_quantity': self.input_quantity,
            'output_quantity': self.output_quantity,
            'step_efficiency': self.step_efficiency,
            'status': self.status,
            'parameters': self.parameters,
            'performance_score': self.performance_score
        }

class QualityTest(db.Model):
    __tablename__ = 'quality_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), nullable=False)
    test_number = db.Column(db.String(50), unique=True)
    
    # Test details
    test_type = db.Column(db.String(30), nullable=False)  # input, intermediate, final
    test_stage = db.Column(db.String(30))  # cleaning, polishing, packaging
    sample_size = db.Column(db.Float)  # kg
    
    # Quality parameters
    moisture_content = db.Column(db.Float)
    broken_grains = db.Column(db.Float)
    foreign_matter = db.Column(db.Float)
    chalky_grains = db.Column(db.Float)
    head_rice_recovery = db.Column(db.Float)
    milling_degree = db.Column(db.Float)
    
    # Color and appearance
    whiteness_index = db.Column(db.Float)
    transparency = db.Column(db.Float)
    grain_length = db.Column(db.Float)
    grain_width = db.Column(db.Float)
    
    # Overall assessment
    overall_grade = db.Column(db.String(5))  # A, B, C, D
    quality_score = db.Column(db.Float)  # 0-100
    pass_fail = db.Column(db.Boolean, default=True)
    
    # Test execution
    tested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    test_method = db.Column(db.String(20), default='manual')  # manual, automated, ai
    
    # AI analysis
    ai_analysis = db.Column(JSON)
    confidence_score = db.Column(db.Float)
    
    # Notes and recommendations
    notes = db.Column(db.Text)
    recommendations = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.test_number:
            self.test_number = self._generate_test_number()
    
    def _generate_test_number(self):
        prefix = f"QT{datetime.now().strftime('%Y%m%d')}"
        count = QualityTest.query.filter(
            QualityTest.test_number.like(f"{prefix}%")
        ).count() + 1
        return f"{prefix}{count:03d}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'test_number': self.test_number,
            'test_type': self.test_type,
            'test_stage': self.test_stage,
            'moisture_content': self.moisture_content,
            'broken_grains': self.broken_grains,
            'foreign_matter': self.foreign_matter,
            'head_rice_recovery': self.head_rice_recovery,
            'overall_grade': self.overall_grade,
            'quality_score': self.quality_score,
            'pass_fail': self.pass_fail,
            'test_date': self.test_date.isoformat(),
            'ai_analysis': self.ai_analysis,
            'confidence_score': self.confidence_score
        }

class ProductionSchedule(db.Model):
    __tablename__ = 'production_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(10), nullable=False)  # morning, afternoon, night
    
    # Capacity planning
    planned_batches = db.Column(db.Integer, default=0)
    planned_quantity = db.Column(db.Float, default=0)  # total input quantity
    available_capacity = db.Column(db.Float)  # machine capacity
    utilization_target = db.Column(db.Float, default=85)  # percentage
    
    # Resource allocation
    assigned_operators = db.Column(JSON)  # list of operator IDs
    machine_allocation = db.Column(JSON)  # machine assignments
    
    # AI optimization
    ai_optimized = db.Column(db.Boolean, default=False)
    optimization_score = db.Column(db.Float)
    efficiency_prediction = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, in_progress, completed
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_date': self.schedule_date.isoformat(),
            'shift': self.shift,
            'planned_batches': self.planned_batches,
            'planned_quantity': self.planned_quantity,
            'available_capacity': self.available_capacity,
            'utilization_target': self.utilization_target,
            'ai_optimized': self.ai_optimized,
            'optimization_score': self.optimization_score,
            'status': self.status
        }

class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50), nullable=False)
    machine_name = db.Column(db.String(100))
    
    # Maintenance details
    maintenance_type = db.Column(db.String(20), nullable=False)  # preventive, corrective, emergency
    description = db.Column(db.Text, nullable=False)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_hours = db.Column(db.Float)
    
    # Personnel and costs
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cost = db.Column(db.Float, default=0)
    parts_used = db.Column(JSON)
    
    # Status and impact
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    impact_on_production = db.Column(db.String(20))  # none, low, medium, high
    downtime_hours = db.Column(db.Float, default=0)
    
    # AI predictions
    ai_predicted = db.Column(db.Boolean, default=False)
    failure_probability = db.Column(db.Float)
    recommended_action = db.Column(db.String(100))
    
    # Notes and follow-up
    notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    next_maintenance_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
            'machine_name': self.machine_name,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'cost': self.cost,
            'downtime_hours': self.downtime_hours,
            'ai_predicted': self.ai_predicted,
            'failure_probability': self.failure_probability
        }