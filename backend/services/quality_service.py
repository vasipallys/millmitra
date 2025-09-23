from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from models.quality import QualityStandard, QualityTestTemplate, QualityInspection, QualityAlert, QualityTrend
from models.production import ProductionBatch
from extensions import db
import uuid

class QualityService:
    def __init__(self):
        pass
    
    def create_quality_standard(self, user, data):
        """Create new quality standard"""
        standard = QualityStandard(
            standard_name=data['standard_name'],
            standard_code=data.get('standard_code', self._generate_standard_code()),
            product_type=data['product_type'],
            grade=data['grade'],
            moisture_content_min=data.get('moisture_content_min'),
            moisture_content_max=data.get('moisture_content_max'),
            broken_grains_max=data.get('broken_grains_max'),
            foreign_matter_max=data.get('foreign_matter_max'),
            chalky_grains_max=data.get('chalky_grains_max'),
            damaged_grains_max=data.get('damaged_grains_max'),
            grain_length_min=data.get('grain_length_min'),
            grain_length_max=data.get('grain_length_max'),
            grain_width_min=data.get('grain_width_min'),
            grain_width_max=data.get('grain_width_max'),
            whiteness_index_min=data.get('whiteness_index_min'),
            additional_parameters=data.get('additional_parameters', {}),
            version=data.get('version', '1.0'),
            effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d') if data.get('effective_date') else datetime.utcnow(),
            created_by=user.id
        )
        
        db.session.add(standard)
        db.session.commit()
        
        return standard
    
    def create_test_template(self, user, data):
        """Create new test template"""
        template = QualityTestTemplate(
            template_name=data['template_name'],
            template_code=data.get('template_code', self._generate_template_code()),
            product_type=data['product_type'],
            test_type=data['test_type'],
            test_parameters=data['test_parameters'],
            test_methods=data.get('test_methods', {}),
            equipment_required=data.get('equipment_required', []),
            estimated_duration=data.get('estimated_duration'),
            required_sample_size=data.get('required_sample_size'),
            test_frequency=data.get('test_frequency'),
            quality_standard_id=data.get('quality_standard_id'),
            created_by=user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return template
    
    def create_inspection(self, user, data, ai_analysis=None):
        """Create new quality inspection"""
        inspection = QualityInspection(
            inspection_number=self._generate_inspection_number(),
            inspection_type=data['inspection_type'],
            reference_type=data['reference_type'],
            reference_id=data['reference_id'],
            product_type=data['product_type'],
            product_variety=data.get('product_variety'),
            sample_size=data['sample_size'],
            sample_location=data.get('sample_location'),
            test_template_id=data.get('test_template_id'),
            inspector_id=user.id,
            inspection_date=datetime.strptime(data['inspection_date'], '%Y-%m-%d %H:%M:%S') if data.get('inspection_date') else datetime.utcnow(),
            start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S') if data.get('start_time') else datetime.utcnow(),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S') if data.get('end_time') else None,
            test_results=data['test_results'],
            inspector_notes=data.get('inspector_notes')
        )
        
        # Apply AI analysis results
        if ai_analysis:
            inspection.overall_grade = ai_analysis.get('recommended_grade')
            inspection.quality_score = ai_analysis.get('quality_score')
            inspection.pass_fail = ai_analysis.get('quality_score', 0) >= 70
            inspection.ai_analysis = ai_analysis
            inspection.confidence_score = ai_analysis.get('confidence')
            inspection.anomalies_detected = ai_analysis.get('anomalies_detected')
            inspection.recommendations = ai_analysis.get('recommendations')
        else:
            # Fallback calculation
            inspection.quality_score = self._calculate_basic_quality_score(data['test_results'])
            inspection.overall_grade = self._get_grade_from_score(inspection.quality_score)
            inspection.pass_fail = inspection.quality_score >= 70
        
        db.session.add(inspection)
        db.session.commit()
        
        # Update related records
        self._update_reference_quality(inspection)
        
        return inspection
    
    def approve_inspection(self, inspection, user, data):
        """Approve quality inspection"""
        inspection.status = 'approved'
        inspection.approved_by = user.id
        inspection.approval_date = datetime.utcnow()
        
        if data.get('approval_notes'):
            inspection.inspector_notes = (inspection.inspector_notes or '') + f"\nApproval Notes: {data['approval_notes']}"
        
        # Apply corrective actions if specified
        if data.get('corrective_actions'):
            inspection.corrective_actions = data['corrective_actions']
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Inspection approved successfully',
            'inspection': inspection.to_dict()
        }
    
    def create_quality_alert(self, alert_data):
        """Create quality alert"""
        alert = QualityAlert(
            alert_number=self._generate_alert_number(),
            alert_type=alert_data['alert_type'],
            severity=alert_data['severity'],
            source_type=alert_data['source_type'],
            source_id=alert_data.get('source_id'),
            title=alert_data['title'],
            description=alert_data['description'],
            affected_products=alert_data.get('affected_products', []),
            potential_impact=alert_data.get('potential_impact'),
            assigned_to=alert_data.get('assigned_to'),
            ai_recommendations=alert_data.get('ai_recommendations'),
            risk_assessment=alert_data.get('risk_assessment')
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    def resolve_alert(self, alert, user, data):
        """Resolve quality alert"""
        alert.status = 'resolved'
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = data.get('resolution_notes')
        alert.corrective_actions_taken = data.get('corrective_actions_taken', [])
        alert.preventive_measures = data.get('preventive_measures', [])
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Alert resolved successfully',
            'alert': alert.to_dict()
        }
    
    def get_quality_trends(self, days, product_type=None, parameter=None):
        """Get quality trends data"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        query = QualityInspection.query.filter(
            QualityInspection.inspection_date >= start_date,
            QualityInspection.inspection_date <= end_date,
            QualityInspection.status == 'approved'
        )
        
        if product_type:
            query = query.filter(QualityInspection.product_type == product_type)
        
        inspections = query.order_by(QualityInspection.inspection_date).all()
        
        # Process data for trends
        trends_data = []
        for inspection in inspections:
            test_results = inspection.test_results or {}
            
            trend_entry = {
                'date': inspection.inspection_date.date().isoformat(),
                'product_type': inspection.product_type,
                'quality_score': inspection.quality_score,
                'overall_grade': inspection.overall_grade,
                'test_results': test_results
            }
            
            # Add specific parameter if requested
            if parameter and parameter in test_results:
                trend_entry['parameter_value'] = test_results[parameter]
            
            trends_data.append(trend_entry)
        
        return trends_data
    
    def get_dashboard_data(self, days):
        """Get quality dashboard data"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Basic statistics
        total_inspections = QualityInspection.query.filter(
            QualityInspection.inspection_date >= start_date
        ).count()
        
        passed_inspections = QualityInspection.query.filter(
            QualityInspection.inspection_date >= start_date,
            QualityInspection.pass_fail == True
        ).count()
        
        # Grade distribution
        grade_distribution = db.session.query(
            QualityInspection.overall_grade,
            func.count(QualityInspection.id)
        ).filter(
            QualityInspection.inspection_date >= start_date,
            QualityInspection.overall_grade.isnot(None)
        ).group_by(QualityInspection.overall_grade).all()
        
        # Active alerts
        active_alerts = QualityAlert.query.filter(
            QualityAlert.status.in_(['open', 'investigating'])
        ).count()
        
        # Average quality score
        avg_quality_score = db.session.query(
            func.avg(QualityInspection.quality_score)
        ).filter(
            QualityInspection.inspection_date >= start_date,
            QualityInspection.quality_score.isnot(None)
        ).scalar() or 0
        
        return {
            'summary': {
                'total_inspections': total_inspections,
                'passed_inspections': passed_inspections,
                'pass_rate': (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0,
                'average_quality_score': round(float(avg_quality_score), 2),
                'active_alerts': active_alerts
            },
            'grade_distribution': dict(grade_distribution),
            'period': f"{start_date.date()} to {end_date.date()}"
        }
    
    def get_recent_quality_data(self, days):
        """Get recent quality data for analysis"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        inspections = QualityInspection.query.filter(
            QualityInspection.inspection_date >= start_date,
            QualityInspection.status == 'approved'
        ).order_by(QualityInspection.inspection_date).all()
        
        quality_data = []
        for inspection in inspections:
            test_results = inspection.test_results or {}
            
            data_point = {
                'inspection_id': inspection.id,
                'date': inspection.inspection_date.isoformat(),
                'product_type': inspection.product_type,
                'quality_score': inspection.quality_score,
                'overall_grade': inspection.overall_grade,
                **test_results  # Flatten test results
            }
            
            quality_data.append(data_point)
        
        return quality_data
    
    def get_batch_quality_data(self, batch_id):
        """Get quality data for a specific batch"""
        inspections = QualityInspection.query.filter(
            QualityInspection.reference_type == 'batch',
            QualityInspection.reference_id == batch_id
        ).order_by(QualityInspection.inspection_date).all()
        
        batch_data = {
            'batch_id': batch_id,
            'inspections': [inspection.to_dict() for inspection in inspections],
            'inspection_count': len(inspections)
        }
        
        if inspections:
            # Calculate batch quality metrics
            quality_scores = [insp.quality_score for insp in inspections if insp.quality_score]
            if quality_scores:
                batch_data['average_quality_score'] = sum(quality_scores) / len(quality_scores)
                batch_data['min_quality_score'] = min(quality_scores)
                batch_data['max_quality_score'] = max(quality_scores)
            
            # Get final inspection
            final_inspection = next((insp for insp in inspections if insp.inspection_type == 'final'), None)
            if final_inspection:
                batch_data['final_grade'] = final_inspection.overall_grade
                batch_data['final_quality_score'] = final_inspection.quality_score
        
        return batch_data
    
    def get_compliance_data(self, start_date, end_date, product_type=None):
        """Get compliance data for reporting"""
        query = QualityInspection.query
        
        if start_date:
            query = query.filter(QualityInspection.inspection_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(QualityInspection.inspection_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        if product_type:
            query = query.filter(QualityInspection.product_type == product_type)
        
        inspections = query.filter(QualityInspection.status == 'approved').all()
        
        compliance_data = {
            'total_inspections': len(inspections),
            'compliant_inspections': len([insp for insp in inspections if insp.pass_fail]),
            'compliance_rate': 0,
            'grade_breakdown': {},
            'parameter_compliance': {},
            'inspections': [insp.to_dict() for insp in inspections]
        }
        
        if inspections:
            compliance_data['compliance_rate'] = (compliance_data['compliant_inspections'] / compliance_data['total_inspections']) * 100
            
            # Grade breakdown
            for inspection in inspections:
                grade = inspection.overall_grade or 'Unknown'
                compliance_data['grade_breakdown'][grade] = compliance_data['grade_breakdown'].get(grade, 0) + 1
        
        return compliance_data
    
    def _generate_standard_code(self):
        """Generate unique standard code"""
        return f"QS{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
    
    def _generate_template_code(self):
        """Generate unique template code"""
        return f"QT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
    
    def _generate_inspection_number(self):
        """Generate unique inspection number"""
        return f"QI{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
    
    def _generate_alert_number(self):
        """Generate unique alert number"""
        return f"QA{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
    
    def _calculate_basic_quality_score(self, test_results):
        """Basic quality score calculation (fallback)"""
        score = 100
        
        # Moisture content (optimal around 14%)
        moisture = test_results.get('moisture_content', 14)
        score -= abs(moisture - 14) * 3
        
        # Foreign matter penalty
        foreign_matter = test_results.get('foreign_matter', 0)
        score -= foreign_matter * 10
        
        # Broken grains penalty
        broken_grains = test_results.get('broken_grains', 0)
        score -= broken_grains * 5
        
        return max(0, min(100, score))
    
    def _get_grade_from_score(self, score):
        """Get grade from quality score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        else:
            return 'D'
    
    def _update_reference_quality(self, inspection):
        """Update quality information in referenced records"""
        if inspection.reference_type == 'batch' and inspection.inspection_type == 'final':
            # Update production batch quality
            batch = ProductionBatch.query.get(inspection.reference_id)
            if batch:
                batch.quality_grade = inspection.overall_grade
                db.session.commit()