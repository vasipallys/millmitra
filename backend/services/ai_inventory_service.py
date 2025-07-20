import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.inventory import PaddyStock, ProductStock, InventoryTransaction
from models.production import ProductionBatch
import statistics

class AIInventoryService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def generate_dashboard_insights(self, dashboard_data: Dict):
        """Generate AI insights for inventory dashboard"""
        insights = []
        
        # Stock level insights
        total_value = dashboard_data.get('total_inventory_value', 0)
        if total_value > 5000000:  # 50 lakhs
            insights.append({
                'type': 'info',
                'title': 'High Inventory Value',
                'message': f'Current inventory value is ₹{total_value:,.0f}. Consider optimizing stock levels.',
                'priority': 'medium'
            })
        
        # Low stock alerts
        low_stock_items = dashboard_data.get('low_stock_items', [])
        if len(low_stock_items) > 5:
            insights.append({
                'type': 'warning',
                'title': 'Multiple Low Stock Items',
                'message': f'{len(low_stock_items)} items are below reorder point.',
                'priority': 'high'
            })
        
        # Aging stock insights
        aging_stock = dashboard_data.get('aging_stock_value', 0)
        if aging_stock > total_value * 0.15:  # More than 15% aging
            insights.append({
                'type': 'warning',
                'title': 'High Aging Stock',
                'message': f'₹{aging_stock:,.0f} worth of stock is aging. Consider promotional sales.',
                'priority': 'high'
            })
        
        return insights
    
    def get_stock_optimization_suggestions(self):
        """AI-powered stock optimization suggestions"""
        suggestions = [
            {
                'category': 'reorder_optimization',
                'title': 'Optimize Reorder Points',
                'description': 'AI analysis suggests adjusting reorder points for 12 items',
                'potential_savings': 150000,
                'implementation_effort': 'low'
            },
            {
                'category': 'storage_optimization',
                'title': 'Storage Space Optimization',
                'description': 'Reorganize storage to improve space utilization by 15%',
                'potential_savings': 75000,
                'implementation_effort': 'medium'
            },
            {
                'category': 'demand_forecasting',
                'title': 'Improve Demand Forecasting',
                'description': 'Implement AI demand forecasting to reduce stockouts by 25%',
                'potential_savings': 200000,
                'implementation_effort': 'high'
            }
        ]
        
        return suggestions
    
    def analyze_paddy_stock_levels(self, stocks: List[Dict]):
        """AI analysis of paddy stock levels"""
        analysis = {
            'overall_status': 'optimal',
            'variety_analysis': {},
            'recommendations': [],
            'risk_factors': []
        }
        
        if not stocks:
            return analysis
        
        # Group by variety
        variety_stocks = {}
        for stock in stocks:
            variety = stock.get('variety', 'Unknown')
            if variety not in variety_stocks:
                variety_stocks[variety] = []
            variety_stocks[variety].append(stock)
        
        # Analyze each variety
        for variety, variety_stock_list in variety_stocks.items():
            total_quantity = sum(s.get('quantity', 0) for s in variety_stock_list)
            avg_age_days = statistics.mean([s.get('age_days', 0) for s in variety_stock_list])
            
            variety_analysis = {
                'total_quantity': total_quantity,
                'average_age_days': avg_age_days,
                'stock_status': 'normal'
            }
            
            # Determine stock status
            if total_quantity < 1000:  # Less than 1 ton
                variety_analysis['stock_status'] = 'low'
                analysis['recommendations'].append(f'Reorder {variety} paddy - stock below minimum level')
            elif total_quantity > 10000:  # More than 10 tons
                variety_analysis['stock_status'] = 'high'
                analysis['recommendations'].append(f'Consider processing {variety} paddy - high stock level')
            
            # Age analysis
            if avg_age_days > 90:
                analysis['risk_factors'].append(f'{variety} paddy aging - average age {avg_age_days:.0f} days')
            
            analysis['variety_analysis'][variety] = variety_analysis
        
        # Overall status determination
        low_stock_varieties = [v for v, a in analysis['variety_analysis'].items() if a['stock_status'] == 'low']
        if len(low_stock_varieties) > 2:
            analysis['overall_status'] = 'critical'
        elif len(low_stock_varieties) > 0:
            analysis['overall_status'] = 'attention_needed'
        
        return analysis
    
    def predict_paddy_demand(self, variety: str):
        """AI prediction of paddy demand"""
        try:
            response = requests.post(f"{self.ai_service_url}/inventory/predict-paddy-demand", 
                                   json={'variety': variety})
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_demand_prediction(variety)
    
    def assess_paddy_quality(self, paddy_data: Dict):
        """AI quality assessment of incoming paddy"""
        assessment = {
            'quality_score': 0.0,
            'quality_grade': 'B',
            'quality_factors': [],
            'storage_recommendations': [],
            'price_adjustment': 0.0
        }
        
        # Moisture content assessment
        moisture_content = paddy_data.get('moisture_content', 14.0)
        if moisture_content <= 12.0:
            assessment['quality_score'] += 0.3
            assessment['quality_factors'].append('Excellent moisture content')
        elif moisture_content <= 14.0:
            assessment['quality_score'] += 0.2
            assessment['quality_factors'].append('Good moisture content')
        else:
            assessment['quality_factors'].append('High moisture content - requires drying')
            assessment['storage_recommendations'].append('Immediate drying required')
            assessment['price_adjustment'] -= 0.05
        
        # Foreign matter assessment
        foreign_matter = paddy_data.get('foreign_matter_percentage', 2.0)
        if foreign_matter <= 1.0:
            assessment['quality_score'] += 0.25
            assessment['quality_factors'].append('Low foreign matter')
        elif foreign_matter <= 3.0:
            assessment['quality_score'] += 0.15
            assessment['quality_factors'].append('Acceptable foreign matter')
        else:
            assessment['quality_factors'].append('High foreign matter content')
            assessment['price_adjustment'] -= 0.03
        
        # Broken grain assessment
        broken_percentage = paddy_data.get('broken_percentage', 5.0)
        if broken_percentage <= 3.0:
            assessment['quality_score'] += 0.2
            assessment['quality_factors'].append('Low broken grain percentage')
        elif broken_percentage <= 7.0:
            assessment['quality_score'] += 0.1
            assessment['quality_factors'].append('Acceptable broken grain percentage')
        else:
            assessment['quality_factors'].append('High broken grain percentage')
            assessment['price_adjustment'] -= 0.02
        
        # Determine quality grade
        if assessment['quality_score'] >= 0.6:
            assessment['quality_grade'] = 'A'
        elif assessment['quality_score'] >= 0.4:
            assessment['quality_grade'] = 'B'
        else:
            assessment['quality_grade'] = 'C'
        
        # Storage recommendations
        if moisture_content > 14.0:
            assessment['storage_recommendations'].append('Store in dry, well-ventilated area')
        if foreign_matter > 3.0:
            assessment['storage_recommendations'].append('Clean before storage')
        
        return assessment
    
    def optimize_storage_location(self, stock_data: Dict):
        """AI optimization of storage location"""
        optimization = {
            'recommended_location': 'Warehouse A',
            'storage_type': 'bulk',
            'storage_conditions': [],
            'capacity_utilization': 0.75,
            'accessibility_score': 0.8
        }
        
        variety = stock_data.get('variety', '')
        quantity = stock_data.get('quantity', 0)
        quality_grade = stock_data.get('quality_grade', 'B')
        
        # Location optimization based on variety
        if 'basmati' in variety.lower():
            optimization['recommended_location'] = 'Premium Storage'
            optimization['storage_conditions'].append('Climate controlled')
        elif quality_grade == 'A':
            optimization['recommended_location'] = 'Warehouse A'
        else:
            optimization['recommended_location'] = 'Warehouse B'
        
        # Storage type based on quantity
        if quantity > 5000:  # More than 5 tons
            optimization['storage_type'] = 'bulk'
        else:
            optimization['storage_type'] = 'bagged'
        
        # Storage conditions
        moisture_content = stock_data.get('moisture_content', 14.0)
        if moisture_content > 14.0:
            optimization['storage_conditions'].append('Immediate drying required')
        
        optimization['storage_conditions'].append('Regular pest monitoring')
        optimization['storage_conditions'].append('Temperature monitoring')
        
        return optimization
    
    def recommend_purchase_price(self, paddy_data: Dict):
        """AI recommendation for paddy purchase price"""
        base_price = 2500  # Base price per quintal
        
        recommendation = {
            'recommended_price': base_price,
            'price_factors': [],
            'market_comparison': {},
            'negotiation_points': []
        }
        
        # Quality adjustments
        quality_grade = paddy_data.get('quality_grade', 'B')
        if quality_grade == 'A':
            recommendation['recommended_price'] += 200
            recommendation['price_factors'].append('Premium quality (+₹200)')
        elif quality_grade == 'C':
            recommendation['recommended_price'] -= 150
            recommendation['price_factors'].append('Lower quality (-₹150)')
        
        # Variety premium
        variety = paddy_data.get('variety', '').lower()
        if 'basmati' in variety:
            recommendation['recommended_price'] += 500
            recommendation['price_factors'].append('Basmati variety (+₹500)')
        
        # Quantity discount
        quantity = paddy_data.get('quantity', 0)
        if quantity > 10000:  # More than 100 quintals
            discount = min(100, quantity // 1000 * 10)
            recommendation['recommended_price'] -= discount
            recommendation['price_factors'].append(f'Volume discount (-₹{discount})')
        
        # Market comparison (simulated)
        recommendation['market_comparison'] = {
            'local_average': base_price + 50,
            'regional_average': base_price + 25,
            'our_price': recommendation['recommended_price']
        }
        
        # Negotiation points
        if paddy_data.get('moisture_content', 14.0) > 14.0:
            recommendation['negotiation_points'].append('High moisture content - request drying cost adjustment')
        
        if paddy_data.get('foreign_matter_percentage', 2.0) > 3.0:
            recommendation['negotiation_points'].append('High foreign matter - request cleaning cost adjustment')
        
        return recommendation
    
    def analyze_product_stock_levels(self, stocks: List[Dict]):
        """AI analysis of product stock levels"""
        analysis = {
            'overall_health': 'good',
            'product_analysis': {},
            'turnover_analysis': {},
            'recommendations': []
        }
        
        if not stocks:
            return analysis
        
        # Group by product type
        product_stocks = {}
        for stock in stocks:
            product_type = stock.get('product_type', 'Unknown')
            if product_type not in product_stocks:
                product_stocks[product_type] = []
            product_stocks[product_type].append(stock)
        
        # Analyze each product type
        for product_type, product_stock_list in product_stocks.items():
            total_quantity = sum(s.get('quantity', 0) for s in product_stock_list)
            total_value = sum(s.get('value', 0) for s in product_stock_list)
            avg_age = statistics.mean([s.get('age_days', 0) for s in product_stock_list])
            
            # Calculate turnover (simplified)
            monthly_sales = sum(s.get('monthly_sales', 0) for s in product_stock_list)
            turnover_ratio = monthly_sales / total_quantity if total_quantity > 0 else 0
            
            product_analysis = {
                'total_quantity': total_quantity,
                'total_value': total_value,
                'average_age_days': avg_age,
                'turnover_ratio': turnover_ratio,
                'stock_status': 'normal'
            }
            
            # Determine stock status
            if turnover_ratio < 0.1:  # Less than 10% monthly turnover
                product_analysis['stock_status'] = 'slow_moving'
                analysis['recommendations'].append(f'Consider promotional pricing for {product_type}')
            elif turnover_ratio > 0.5:  # More than 50% monthly turnover
                product_analysis['stock_status'] = 'fast_moving'
                analysis['recommendations'].append(f'Increase stock levels for {product_type}')
            
            analysis['product_analysis'][product_type] = product_analysis
        
        return analysis
    
    def analyze_sales_velocity(self, product_type: str, grade: str):
        """AI analysis of sales velocity"""
        velocity_analysis = {
            'current_velocity': 0.0,
            'velocity_trend': 'stable',
            'seasonal_factors': [],
            'predictions': {}
        }
        
        # Simulated velocity calculation
        base_velocity = 0.25  # 25% per month
        
        # Adjust for product type
        if product_type.lower() == 'basmati':
            base_velocity *= 1.2
        elif product_type.lower() == 'broken':
            base_velocity *= 0.8
        
        # Adjust for grade
        if grade == 'A':
            base_velocity *= 1.1
        elif grade == 'C':
            base_velocity *= 0.9
        
        velocity_analysis['current_velocity'] = base_velocity
        
        # Seasonal factors
        current_month = datetime.now().month
        if current_month in [10, 11, 12]:  # Festival season
            velocity_analysis['seasonal_factors'].append('Festival season - increased demand')
            velocity_analysis['velocity_trend'] = 'increasing'
        elif current_month in [6, 7, 8]:  # Monsoon season
            velocity_analysis['seasonal_factors'].append('Monsoon season - stable demand')
        
        # Predictions
        velocity_analysis['predictions'] = {
            'next_month': base_velocity * 1.05,
            'next_quarter': base_velocity * 0.95,
            'stock_out_risk': 'low' if base_velocity < 0.3 else 'medium' if base_velocity < 0.5 else 'high'
        }
        
        return velocity_analysis
    
    def validate_transaction(self, transaction_data: Dict):
        """AI validation of inventory transaction"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Basic validation
        if not transaction_data.get('transaction_type'):
            validation['errors'].append('Transaction type is required')
        
        if not transaction_data.get('quantity') or transaction_data['quantity'] <= 0:
            validation['errors'].append('Valid quantity is required')
        
        # Stock availability check for outbound transactions
        if transaction_data.get('transaction_type') in ['sale', 'transfer_out', 'production_use']:
            available_quantity = transaction_data.get('available_quantity', 0)
            requested_quantity = transaction_data.get('quantity', 0)
            
            if requested_quantity > available_quantity:
                validation['errors'].append(f'Insufficient stock. Available: {available_quantity}, Requested: {requested_quantity}')
        
        # Price validation
        unit_price = transaction_data.get('unit_price', 0)
        if unit_price <= 0:
            validation['warnings'].append('Unit price not specified or invalid')
        
        # Date validation
        transaction_date = transaction_data.get('transaction_date')
        if transaction_date:
            try:
                trans_date = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
                if trans_date > datetime.now():
                    validation['warnings'].append('Transaction date is in the future')
            except:
                validation['errors'].append('Invalid transaction date format')
        
        validation['valid'] = len(validation['errors']) == 0
        return validation
    
    def analyze_transaction_impact(self, transaction_data: Dict):
        """AI analysis of transaction impact"""
        impact = {
            'stock_impact': {},
            'financial_impact': {},
            'operational_impact': {},
            'recommendations': []
        }
        
        quantity = transaction_data.get('quantity', 0)
        unit_price = transaction_data.get('unit_price', 0)
        transaction_type = transaction_data.get('transaction_type', '')
        
        # Stock impact
        if transaction_type in ['purchase', 'transfer_in', 'production_output']:
            impact['stock_impact']['type'] = 'increase'
            impact['stock_impact']['quantity_change'] = quantity
        else:
            impact['stock_impact']['type'] = 'decrease'
            impact['stock_impact']['quantity_change'] = -quantity
        
        # Financial impact
        total_value = quantity * unit_price
        impact['financial_impact']['value_change'] = total_value if impact['stock_impact']['type'] == 'increase' else -total_value
        impact['financial_impact']['inventory_value_impact'] = impact['financial_impact']['value_change']
        
        # Operational impact
        if transaction_type == 'sale':
            impact['operational_impact']['revenue_generated'] = total_value
            impact['recommendations'].append('Update customer order status')
        elif transaction_type == 'purchase':
            impact['operational_impact']['procurement_cost'] = total_value
            impact['recommendations'].append('Update supplier payment schedule')
        
        # Reorder point check
        remaining_quantity = transaction_data.get('remaining_quantity_after', 0)
        reorder_point = transaction_data.get('reorder_point', 0)
        
        if remaining_quantity <= reorder_point:
            impact['recommendations'].append('Stock level below reorder point - initiate procurement')
        
        return impact
    
    def detect_transaction_fraud(self, transaction_data: Dict):
        """AI fraud detection for transactions"""
        fraud_check = {
            'is_suspicious': False,
            'risk_score': 0.0,
            'indicators': []
        }
        
        # Unusual quantity check
        quantity = transaction_data.get('quantity', 0)
        avg_quantity = transaction_data.get('average_quantity', 1000)
        
        if quantity > avg_quantity * 5:  # More than 5x average
            fraud_check['risk_score'] += 0.3
            fraud_check['indicators'].append('Unusually large quantity')
        
        # Price anomaly check
        unit_price = transaction_data.get('unit_price', 0)
        market_price = transaction_data.get('market_price', 0)
        
        if market_price > 0:
            price_deviation = abs(unit_price - market_price) / market_price
            if price_deviation > 0.2:  # More than 20% deviation
                fraud_check['risk_score'] += 0.4
                fraud_check['indicators'].append('Price significantly different from market rate')
        
        # Time-based anomaly
        transaction_hour = datetime.now().hour
        if transaction_hour < 6 or transaction_hour > 22:  # Outside business hours
            fraud_check['risk_score'] += 0.2
            fraud_check['indicators'].append('Transaction outside normal business hours')
        
        # User behavior check
        user_id = transaction_data.get('user_id')
        recent_transactions = transaction_data.get('user_recent_transactions', 0)
        
        if recent_transactions > 10:  # More than 10 transactions today
            fraud_check['risk_score'] += 0.1
            fraud_check['indicators'].append('High transaction frequency for user')
        
        fraud_check['is_suspicious'] = fraud_check['risk_score'] > 0.5
        return fraud_check
    
    def calculate_optimal_reorder_points(self):
        """AI calculation of optimal reorder points"""
        reorder_points = []
        
        # Simulated calculation for different products
        products = [
            {'product': 'Basmati Rice', 'current_reorder': 1000, 'optimal_reorder': 1200},
            {'product': 'Regular Rice', 'current_reorder': 2000, 'optimal_reorder': 1800},
            {'product': 'Broken Rice', 'current_reorder': 500, 'optimal_reorder': 600},
            {'product': 'Rice Bran', 'current_reorder': 300, 'optimal_reorder': 400}
        ]
        
        for product in products:
            reorder_point = {
                'product': product['product'],
                'current_reorder_point': product['current_reorder'],
                'ai_recommended_reorder_point': product['optimal_reorder'],
                'change_percentage': ((product['optimal_reorder'] - product['current_reorder']) / product['current_reorder']) * 100,
                'reasoning': self._get_reorder_reasoning(product),
                'confidence': 0.85
            }
            reorder_points.append(reorder_point)
        
        return reorder_points
    
    def forecast_demand(self, product_type: str, days: int):
        """AI demand forecasting"""
        forecast = {
            'product_type': product_type,
            'forecast_period_days': days,
            'daily_forecast': [],
            'total_predicted_demand': 0,
            'confidence_interval': {'lower': 0, 'upper': 0},
            'seasonal_factors': [],
            'trend_analysis': 'stable'
        }
        
        # Generate daily forecast (simplified)
        base_daily_demand = 100  # Base daily demand
        
        # Adjust for product type
        if 'basmati' in product_type.lower():
            base_daily_demand *= 1.5
        elif 'broken' in product_type.lower():
            base_daily_demand *= 0.7
        
        total_demand = 0
        for day in range(days):
            # Add some randomness and seasonal variation
            seasonal_factor = 1.0
            if (day % 7) in [5, 6]:  # Weekend
                seasonal_factor = 1.2
            
            daily_demand = base_daily_demand * seasonal_factor * (0.8 + 0.4 * np.random.random())
            forecast['daily_forecast'].append({
                'day': day + 1,
                'predicted_demand': round(daily_demand, 2),
                'confidence': 0.8
            })
            total_demand += daily_demand
        
        forecast['total_predicted_demand'] = round(total_demand, 2)
        forecast['confidence_interval'] = {
            'lower': round(total_demand * 0.85, 2),
            'upper': round(total_demand * 1.15, 2)
        }
        
        return forecast
    
    def analyze_seasonal_patterns(self, product_type: str):
        """AI analysis of seasonal demand patterns"""
        patterns = {
            'product_type': product_type,
            'seasonal_peaks': [],
            'seasonal_lows': [],
            'monthly_factors': {},
            'recommendations': []
        }
        
        # Simulated seasonal analysis
        if 'basmati' in product_type.lower():
            patterns['seasonal_peaks'] = ['October', 'November', 'December']
            patterns['seasonal_lows'] = ['June', 'July']
            patterns['recommendations'].append('Stock up before festival season')
        else:
            patterns['seasonal_peaks'] = ['April', 'May']
            patterns['seasonal_lows'] = ['August', 'September']
            patterns['recommendations'].append('Maintain steady stock levels')
        
        # Monthly factors (1.0 = average)
        patterns['monthly_factors'] = {
            'January': 0.9, 'February': 0.85, 'March': 0.95, 'April': 1.1,
            'May': 1.15, 'June': 0.8, 'July': 0.75, 'August': 0.7,
            'September': 0.8, 'October': 1.3, 'November': 1.4, 'December': 1.35
        }
        
        return patterns
    
    def _fallback_demand_prediction(self, variety: str):
        """Fallback demand prediction when AI service is unavailable"""
        base_demand = 1000  # Base monthly demand in kg
        
        # Adjust for variety
        if 'basmati' in variety.lower():
            base_demand *= 1.5
        elif 'broken' in variety.lower():
            base_demand *= 0.8
        
        return {
            'variety': variety,
            'predicted_monthly_demand': base_demand,
            'confidence': 0.6,
            'factors': ['Historical average', 'Variety adjustment']
        }
    
    def _get_reorder_reasoning(self, product: Dict):
        """Get reasoning for reorder point recommendation"""
        current = product['current_reorder']
        optimal = product['optimal_reorder']
        
        if optimal > current:
            return f"Increase recommended due to higher demand velocity and longer lead times"
        elif optimal < current:
            return f"Decrease recommended due to improved supply chain efficiency"
        else:
            return "Current reorder point is optimal"
