from datetime import datetime
from sqlalchemy import JSON
from backend.database import db

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Equipment identification
    equipment_code = db.Column(db.String(20), unique=True, nullable=False)
    equipment_name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)  # cleaner, dryer, mill, etc.
    category = db.Column(db.String(30), nullable=False)  # processing, handling, storage
    
    # Equipment details
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    year_manufactured = db.Column(db.Integer)
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)
    
    # Location and capacity
    location = db.Column(db.String(100))
    capacity = db.Column(db.Float)  # processing capacity
    capacity_unit = db.Column(db.String(20))  # tons/hour, kg/batch, etc.
    
    # Technical specifications
    specifications = db.Column(JSON)  # Technical specs
    operating_parameters = db.Column(JSON)  # Normal operating ranges
    
    # Status and condition
    status = db.Column(db.String(20), default='active')  # active, maintenance, retired, broken
    condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
    last_service_date = db.Column(db.Date)
    next_service_date = db.Column(db.Date)
    
    # Performance metrics
    efficiency_rating = db.Column(db.Float)  # 0-100%
    uptime_percentage = db.Column(db.Float)  # 0-100%
    total_operating_hours = db.Column(db.Float, default=0)
    
    # AI insights
    health_score = db.Column(db.Float)  # AI-calculated health score
    predicted_failure_date = db.Column(db.Date)
    maintenance_priority = db.Column(db.String(10))  # low, medium, high, critical
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_code': self.equipment_code,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
            'year_manufactured': self.year_manufactured,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_cost': self.purchase_cost,
            'location': self.location,
            'capacity': self.capacity,
            'capacity_unit': self.capacity_unit,
            'specifications': self.specifications,
            'operating_parameters': self.operating_parameters,
            'status': self.status,
            'condition': self.condition,
            'last_service_date': self.last_service_date.isoformat() if self.last_service_date else None,
            'next_service_date': self.next_service_date.isoformat() if self.next_service_date else None,
            'efficiency_rating': self.efficiency_rating,
            'uptime_percentage': self.uptime_percentage,
            'total_operating_hours': self.total_operating_hours,
            'health_score': self.health_score,
            'predicted_failure_date': self.predicted_failure_date.isoformat() if self.predicted_failure_date else None,
            'maintenance_priority': self.maintenance_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MaintenanceSchedule(db.Model):
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Schedule identification
    schedule_name = db.Column(db.String(100), nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False)  # preventive, predictive, corrective
    
    # Equipment reference
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    # Schedule details
    frequency_type = db.Column(db.String(20), nullable=False)  # hours, days, weeks, months
    frequency_value = db.Column(db.Integer, nullable=False)  # e.g., 30 for 30 days
    
    # Maintenance tasks
    tasks = db.Column(JSON, nullable=False)  # List of maintenance tasks
    estimated_duration = db.Column(db.Integer)  # in minutes
    required_parts = db.Column(JSON)  # Required spare parts
    required_skills = db.Column(JSON)  # Required technician skills
    
    # Scheduling
    last_completed = db.Column(db.DateTime)
    next_due = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # AI optimization
    ai_optimized = db.Column(db.Boolean, default=False)
    optimization_data = db.Column(JSON)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='maintenance_schedules')
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_name': self.schedule_name,
            'schedule_type': self.schedule_type,
            'equipment': self.equipment.to_dict() if self.equipment else None,
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
            'tasks': self.tasks,
            'estimated_duration': self.estimated_duration,
            'required_parts': self.required_parts,
            'required_skills': self.required_skills,
            'last_completed': self.last_completed.isoformat() if self.last_completed else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'is_active': self.is_active,
            'ai_optimized': self.ai_optimized,
            'optimization_data': self.optimization_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MaintenanceTask(db.Model):
    __tablename__ = 'maintenance_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Task identification
    task_number = db.Column(db.String(20), unique=True, nullable=False)
    task_type = db.Column(db.String(20), nullable=False)  # preventive, corrective, emergency
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    
    # Equipment and schedule reference
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('maintenance_schedules.id'))
    
    # Task details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime, nullable=False)
    estimated_duration = db.Column(db.Integer)  # in minutes
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_team = db.Column(JSON)  # List of team member IDs
    
    # Status and completion
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    completion_percentage = db.Column(db.Float, default=0)
    
    # Parts and materials
    required_parts = db.Column(JSON)
    parts_used = db.Column(JSON)
    parts_cost = db.Column(db.Float, default=0)
    
    # Results and notes
    work_performed = db.Column(db.Text)
    issues_found = db.Column(JSON)
    recommendations = db.Column(JSON)
    technician_notes = db.Column(db.Text)
    
    # Quality and safety
    safety_checklist = db.Column(JSON)
    quality_check_passed = db.Column(db.Boolean)
    
    # AI insights
    ai_recommendations = db.Column(JSON)
    predicted_issues = db.Column(JSON)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='maintenance_tasks')
    schedule = db.relationship('MaintenanceSchedule', backref='tasks')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_maintenance_tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_number': self.task_number,
            'task_type': self.task_type,
            'priority': self.priority,
            'equipment': self.equipment.to_dict() if self.equipment else None,
            'schedule': self.schedule.to_dict() if self.schedule else None,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'estimated_duration': self.estimated_duration,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'assignee': self.assignee.username if self.assignee else None,
            'assigned_team': self.assigned_team,
            'status': self.status,
            'completion_percentage': self.completion_percentage,
            'required_parts': self.required_parts,
            'parts_used': self.parts_used,
            'parts_cost': self.parts_cost,
            'work_performed': self.work_performed,
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'technician_notes': self.technician_notes,
            'safety_checklist': self.safety_checklist,
            'quality_check_passed': self.quality_check_passed,
            'ai_recommendations': self.ai_recommendations,
            'predicted_issues': self.predicted_issues,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentReading(db.Model):
    __tablename__ = 'equipment_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Equipment reference
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    # Reading details
    reading_type = db.Column(db.String(30), nullable=False)  # temperature, pressure, vibration, etc.
    reading_value = db.Column(db.Float, nullable=False)
    reading_unit = db.Column(db.String(20), nullable=False)
    
    # Context
    reading_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    production_context = db.Column(JSON)  # Related production batch, etc.
    
    # Status and alerts
    is_normal = db.Column(db.Boolean, default=True)
    alert_triggered = db.Column(db.Boolean, default=False)
    alert_level = db.Column(db.String(10))  # warning, critical
    
    # AI analysis
    anomaly_score = db.Column(db.Float)  # AI-calculated anomaly score
    predicted_trend = db.Column(db.String(20))  # increasing, decreasing, stable
    ai_insights = db.Column(JSON)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='readings')
    operator = db.relationship('User', backref='equipment_readings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment': self.equipment.to_dict() if self.equipment else None,
            'reading_type': self.reading_type,
            'reading_value': self.reading_value,
            'reading_unit': self.reading_unit,
            'reading_timestamp': self.reading_timestamp.isoformat() if self.reading_timestamp else None,
            'operator': self.operator.username if self.operator else None,
            'production_context': self.production_context,
            'is_normal': self.is_normal,
            'alert_triggered': self.alert_triggered,
            'alert_level': self.alert_level,
            'anomaly_score': self.anomaly_score,
            'predicted_trend': self.predicted_trend,
            'ai_insights': self.ai_insights,
            'notes': self.notes
        }

class SparePart(db.Model):
    __tablename__ = 'spare_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Part identification
    part_number = db.Column(db.String(50), unique=True, nullable=False)
    part_name = db.Column(db.String(100), nullable=False)
    part_category = db.Column(db.String(50), nullable=False)
    
    # Part details
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    unit_cost = db.Column(db.Float)
    
    # Inventory
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=1)
    maximum_stock = db.Column(db.Integer, default=10)
    reorder_point = db.Column(db.Integer, default=2)
    
    # Compatibility
    compatible_equipment = db.Column(JSON)  # List of equipment IDs
    
    # Usage tracking
    total_used = db.Column(db.Integer, default=0)
    average_monthly_usage = db.Column(db.Float, default=0)
    
    # AI predictions
    predicted_demand = db.Column(db.Float)
    optimal_stock_level = db.Column(db.Integer)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_critical = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'part_number': self.part_number,
            'part_name': self.part_name,
            'part_category': self.part_category,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'supplier': self.supplier,
            'unit_cost': self.unit_cost,
            'current_stock': self.current_stock,
            'minimum_stock': self.minimum_stock,
            'maximum_stock': self.maximum_stock,
            'reorder_point': self.reorder_point,
            'compatible_equipment': self.compatible_equipment,
            'total_used': self.total_used,
            'average_monthly_usage': self.average_monthly_usage,
            'predicted_demand': self.predicted_demand,
            'optimal_stock_level': self.optimal_stock_level,
            'is_active': self.is_active,
            'is_critical': self.is_critical,
            'stock_status': self._get_stock_status(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def _get_stock_status(self):
        """Get current stock status"""
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock <= self.reorder_point:
            return 'reorder_needed'
        elif self.current_stock <= self.minimum_stock:
            return 'low_stock'
        else:
            return 'adequate'