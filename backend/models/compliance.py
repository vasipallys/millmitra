from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import db

class ComplianceFramework(db.Model):
    __tablename__ = 'compliance_frameworks'
    
    id = db.Column(db.Integer, primary_key=True)
    framework_name = db.Column(db.String(100), nullable=False)
    framework_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Framework details
    regulatory_body = db.Column(db.String(100))
    framework_type = db.Column(db.String(50))  # food_safety, environmental, labor, tax
    applicable_scope = db.Column(db.String(100))  # national, state, local
    
    # Requirements
    requirements = db.Column(JSON)  # List of compliance requirements
    documentation_required = db.Column(JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = relationship("ComplianceAssessment", back_populates="framework")

class ComplianceAssessment(db.Model):
    __tablename__ = 'compliance_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_name = db.Column(db.String(100), nullable=False)
    framework_id = db.Column(db.Integer, db.ForeignKey('compliance_frameworks.id'), nullable=False)
    
    # Assessment details
    assessment_type = db.Column(db.String(50))  # internal, external, audit
    assessment_date = db.Column(db.DateTime, nullable=False)
    assessor_name = db.Column(db.String(100))
    assessor_organization = db.Column(db.String(100))
    
    # Scope
    assessment_scope = db.Column(db.Text)
    areas_covered = db.Column(JSON)
    
    # Results
    overall_score = db.Column(db.Float)
    compliance_percentage = db.Column(db.Float)
    status = db.Column(db.String(20), default='compliant')  # compliant, non_compliant, partial
    
    # Findings
    findings = db.Column(JSON)  # List of findings with severity
    recommendations = db.Column(JSON)
    
    # Follow-up
    next_assessment_date = db.Column(db.DateTime)
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Documentation
    assessment_report = db.Column(db.String(255))  # File path
    supporting_documents = db.Column(JSON)
    
    conducted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    framework = relationship("ComplianceFramework", back_populates="assessments")
    conducted_by_user = relationship("User")
    action_items = relationship("ComplianceActionItem", back_populates="assessment")

class ComplianceActionItem(db.Model):
    __tablename__ = 'compliance_action_items'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('compliance_assessments.id'), nullable=False)
    
    # Action details
    action_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    action_type = db.Column(db.String(50))  # corrective, preventive, improvement
    
    # Priority and timeline
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    due_date = db.Column(db.DateTime, nullable=False)
    estimated_effort = db.Column(db.Integer)  # hours
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    department = db.Column(db.String(50))
    
    # Progress
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    progress_percentage = db.Column(db.Float, default=0)
    completion_date = db.Column(db.DateTime)
    
    # Evidence and verification
    evidence_required = db.Column(db.Text)
    evidence_provided = db.Column(JSON)
    verification_method = db.Column(db.String(100))
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verification_date = db.Column(db.DateTime)
    
    # Cost impact
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="action_items")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
    verified_by_user = relationship("User", foreign_keys=[verified_by])

class RegulatoryDocument(db.Model):
    __tablename__ = 'regulatory_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # license, permit, certificate, registration
    document_number = db.Column(db.String(100), unique=True)
    
    # Issuing authority
    issuing_authority = db.Column(db.String(100), nullable=False)
    issuing_office = db.Column(db.String(100))
    
    # Validity
    issue_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime)
    renewal_required = db.Column(db.Boolean, default=True)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, expired, suspended, cancelled
    
    # Document details
    scope = db.Column(db.Text)
    conditions = db.Column(JSON)
    restrictions = db.Column(JSON)
    
    # File storage
    document_file = db.Column(db.String(255))  # File path
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(20))
    
    # Renewal tracking
    renewal_notice_days = db.Column(db.Integer, default=30)
    last_renewal_date = db.Column(db.DateTime)
    renewal_cost = db.Column(db.Float)
    
    # Compliance linkage
    related_frameworks = db.Column(JSON)  # List of framework IDs
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")

class ComplianceAlert(db.Model):
    __tablename__ = 'compliance_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_title = db.Column(db.String(200), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # expiry, violation, update, reminder
    
    # Alert details
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Trigger conditions
    trigger_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Related entities
    related_document_id = db.Column(db.Integer, db.ForeignKey('regulatory_documents.id'))
    related_assessment_id = db.Column(db.Integer, db.ForeignKey('compliance_assessments.id'))
    related_action_item_id = db.Column(db.Integer, db.ForeignKey('compliance_action_items.id'))
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved, dismissed
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    # Notification
    notification_sent = db.Column(db.Boolean, default=False)
    notification_channels = db.Column(JSON)  # email, sms, dashboard
    recipients = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    related_document = relationship("RegulatoryDocument")
    related_assessment = relationship("ComplianceAssessment")
    related_action_item = relationship("ComplianceActionItem")
    acknowledged_by_user = relationship("User")

class AuditTrail(db.Model):
    __tablename__ = 'audit_trails'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # create, update, delete, access
    entity_type = db.Column(db.String(50), nullable=False)  # document, assessment, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    
    # User and session
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    # Changes
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)
    changes_summary = db.Column(db.Text)
    
    # Context
    reason = db.Column(db.Text)
    additional_context = db.Column(JSON)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")