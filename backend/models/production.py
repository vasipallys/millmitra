"""
Production Management Models
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class ProductionBatch(db.Model):
    __tablename__ = 'production_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    paddy_stock_id = db.Column(db.Integer, db.ForeignKey('paddy_stock.id'), nullable=False)
    
    # Production details
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    machine_id = db.Column(db.String(20))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shift = db.Column(db.String(20))  # morning, afternoon, night
    
    # Input quantities
    paddy_input_quantity = db.Column(db.Float, nullable=False)  # in kg
    paddy_variety = db.Column(db.String(50))
    paddy_quality_grade = db.Column(db.String(10))
    
    # Output quantities
    rice_output = db.Column(db.Float, default=0.0)
    broken_rice_output = db.Column(db.Float, default=0.0)
    bran_output = db.Column(db.Float, default=0.0)
    husk_output = db.Column(db.Float, default=0.0)
    total_output = db.Column(db.Float, default=0.0)
    
    # Efficiency metrics
    yield_percentage = db.Column(db.Float)  # rice output / paddy input
    efficiency_percentage = db.Column(db.Float)  # overall efficiency
    wastage_percentage = db.Column(db.Float)
    
    # Quality parameters
    output_quality_grade = db.Column(db.String(10))
    moisture_content_output = db.Column(db.Float)
    broken_percentage_output = db.Column(db.Float)
    foreign_matter_output = db.Column(db.Float)
    
    # Machine parameters
    machine_settings = db.Column(db.Text)  # JSON string
    machine_performance = db.Column(db.Text)  # JSON string
    maintenance_alerts = db.Column(db.Text)  # JSON string
    
    # Status and tracking
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, paused, cancelled
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # AI insights
    predicted_yield = db.Column(db.Float)  # AI prediction before processing
    actual_vs_predicted = db.Column(db.Float)  # variance analysis
    optimization_suggestions = db.Column(db.Text)  # JSON string
    anomaly_flags = db.Column(db.Text)  # JSON string
    
    # Cost tracking
    labor_cost = db.Column(db.Float, default=0.0)
    energy_cost = db.Column(db.Float, default=0.0)
    maintenance_cost = db.Column(db.Float, default=0.0)
    total_production_cost = db.Column(db.Float, default=0.0)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    paddy_stock = relationship("PaddyStock")
    operator = relationship("User", foreign_keys=[operator_id])
    created_by_user = relationship("User", foreign_keys=[created_by])

    def get_machine_settings(self):
        if self.machine_settings:
            try:
                return json.loads(self.machine_settings)
            except:
                return {}
        return {}

    def set_machine_settings(self, settings):
        self.machine_settings = json.dumps(settings)

    def get_machine_performance(self):
        if self.machine_performance:
            try:
                return json.loads(self.machine_performance)
            except:
                return {}
        return {}

    def set_machine_performance(self, performance):
        self.machine_performance = json.dumps(performance)

    def get_optimization_suggestions(self):
        if self.optimization_suggestions:
            try:
                return json.loads(self.optimization_suggestions)
            except:
                return []
        return []

    def set_optimization_suggestions(self, suggestions):
        self.optimization_suggestions = json.dumps(suggestions)

    def get_anomaly_flags(self):
        if self.anomaly_flags:
            try:
                return json.loads(self.anomaly_flags)
            except:
                return []
        return []

    def set_anomaly_flags(self, flags):
        self.anomaly_flags = json.dumps(flags)

    def calculate_yield_percentage(self):
        """Calculate rice yield percentage"""
        if self.paddy_input_quantity and self.rice_output:
            return (self.rice_output / self.paddy_input_quantity) * 100
        return 0.0

    def calculate_efficiency_percentage(self):
        """Calculate overall production efficiency"""
        if self.paddy_input_quantity and self.total_output:
            return (self.total_output / self.paddy_input_quantity) * 100
        return 0.0

    def calculate_wastage_percentage(self):
        """Calculate wastage percentage"""
        if self.paddy_input_quantity and self.total_output:
            wastage = self.paddy_input_quantity - self.total_output
            return (wastage / self.paddy_input_quantity) * 100
        return 0.0

    def get_duration_hours(self):
        """Get production duration in hours"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return 0.0

    def get_production_rate(self):
        """Get production rate in kg/hour"""
        duration = self.get_duration_hours()
        if duration > 0:
            return self.total_output / duration
        return 0.0

    def analyze_performance(self):
        """AI-powered performance analysis"""
        analysis = {
            'efficiency_rating': 'good',
            'yield_rating': 'good',
            'quality_rating': 'good',
            'recommendations': []
        }
        
        # Efficiency analysis
        efficiency = self.calculate_efficiency_percentage()
        if efficiency < 85:
            analysis['efficiency_rating'] = 'poor'
            analysis['recommendations'].append({
                'type': 'efficiency',
                'message': f'Low efficiency ({efficiency:.1f}%). Check machine settings.',
                'priority': 'high'
            })
        elif efficiency < 90:
            analysis['efficiency_rating'] = 'average'
        
        # Yield analysis
        yield_pct = self.calculate_yield_percentage()
        if yield_pct < 65:
            analysis['yield_rating'] = 'poor'
            analysis['recommendations'].append({
                'type': 'yield',
                'message': f'Low yield ({yield_pct:.1f}%). Check paddy quality.',
                'priority': 'high'
            })
        elif yield_pct < 70:
            analysis['yield_rating'] = 'average'
        
        # Quality analysis
        if self.broken_percentage_output and self.broken_percentage_output > 10:
            analysis['quality_rating'] = 'poor'
            analysis['recommendations'].append({
                'type': 'quality',
                'message': f'High broken rice ({self.broken_percentage_output:.1f}%).',
                'priority': 'medium'
            })
        
        return analysis

    def update_totals(self):
        """Update calculated fields"""
        self.total_output = (self.rice_output or 0) + (self.broken_rice_output or 0) + \
                           (self.bran_output or 0) + (self.husk_output or 0)
        self.yield_percentage = self.calculate_yield_percentage()
        self.efficiency_percentage = self.calculate_efficiency_percentage()
        self.wastage_percentage = self.calculate_wastage_percentage()
        
        # Calculate total production cost
        self.total_production_cost = (self.labor_cost or 0) + (self.energy_cost or 0) + \
                                   (self.maintenance_cost or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'batch_number': self.batch_number,
            'paddy_stock_id': self.paddy_stock_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'machine_id': self.machine_id,
            'operator_id': self.operator_id,
            'shift': self.shift,
            'paddy_input_quantity': self.paddy_input_quantity,
            'paddy_variety': self.paddy_variety,
            'paddy_quality_grade': self.paddy_quality_grade,
            'rice_output': self.rice_output,
            'broken_rice_output': self.broken_rice_output,
            'bran_output': self.bran_output,
            'husk_output': self.husk_output,
            'total_output': self.total_output,
            'yield_percentage': self.yield_percentage,
            'efficiency_percentage': self.efficiency_percentage,
            'wastage_percentage': self.wastage_percentage,
            'output_quality_grade': self.output_quality_grade,
            'moisture_content_output': self.moisture_content_output,
            'broken_percentage_output': self.broken_percentage_output,
            'foreign_matter_output': self.foreign_matter_output,
            'machine_settings': self.get_machine_settings(),
            'machine_performance': self.get_machine_performance(),
            'status': self.status,
            'completion_percentage': self.completion_percentage,
            'predicted_yield': self.predicted_yield,
            'actual_vs_predicted': self.actual_vs_predicted,
            'optimization_suggestions': self.get_optimization_suggestions(),
            'anomaly_flags': self.get_anomaly_flags(),
            'labor_cost': self.labor_cost,
            'energy_cost': self.energy_cost,
            'maintenance_cost': self.maintenance_cost,
            'total_production_cost': self.total_production_cost,
            'duration_hours': self.get_duration_hours(),
            'production_rate': self.get_production_rate(),
            'performance_analysis': self.analyze_performance(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class QualityTest(db.Model):
    __tablename__ = 'quality_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.String(50), unique=True, nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batches.id'))
    sample_type = db.Column(db.String(20))  # input_paddy, output_rice, final_product
    
    # Test details
    test_date = db.Column(db.DateTime, nullable=False)
    tested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    test_method = db.Column(db.String(50))  # manual, automated, ai_vision
    
    # Quality parameters
    moisture_content = db.Column(db.Float)
    foreign_matter = db.Column(db.Float)
    broken_percentage = db.Column(db.Float)
    chalky_percentage = db.Column(db.Float)
    grain_length = db.Column(db.Float)
    grain_width = db.Column(db.Float)
    head_rice_percentage = db.Column(db.Float)
    
    # Grading
    grade = db.Column(db.String(10))  # A, B, C, D, E
    grade_confidence = db.Column(db.Float)  # AI confidence in grading
    
    # AI analysis
    ai_analysis_results = db.Column(db.Text)  # JSON string
    image_analysis_data = db.Column(db.Text)  # JSON string for computer vision results
    
    # Status
    status = db.Column(db.String(20), default='completed')  # pending, completed, verified
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verification_date = db.Column(db.DateTime)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    production_batch = relationship("ProductionBatch")
    tested_by_user = relationship("User", foreign_keys=[tested_by])
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    created_by_user = relationship("User", foreign_keys=[created_by])

    def get_ai_analysis_results(self):
        if self.ai_analysis_results:
            try:
                return json.loads(self.ai_analysis_results)
            except:
                return {}
        return {}

    def set_ai_analysis_results(self, results):
        self.ai_analysis_results = json.dumps(results)

    def get_image_analysis_data(self):
        if self.image_analysis_data:
            try:
                return json.loads(self.image_analysis_data)
            except:
                return {}
        return {}

    def set_image_analysis_data(self, data):
        self.image_analysis_data = json.dumps(data)

    def calculate_quality_score(self):
        """Calculate overall quality score"""
        scores = {}
        
        # Moisture content score (optimal: 14%)
        if self.moisture_content:
            scores['moisture'] = max(0, 100 - abs(self.moisture_content - 14) * 5)
        
        # Foreign matter score (lower is better)
        if self.foreign_matter:
            scores['foreign_matter'] = max(0, 100 - self.foreign_matter * 20)
        
        # Broken percentage score (lower is better)
        if self.broken_percentage:
            scores['broken'] = max(0, 100 - self.broken_percentage * 2)
        
        # Chalky percentage score (lower is better)
        if self.chalky_percentage:
            scores['chalky'] = max(0, 100 - self.chalky_percentage * 3)
        
        # Head rice percentage score (higher is better)
        if self.head_rice_percentage:
            scores['head_rice'] = min(100, self.head_rice_percentage)
        
        if scores:
            return sum(scores.values()) / len(scores)
        return 0.0

    def determine_grade(self):
        """AI-powered grade determination"""
        quality_score = self.calculate_quality_score()
        
        if quality_score >= 90:
            return 'A'
        elif quality_score >= 80:
            return 'B'
        elif quality_score >= 70:
            return 'C'
        elif quality_score >= 60:
            return 'D'
        else:
            return 'E'

    def get_quality_recommendations(self):
        """Get quality improvement recommendations"""
        recommendations = []
        
        if self.moisture_content and self.moisture_content > 14:
            recommendations.append({
                'parameter': 'moisture_content',
                'message': f'Moisture content ({self.moisture_content}%) is high. Improve drying.',
                'priority': 'high'
            })
        
        if self.foreign_matter and self.foreign_matter > 2:
            recommendations.append({
                'parameter': 'foreign_matter',
                'message': f'Foreign matter ({self.foreign_matter}%) exceeds limit. Improve cleaning.',
                'priority': 'medium'
            })
        
        if self.broken_percentage and self.broken_percentage > 10:
            recommendations.append({
                'parameter': 'broken_percentage',
                'message': f'High broken rice ({self.broken_percentage}%). Check milling settings.',
                'priority': 'medium'
            })
        
        return recommendations

    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'batch_id': self.batch_id,
            'sample_type': self.sample_type,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'tested_by': self.tested_by,
            'test_method': self.test_method,
            'moisture_content': self.moisture_content,
            'foreign_matter': self.foreign_matter,
            'broken_percentage': self.broken_percentage,
            'chalky_percentage': self.chalky_percentage,
            'grain_length': self.grain_length,
            'grain_width': self.grain_width,
            'head_rice_percentage': self.head_rice_percentage,
            'grade': self.grade or self.determine_grade(),
            'grade_confidence': self.grade_confidence,
            'quality_score': self.calculate_quality_score(),
            'ai_analysis_results': self.get_ai_analysis_results(),
            'image_analysis_data': self.get_image_analysis_data(),
            'status': self.status,
            'verified_by': self.verified_by,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'quality_recommendations': self.get_quality_recommendations(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
