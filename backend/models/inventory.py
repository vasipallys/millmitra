"""
Inventory Management Models
"""

from datetime import datetime, timedelta
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class PaddyStock(db.Model):
    __tablename__ = 'paddy_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Purchase details
    purchase_date = db.Column(db.DateTime, nullable=False)
    variety = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in kg
    purchase_price = db.Column(db.Float, nullable=False)  # per kg
    total_amount = db.Column(db.Float, nullable=False)
    
    # Quality parameters
    moisture_content = db.Column(db.Float)
    foreign_matter = db.Column(db.Float)
    broken_percentage = db.Column(db.Float)
    chalky_percentage = db.Column(db.Float)
    grain_length = db.Column(db.Float)
    grain_width = db.Column(db.Float)
    quality_grade = db.Column(db.String(10))
    
    # Storage information
    warehouse_id = db.Column(db.String(20))
    bin_number = db.Column(db.String(20))
    storage_conditions = db.Column(db.Text)  # JSON string
    
    # Processing status
    status = db.Column(db.String(20), default='stored')  # stored, processing, processed, sold
    processed_quantity = db.Column(db.Float, default=0.0)
    remaining_quantity = db.Column(db.Float)
    
    # AI predictions
    predicted_yield = db.Column(db.Float)  # AI-predicted rice yield
    quality_degradation_rate = db.Column(db.Float)  # AI-predicted degradation
    optimal_processing_date = db.Column(db.DateTime)  # AI-suggested processing date
    market_value_prediction = db.Column(db.Float)  # AI-predicted market value
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farmer = relationship("Farmer")
    created_by_user = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.remaining_quantity is None:
            self.remaining_quantity = self.quantity

    def get_storage_conditions(self):
        if self.storage_conditions:
            try:
                return json.loads(self.storage_conditions)
            except:
                return {}
        return {}

    def set_storage_conditions(self, conditions):
        self.storage_conditions = json.dumps(conditions)

    def get_age_days(self):
        """Get age of stock in days"""
        return (datetime.utcnow() - self.purchase_date).days

    def is_aging(self, threshold_days=30):
        """Check if stock is aging beyond threshold"""
        return self.get_age_days() > threshold_days

    def get_quality_score(self):
        """Calculate overall quality score"""
        scores = {
            'moisture': max(0, 100 - abs((self.moisture_content or 14) - 14) * 5),
            'foreign_matter': max(0, 100 - (self.foreign_matter or 0) * 20),
            'broken': max(0, 100 - (self.broken_percentage or 0) * 2),
            'chalky': max(0, 100 - (self.chalky_percentage or 0) * 3)
        }
        return sum(scores.values()) / len(scores)

    def predict_quality_degradation(self):
        """AI-powered quality degradation prediction"""
        base_degradation = 0.1  # 0.1% per day base rate
        
        # Factors affecting degradation
        moisture_factor = max(1.0, (self.moisture_content or 14) / 14)
        age_factor = 1 + (self.get_age_days() / 365) * 0.5
        storage_factor = 1.0  # Would be calculated from storage conditions
        
        daily_degradation = base_degradation * moisture_factor * age_factor * storage_factor
        return daily_degradation

    def get_storage_recommendations(self):
        """AI-powered storage recommendations"""
        recommendations = []
        
        if self.moisture_content and self.moisture_content > 14:
            recommendations.append({
                'type': 'warning',
                'message': f'High moisture content ({self.moisture_content}%). Consider drying.',
                'priority': 'high'
            })
        
        if self.is_aging(30):
            recommendations.append({
                'type': 'alert',
                'message': f'Stock is {self.get_age_days()} days old. Consider processing soon.',
                'priority': 'medium'
            })
        
        if self.foreign_matter and self.foreign_matter > 2:
            recommendations.append({
                'type': 'info',
                'message': f'High foreign matter ({self.foreign_matter}%). Clean before processing.',
                'priority': 'low'
            })
        
        return recommendations

    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'farmer_id': self.farmer_id,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'variety': self.variety,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'total_amount': self.total_amount,
            'moisture_content': self.moisture_content,
            'foreign_matter': self.foreign_matter,
            'broken_percentage': self.broken_percentage,
            'chalky_percentage': self.chalky_percentage,
            'grain_length': self.grain_length,
            'grain_width': self.grain_width,
            'quality_grade': self.quality_grade,
            'warehouse_id': self.warehouse_id,
            'bin_number': self.bin_number,
            'storage_conditions': self.get_storage_conditions(),
            'status': self.status,
            'processed_quantity': self.processed_quantity,
            'remaining_quantity': self.remaining_quantity,
            'predicted_yield': self.predicted_yield,
            'quality_degradation_rate': self.quality_degradation_rate,
            'optimal_processing_date': self.optimal_processing_date.isoformat() if self.optimal_processing_date else None,
            'market_value_prediction': self.market_value_prediction,
            'age_days': self.get_age_days(),
            'quality_score': self.get_quality_score(),
            'storage_recommendations': self.get_storage_recommendations(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Frontend StockCard aliases
            'product_name': f"{self.variety or 'Paddy'} ({self.quality_grade or 'N/A'})",
            'current_stock': self.remaining_quantity if self.remaining_quantity is not None else self.quantity,
            'reorder_level': 100,
            'max_stock': self.quantity,
            'unit': 'kg',
            'category': 'paddy',
            'last_updated': self.updated_at.isoformat() if self.updated_at else None
        }

class ProductStock(db.Model):
    __tablename__ = 'product_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)  # rice, broken_rice, bran, husk
    variety = db.Column(db.String(50))
    grade = db.Column(db.String(10))
    
    # Stock details
    quantity = db.Column(db.Float, nullable=False)  # in kg
    unit_cost = db.Column(db.Float)  # production cost per kg
    market_price = db.Column(db.Float)  # current market price per kg
    
    # Inventory management
    minimum_stock_level = db.Column(db.Float, default=0.0)
    maximum_stock_level = db.Column(db.Float, default=0.0)
    reorder_point = db.Column(db.Float, default=0.0)
    
    # Storage information
    warehouse_id = db.Column(db.String(20))
    storage_location = db.Column(db.String(50))
    packaging_type = db.Column(db.String(50))  # bulk, 25kg_bag, 50kg_bag
    
    # Quality and expiry
    production_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    quality_parameters = db.Column(db.Text)  # JSON string
    
    # AI insights
    demand_forecast = db.Column(db.Float)  # AI-predicted demand
    optimal_price = db.Column(db.Float)  # AI-suggested optimal price
    turnover_prediction = db.Column(db.Float)  # AI-predicted turnover rate
    
    # Status
    status = db.Column(db.String(20), default='available')  # available, reserved, sold, expired
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")

    def get_quality_parameters(self):
        if self.quality_parameters:
            try:
                return json.loads(self.quality_parameters)
            except:
                return {}
        return {}

    def set_quality_parameters(self, parameters):
        self.quality_parameters = json.dumps(parameters)

    def is_low_stock(self):
        """Check if stock is below minimum level"""
        return self.quantity <= self.minimum_stock_level

    def is_near_expiry(self, days_threshold=30):
        """Check if product is near expiry"""
        if not self.expiry_date:
            return False
        days_to_expiry = (self.expiry_date - datetime.utcnow()).days
        return days_to_expiry <= days_threshold

    def get_stock_status(self):
        """Get comprehensive stock status"""
        status = {
            'level': 'normal',
            'alerts': []
        }
        
        if self.is_low_stock():
            status['level'] = 'low'
            status['alerts'].append({
                'type': 'stock_low',
                'message': f'Stock below minimum level ({self.minimum_stock_level} kg)',
                'priority': 'high'
            })
        
        if self.is_near_expiry():
            status['alerts'].append({
                'type': 'near_expiry',
                'message': f'Product expires on {self.expiry_date.strftime("%Y-%m-%d")}',
                'priority': 'medium'
            })
        
        if self.quantity == 0:
            status['level'] = 'out_of_stock'
            status['alerts'].append({
                'type': 'out_of_stock',
                'message': 'Product is out of stock',
                'priority': 'critical'
            })
        
        return status

    def calculate_turnover_rate(self):
        """Calculate inventory turnover rate"""
        # This would be calculated based on sales history
        # For now, return a placeholder
        return self.turnover_prediction or 0.0

    def get_pricing_recommendations(self):
        """AI-powered pricing recommendations"""
        recommendations = []
        
        if self.market_price and self.unit_cost:
            margin = ((self.market_price - self.unit_cost) / self.unit_cost) * 100
            
            if margin < 10:
                recommendations.append({
                    'type': 'pricing',
                    'message': f'Low margin ({margin:.1f}%). Consider price adjustment.',
                    'suggested_price': self.unit_cost * 1.15,
                    'priority': 'medium'
                })
        
        if self.is_near_expiry():
            recommendations.append({
                'type': 'clearance',
                'message': 'Consider clearance pricing due to approaching expiry.',
                'suggested_discount': 15,
                'priority': 'high'
            })
        
        return recommendations

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'variety': self.variety,
            'grade': self.grade,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'market_price': self.market_price,
            'minimum_stock_level': self.minimum_stock_level,
            'maximum_stock_level': self.maximum_stock_level,
            'reorder_point': self.reorder_point,
            'warehouse_id': self.warehouse_id,
            'storage_location': self.storage_location,
            'packaging_type': self.packaging_type,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quality_parameters': self.get_quality_parameters(),
            'demand_forecast': self.demand_forecast,
            'optimal_price': self.optimal_price,
            'turnover_prediction': self.turnover_prediction,
            'status': self.status,
            'stock_status': self.get_stock_status(),
            'pricing_recommendations': self.get_pricing_recommendations(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Frontend StockCard aliases
            'current_stock': self.quantity,
            'reorder_level': self.reorder_point or self.minimum_stock_level or 0,
            'max_stock': self.maximum_stock_level or 0,
            'unit': 'kg',
            'category': self.product_type,
            'last_updated': self.updated_at.isoformat() if self.updated_at else None
        }


class StockMovement(db.Model):
    """Persisted inventory in/out/transfer against a paddy or product lot."""
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    stock_kind = db.Column(db.String(20), nullable=False)  # paddy, product
    stock_id = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, transfer
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    total_value = db.Column(db.Float)
    reference_type = db.Column(db.String(80))
    reference_number = db.Column(db.String(80))
    reason = db.Column(db.String(120))
    notes = db.Column(db.Text)
    location_from = db.Column(db.String(80))
    location_to = db.Column(db.String(80))
    variety = db.Column(db.String(80))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'stock_kind': self.stock_kind,
            'item_type': self.stock_kind,
            'stock_id': self.stock_id,
            'movement_type': self.movement_type,
            'type': self.movement_type,
            'quantity': self.quantity,
            'unit': 'kg',
            'unit_price': self.unit_price,
            'total_value': self.total_value,
            'reference_type': self.reference_type or self.reason,
            'reference_number': self.reference_number,
            'reference': self.reference_number,
            'reason': self.reason,
            'notes': self.notes,
            'location_from': self.location_from,
            'location_to': self.location_to,
            'variety': self.variety,
            'status': 'completed',
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'date': self.created_at.isoformat() if self.created_at else None,
        }
