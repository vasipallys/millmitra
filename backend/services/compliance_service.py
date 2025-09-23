from datetime import datetime, timedelta
from typing import Dict, List
from models.compliance import (
    ComplianceFramework, ComplianceAssessment, ComplianceActionItem,
    RegulatoryDocument, ComplianceAlert, AuditTrail
)
from models.user import User
from extensions import db

class ComplianceService:
    def __init__(self):
        pass
    
    def create_assessment(self, user: User, assessment_data: Dict):
        """Create compliance assessment"""
        assessment = ComplianceAssessment(
            assessment_name=assessment_data['assessment_name'],
            framework_id=assessment_data['framework_id'],
            assessment_type=assessment_data['assessment_type'],
            assessment_date=datetime.fromisoformat(assessment_data['assessment_date']),
            assessor_name=assessment_data.get('assessor_name'),
            assessor_organization=assessment_data.get('assessor_organization'),
            assessment_scope=assessment_data.get('assessment_scope'),
            areas_covered=assessment_data.get('areas_covered', []),
            conducted_by=user.id
        )
        
        db.session.add(assessment)
        db.session.flush()
        
        # Create action items if provided
        for action_data in assessment_data.get('action_items', []):
            action_item = ComplianceActionItem(
                assessment_id=assessment.id,
                action_title=action_data['action_title'],
                description=action_data['description'],
                action_type=action_data.get('action_type', 'corrective'),
                priority=action_data.get('priority', 'medium'),
                due_date=datetime.fromisoformat(action_data['due_date']),
                assigned_to=action_data.get('assigned_to'),
                department=action_data.get('department'),
                estimated_effort=action_data.get('estimated_effort'),
                evidence_required=action_data.get('evidence_required')
            )
            db.session.add(action_item)
        
        # Log audit trail
        self._log_audit_event(user, 'create', 'assessment', assessment.id, assessment_data)
        
        db.session.commit()
        return assessment
    
    def update_assessment_results(self, assessment_id: int, results_data: Dict, user: User):
        """Update assessment results"""
        assessment = ComplianceAssessment.query.get_or_404(assessment_id)
        
        old_values = {
            'overall_score': assessment.overall_score,
            'compliance_percentage': assessment.compliance_percentage,
            'status': assessment.status
        }
        
        assessment.overall_score = results_data.get('overall_score')
        assessment.compliance_percentage = results_data.get('compliance_percentage')
        assessment.status = results_data.get('status', 'compliant')
        assessment.findings = results_data.get('findings', [])
        assessment.recommendations = results_data.get('recommendations', [])
        assessment.next_assessment_date = datetime.fromisoformat(results_data['next_assessment_date']) if results_data.get('next_assessment_date') else None
        assessment.follow_up_required = results_data.get('follow_up_required', False)
        
        # Create alerts for non-compliance
        if assessment.status == 'non_compliant':
            self._create_compliance_alert(
                'Non-Compliance Detected',
                'violation',
                f'Assessment {assessment.assessment_name} shows non-compliance',
                'high',
                related_assessment_id=assessment.id
            )
        
        # Log audit trail
        self._log_audit_event(user, 'update', 'assessment', assessment.id, results_data, old_values)
        
        db.session.commit()
        return assessment
    
    def create_regulatory_document(self, user: User, document_data: Dict):
        """Create regulatory document"""
        document = RegulatoryDocument(
            document_name=document_data['document_name'],
            document_type=document_data['document_type'],
            document_number=document_data.get('document_number'),
            issuing_authority=document_data['issuing_authority'],
            issuing_office=document_data.get('issuing_office'),
            issue_date=datetime.fromisoformat(document_data['issue_date']),
            expiry_date=datetime.fromisoformat(document_data['expiry_date']) if document_data.get('expiry_date') else None,
            renewal_required=document_data.get('renewal_required', True),
            scope=document_data.get('scope'),
            conditions=document_data.get('conditions', []),
            restrictions=document_data.get('restrictions', []),
            document_file=document_data.get('document_file'),
            renewal_notice_days=document_data.get('renewal_notice_days', 30),
            renewal_cost=document_data.get('renewal_cost'),
            related_frameworks=document_data.get('related_frameworks', []),
            created_by=user.id
        )
        
        db.session.add(document)
        db.session.flush()
        
        # Create expiry alert if applicable
        if document.expiry_date and document.renewal_required:
            alert_date = document.expiry_date - timedelta(days=document.renewal_notice_days)
            if alert_date > datetime.now():
                self._create_compliance_alert(
                    f'Document Renewal Required: {document.document_name}',
                    'expiry',
                    f'Document {document.document_name} expires on {document.expiry_date.strftime("%Y-%m-%d")}',
                    'medium',
                    trigger_date=alert_date,
                    due_date=document.expiry_date,
                    related_document_id=document.id
                )
        
        # Log audit trail
        self._log_audit_event(user, 'create', 'document', document.id, document_data)
        
        db.session.commit()
        return document
    
    def update_action_item_progress(self, action_item_id: int, progress_data: Dict, user: User):
        """Update action item progress"""
        action_item = ComplianceActionItem.query.get_or_404(action_item_id)
        
        old_values = {
            'status': action_item.status,
            'progress_percentage': action_item.progress_percentage
        }
        
        action_item.status = progress_data.get('status', action_item.status)
        action_item.progress_percentage = progress_data.get('progress_percentage', action_item.progress_percentage)
        
        if progress_data.get('evidence_provided'):
            action_item.evidence_provided = progress_data['evidence_provided']
        
        if action_item.status == 'completed':
            action_item.completion_date = datetime.utcnow()
            action_item.progress_percentage = 100
            action_item.actual_cost = progress_data.get('actual_cost')
        
        # Log audit trail
        self._log_audit_event(user, 'update', 'action_item', action_item.id, progress_data, old_values)
        
        db.session.commit()
        return action_item
    
    def get_compliance_dashboard(self):
        """Get compliance dashboard data"""
        # Overall compliance status
        total_assessments = ComplianceAssessment.query.count()
        compliant_assessments = ComplianceAssessment.query.filter_by(status='compliant').count()
        compliance_rate = (compliant_assessments / total_assessments * 100) if total_assessments > 0 else 0
        
        # Active alerts
        active_alerts = ComplianceAlert.query.filter_by(status='active').count()
        critical_alerts = ComplianceAlert.query.filter(
            ComplianceAlert.status == 'active',
            ComplianceAlert.severity == 'critical'
        ).count()
        
        # Pending action items
        pending_actions = ComplianceActionItem.query.filter(
            ComplianceActionItem.status.in_(['open', 'in_progress'])
        ).count()
        
        overdue_actions = ComplianceActionItem.query.filter(
            ComplianceActionItem.status.in_(['open', 'in_progress']),
            ComplianceActionItem.due_date < datetime.now()
        ).count()
        
        # Document status
        total_documents = RegulatoryDocument.query.count()
        expiring_documents = RegulatoryDocument.query.filter(
            RegulatoryDocument.expiry_date <= datetime.now() + timedelta(days=30),
            RegulatoryDocument.status == 'active'
        ).count()
        
        # Recent assessments
        recent_assessments = ComplianceAssessment.query.order_by(
            ComplianceAssessment.assessment_date.desc()
        ).limit(5).all()
        
        return {
            'compliance_overview': {
                'total_assessments': total_assessments,
                'compliance_rate': compliance_rate,
                'active_alerts': active_alerts,
                'critical_alerts': critical_alerts
            },
            'action_items': {
                'pending': pending_actions,
                'overdue': overdue_actions
            },
            'documents': {
                'total': total_documents,
                'expiring_soon': expiring_documents
            },
            'recent_assessments': [
                {
                    'id': a.id,
                    'name': a.assessment_name,
                    'date': a.assessment_date.isoformat(),
                    'status': a.status,
                    'compliance_percentage': a.compliance_percentage
                }
                for a in recent_assessments
            ]
        }
    
    def generate_compliance_report(self, start_date: str, end_date: str, framework_id: int = None):
        """Generate compliance report"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        query = ComplianceAssessment.query.filter(
            ComplianceAssessment.assessment_date >= start,
            ComplianceAssessment.assessment_date <= end
        )
        
        if framework_id:
            query = query.filter_by(framework_id=framework_id)
        
        assessments = query.all()
        
        # Calculate metrics
        total_assessments = len(assessments)
        compliant_count = len([a for a in assessments if a.status == 'compliant'])
        avg_compliance_score = sum(a.compliance_percentage or 0 for a in assessments) / total_assessments if total_assessments > 0 else 0
        
        # Group by framework
        framework_breakdown = {}
        for assessment in assessments:
            framework_name = assessment.framework.framework_name
            if framework_name not in framework_breakdown:
                framework_breakdown[framework_name] = {
                    'total': 0,
                    'compliant': 0,
                    'avg_score': 0
                }
            
            framework_breakdown[framework_name]['total'] += 1
            if assessment.status == 'compliant':
                framework_breakdown[framework_name]['compliant'] += 1
            framework_breakdown[framework_name]['avg_score'] += assessment.compliance_percentage or 0
        
        # Calculate averages
        for framework in framework_breakdown.values():
            if framework['total'] > 0:
                framework['avg_score'] /= framework['total']
                framework['compliance_rate'] = (framework['compliant'] / framework['total']) * 100
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_assessments': total_assessments,
                'compliant_assessments': compliant_count,
                'compliance_rate': (compliant_count / total_assessments * 100) if total_assessments > 0 else 0,
                'average_compliance_score': avg_compliance_score
            },
            'framework_breakdown': framework_breakdown,
            'assessments': [
                {
                    'id': a.id,
                    'name': a.assessment_name,
                    'framework': a.framework.framework_name,
                    'date': a.assessment_date.isoformat(),
                    'status': a.status,
                    'score': a.compliance_percentage
                }
                for a in assessments
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def check_expiring_documents(self):
        """Check for expiring documents and create alerts"""
        upcoming_expiry = datetime.now() + timedelta(days=30)
        
        expiring_docs = RegulatoryDocument.query.filter(
            RegulatoryDocument.expiry_date <= upcoming_expiry,
            RegulatoryDocument.status == 'active',
            RegulatoryDocument.renewal_required == True
        ).all()
        
        alerts_created = 0
        for doc in expiring_docs:
            # Check if alert already exists
            existing_alert = ComplianceAlert.query.filter(
                ComplianceAlert.related_document_id == doc.id,
                ComplianceAlert.alert_type == 'expiry',
                ComplianceAlert.status == 'active'
            ).first()
            
            if not existing_alert:
                days_to_expiry = (doc.expiry_date - datetime.now()).days
                severity = 'critical' if days_to_expiry <= 7 else 'high' if days_to_expiry <= 15 else 'medium'
                
                self._create_compliance_alert(
                    f'Document Expiring: {doc.document_name}',
                    'expiry',
                    f'Document expires in {days_to_expiry} days',
                    severity,
                    due_date=doc.expiry_date,
                    related_document_id=doc.id
                )
                alerts_created += 1
        
        db.session.commit()
        return alerts_created
    
    # Helper methods
    def _create_compliance_alert(self, title: str, alert_type: str, description: str, severity: str, 
                                trigger_date: datetime = None, due_date: datetime = None,
                                related_document_id: int = None, related_assessment_id: int = None,
                                related_action_item_id: int = None):
        """Create compliance alert"""
        alert = ComplianceAlert(
            alert_title=title,
            alert_type=alert_type,
            description=description,
            severity=severity,
            trigger_date=trigger_date or datetime.now(),
            due_date=due_date,
            related_document_id=related_document_id,
            related_assessment_id=related_assessment_id,
            related_action_item_id=related_action_item_id
        )
        db.session.add(alert)
    
    def _log_audit_event(self, user: User, event_type: str, entity_type: str, entity_id: int, 
                        new_values: Dict, old_values: Dict = None):
        """Log audit trail event"""
        audit = AuditTrail(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user.id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=f"{event_type.title()} {entity_type} {entity_id}"
        )
        db.session.add(audit)