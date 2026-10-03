"""
Farmer Edit Request Model
Tracks pending farmer information edit requests that require approval
"""

from datetime import datetime
from extensions import db
import json

class FarmerEditRequest(db.Model):
    __tablename__ = 'farmer_edit_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    
    # Reference to farmer being edited
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # User who requested the edit
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Request details
    request_type = db.Column(db.String(50), default='farmer_edit')  # farmer_edit, profile_update, etc.
    request_reason = db.Column(db.Text)  # Reason for the edit
    
    # Original data (before edit)
    original_data = db.Column(db.Text)  # JSON string of original farmer data
    
    # Proposed changes
    proposed_changes = db.Column(db.Text)  # JSON string of proposed changes
    
    # Changed fields list
    changed_fields = db.Column(db.Text)  # JSON array of field names that changed
    
    # Request status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    
    # Approval details
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    review_comments = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Priority level
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Auto-approval settings
    requires_approval = db.Column(db.Boolean, default=True)
    auto_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    farmer = db.relationship('Farmer', backref='edit_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='farmer_edit_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_farmer_edits')
    
    def __init__(self, **kwargs):
        super(FarmerEditRequest, self).__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'farmer_name': self.farmer.name if self.farmer else None,
            'farmer_code': self.farmer.farmer_code if self.farmer else None,
            'requested_by': self.requested_by,
            'requester_name': self.requester.username if self.requester else None,
            'request_type': self.request_type,
            'request_reason': self.request_reason,
            'original_data': json.loads(self.original_data) if self.original_data else {},
            'proposed_changes': json.loads(self.proposed_changes) if self.proposed_changes else {},
            'changed_fields': json.loads(self.changed_fields) if self.changed_fields else [],
            'status': self.status,
            'priority': self.priority,
            'requires_approval': self.requires_approval,
            'auto_approved': self.auto_approved,
            'reviewed_by': self.reviewed_by,
            'reviewer_name': self.reviewer.username if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_comments': self.review_comments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_summary(self):
        """Get a summary of changes for display"""
        try:
            changes = json.loads(self.proposed_changes) if self.proposed_changes else {}
            fields = json.loads(self.changed_fields) if self.changed_fields else []
            
            summary = {
                'total_changes': len(fields),
                'changed_fields': fields,
                'critical_changes': [],
                'minor_changes': []
            }
            
            # Categorize changes
            critical_fields = ['name', 'phone', 'aadhar_number', 'pan_number', 'bank_account', 'ifsc_code']
            
            for field in fields:
                if field in critical_fields:
                    summary['critical_changes'].append({
                        'field': field,
                        'old_value': self.get_original_value(field),
                        'new_value': changes.get(field)
                    })
                else:
                    summary['minor_changes'].append({
                        'field': field,
                        'old_value': self.get_original_value(field),
                        'new_value': changes.get(field)
                    })
            
            return summary
        except Exception as e:
            return {'error': str(e), 'total_changes': 0}
    
    def get_original_value(self, field):
        """Get original value for a field"""
        try:
            original = json.loads(self.original_data) if self.original_data else {}
            return original.get(field)
        except:
            return None
    
    def approve(self, reviewer_id, comments=None):
        """Approve the edit request"""
        self.status = 'approved'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_comments = comments
        self.updated_at = datetime.utcnow()
    
    def reject(self, reviewer_id, comments=None):
        """Reject the edit request"""
        self.status = 'rejected'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_comments = comments
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel the edit request"""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def create_edit_request(farmer_id, requested_by, original_data, proposed_changes, reason=None):
        """Create a new edit request"""
        
        # Determine which fields changed
        changed_fields = []
        for key, new_value in proposed_changes.items():
            old_value = original_data.get(key)
            if str(old_value) != str(new_value):
                changed_fields.append(key)
        
        # Determine priority based on changed fields
        critical_fields = ['name', 'phone', 'aadhar_number', 'pan_number', 'bank_account', 'ifsc_code']
        priority = 'high' if any(field in critical_fields for field in changed_fields) else 'medium'
        
        # Check if auto-approval is possible (for minor changes by authorized users)
        requires_approval = True
        auto_approved = False
        
        # Minor fields that can be auto-approved
        minor_fields = ['email', 'address', 'farming_experience', 'farming_type', 'irrigation_type']
        if all(field in minor_fields for field in changed_fields) and len(changed_fields) <= 2:
            # Can be auto-approved for minor changes
            requires_approval = False
            auto_approved = True
        
        edit_request = FarmerEditRequest(
            farmer_id=farmer_id,
            requested_by=requested_by,
            request_reason=reason,
            original_data=json.dumps(original_data),
            proposed_changes=json.dumps(proposed_changes),
            changed_fields=json.dumps(changed_fields),
            priority=priority,
            requires_approval=requires_approval,
            auto_approved=auto_approved,
            status='approved' if auto_approved else 'pending'
        )
        
        return edit_request
    
    @staticmethod
    def get_pending_requests():
        """Get all pending edit requests"""
        return FarmerEditRequest.query.filter_by(status='pending').order_by(
            FarmerEditRequest.priority.desc(),
            FarmerEditRequest.created_at.asc()
        ).all()
    
    @staticmethod
    def get_requests_by_farmer(farmer_id):
        """Get all edit requests for a specific farmer"""
        return FarmerEditRequest.query.filter_by(farmer_id=farmer_id).order_by(
            FarmerEditRequest.created_at.desc()
        ).all()
    
    @staticmethod
    def get_requests_by_status(status):
        """Get edit requests by status"""
        return FarmerEditRequest.query.filter_by(status=status).order_by(
            FarmerEditRequest.created_at.desc()
        ).all()
