from datetime import datetime
from sqlalchemy import JSON
from extensions import db

class QualityStandard(db.Model):
    __tablename__ = 'quality_standards'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Standard identification
    standard_name = db.Column(db.String(100), nullable=False)
    standard_code = db.Column(db.String(20), unique=True, nullable=False)
    product_type = db.Column(db.String(50), nullable=False)  # rice, paddy, byproduct
    grade = db.Column(db.String(5), nullable=False)  # A, B, C, Export
    
    # Quality parameters with acceptable ranges
    moisture_content_min = db.Column(db.Float)
    moisture_content_max = db.Column(db.Float)
    broken_grains_max = db.Column(db.Float)
    foreign_matter_max = db.Column(db.Float)
    chalky_grains_max = db.Column(db.Float)
    damaged_grains_max = db.Column(db.Float)
    
    # Physical parameters
    grain_length_min = db.Column(db.Float)
    grain_length_max = db.Column(db.Float)
    grain_width_min = db.Column(db.Float)
    grain_width_max = db.Column(db.Float)
    whiteness_index_min = db.Column(db.Float)
    
    # Additional parameters (JSON for flexibility)
    additional_parameters = db.Column(JSON)
    
    # Standard metadata
    version = db.Column(db.String(10), default='1.0')
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'standard_name': self.standard_name,
            'standard_code': self.standard_code,
            'product_type': self.product_type,
            'grade': self.grade,
            'parameters': {
                'moisture_content': {'min': self.moisture_content_min, 'max': self.moisture_content_max},
                'broken_grains_max': self.broken_grains_max,
                'foreign_matter_max': self.foreign_matter_max,
                'chalky_grains_max': self.chalky_grains_max,
                'damaged_grains_max': self.damaged_grains_max,
                'grain_length': {'min': self.grain_length_min, 'max': self.grain_length_max},
                'grain_width': {'min': self.grain_width_min, 'max': self.grain_width_max},
                'whiteness_index_min': self.whiteness_index_min
            },
            'additional_parameters': self.additional_parameters,
            'version': self.version,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'is_active': self.is_active
        }

class QualityTestTemplate(db.Model):
    __tablename__ = 'quality_test_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Template identification
    template_name = db.Column(db.String(100), nullable=False)
    template_code = db.Column(db.String(20), unique=True, nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    test_type = db.Column(db.String(30), nullable=False)  # incoming, in_process, final, export
    
    # Test parameters to be checked
    test_parameters = db.Column(JSON, nullable=False)  # List of parameters to test
    test_methods = db.Column(JSON)  # Testing methods for each parameter
    equipment_required = db.Column(JSON)  # Required equipment
    
    # Test execution
    estimated_duration = db.Column(db.Integer)  # in minutes
    required_sample_size = db.Column(db.Float)  # in grams/kg
    test_frequency = db.Column(db.String(20))  # per_batch, daily, weekly
    
    # Quality standards reference
    quality_standard_id = db.Column(db.Integer, db.ForeignKey('quality_standards.id'))
    
    # Template metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    quality_standard = db.relationship('QualityStandard', backref='test_templates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_name': self.template_name,
            'template_code': self.template_code,
            'product_type': self.product_type,
            'test_type': self.test_type,
            'test_parameters': self.test_parameters,
            'test_methods': self.test_methods,
            'equipment_required': self.equipment_required,
            'estimated_duration': self.estimated_duration,
            'required_sample_size': self.required_sample_size,
            'test_frequency': self.test_frequency,
            'quality_standard': self.quality_standard.to_dict() if self.quality_standard else None,
            'is_active': self.is_active
        }

class QualityInspection(db.Model):
    __tablename__ = 'quality_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Inspection identification
    inspection_number = db.Column(db.String(20), unique=True, nullable=False)
    inspection_type = db.Column(db.String(30), nullable=False)  # incoming, in_process, final, audit
    
    # Reference to what's being inspected
    reference_type = db.Column(db.String(20), nullable=False)  # batch, procurement, shipment
    reference_id = db.Column(db.Integer, nullable=False)
    
    # Inspection details
    product_type = db.Column(db.String(50), nullable=False)
    product_variety = db.Column(db.String(50))
    sample_size = db.Column(db.Float, nullable=False)
    sample_location = db.Column(db.String(100))
    
    # Test template used
    test_template_id = db.Column(db.Integer, db.ForeignKey('quality_test_templates.id'))
    
    # Inspection execution
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    # Test results (JSON for flexibility)
    test_results = db.Column(JSON, nullable=False)
    
    # Overall assessment
    overall_grade = db.Column(db.String(5))  # A, B, C, D, F
    quality_score = db.Column(db.Float)  # 0-100
    pass_fail = db.Column(db.Boolean, default=True)
    
    # AI analysis
    ai_analysis = db.Column(JSON)
    confidence_score = db.Column(db.Float)
    anomalies_detected = db.Column(JSON)
    
    # Status and approval
    status = db.Column(db.String(20), default='pending')  # pending, completed, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    
    # Notes and recommendations
    inspector_notes = db.Column(db.Text)
    recommendations = db.Column(JSON)
    corrective_actions = db.Column(JSON)
    
    # Relationships
    test_template = db.relationship('QualityTestTemplate', backref='inspections')
    inspector = db.relationship('User', foreign_keys=[inspector_id], backref='conducted_inspections')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_inspections')
    
    def to_dict(self):
        return {
            'id': self.id,
            'inspection_number': self.inspection_number,
            'inspection_type': self.inspection_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'product_type': self.product_type,
            'product_variety': self.product_variety,
            'sample_size': self.sample_size,
            'sample_location': self.sample_location,
            'test_template': self.test_template.to_dict() if self.test_template else None,
            'inspector': self.inspector.username if self.inspector else None,
            'inspection_date': self.inspection_date.isoformat() if self.inspection_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'test_results': self.test_results,
            'overall_grade': self.overall_grade,
            'quality_score': self.quality_score,
            'pass_fail': self.pass_fail,
            'ai_analysis': self.ai_analysis,
            'confidence_score': self.confidence_score,
            'anomalies_detected': self.anomalies_detected,
            'status': self.status,
            'approver': self.approver.username if self.approver else None,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'inspector_notes': self.inspector_notes,
            'recommendations': self.recommendations,
            'corrective_actions': self.corrective_actions
        }

class QualityAlert(db.Model):
    __tablename__ = 'quality_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Alert identification
    alert_number = db.Column(db.String(20), unique=True, nullable=False)
    alert_type = db.Column(db.String(30), nullable=False)  # quality_failure, trend_deviation, equipment_issue
    severity = db.Column(db.String(10), nullable=False)  # low, medium, high, critical
    
    # Alert source
    source_type = db.Column(db.String(20), nullable=False)  # inspection, ai_analysis, manual
    source_id = db.Column(db.Integer)
    
    # Alert details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    affected_products = db.Column(JSON)
    potential_impact = db.Column(db.Text)
    
    # Alert status
    status = db.Column(db.String(20), default='open')  # open, investigating, resolved, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timeline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Resolution
    resolution_notes = db.Column(db.Text)
    corrective_actions_taken = db.Column(JSON)
    preventive_measures = db.Column(JSON)
    
    # AI insights
    ai_recommendations = db.Column(JSON)
    risk_assessment = db.Column(JSON)
    
    # Relationships
    assignee = db.relationship('User', backref='assigned_quality_alerts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_number': self.alert_number,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'title': self.title,
            'description': self.description,
            'affected_products': self.affected_products,
            'potential_impact': self.potential_impact,
            'status': self.status,
            'assignee': self.assignee.username if self.assignee else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
            'corrective_actions_taken': self.corrective_actions_taken,
            'preventive_measures': self.preventive_measures,
            'ai_recommendations': self.ai_recommendations,
            'risk_assessment': self.risk_assessment
        }

class QualityTrend(db.Model):
    __tablename__ = 'quality_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Trend identification
    trend_date = db.Column(db.Date, nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    parameter_name = db.Column(db.String(50), nullable=False)
    
    # Trend data
    average_value = db.Column(db.Float)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    std_deviation = db.Column(db.Float)
    sample_count = db.Column(db.Integer)
    
    # Trend analysis
    trend_direction = db.Column(db.String(10))  # improving, declining, stable
    trend_strength = db.Column(db.Float)  # correlation coefficient
    
    # AI analysis
    ai_insights = db.Column(JSON)
    anomaly_score = db.Column(db.Float)
    predictions = db.Column(JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trend_date': self.trend_date.isoformat() if self.trend_date else None,
            'product_type': self.product_type,
            'parameter_name': self.parameter_name,
            'average_value': self.average_value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'std_deviation': self.std_deviation,
            'sample_count': self.sample_count,
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'ai_insights': self.ai_insights,
            'anomaly_score': self.anomaly_score,
            'predictions': self.predictions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }