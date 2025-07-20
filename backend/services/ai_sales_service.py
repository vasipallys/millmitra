import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.sales import SalesOrder, SalesQuote
from models.customer import Customer
from models.inventory import ProductStock
import statistics
import math

class AISalesService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def validate_sales_order(self, order_data: Dict):
        """AI validation of sales order data"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Required fields validation
        required_fields = ['customer_id', 'items', 'delivery_date']
        for field in required_fields:
            if not order_data.get(field):
                validation['errors'].append(f'{field.replace("_", " ").title()} is required')
        
        # Items validation
        items = order_data.get('items', [])
        if not items:
            validation['errors'].append('Order must contain at least one item')
        
        total_value = 0
        for item in items:
            if not item.get('product_id') or not item.get('quantity'):
                validation['errors'].append('Each item must have product_id and quantity')
            
            quantity = item.get('quantity', 0)
            price = item.get('unit_price', 0)
            
            if quantity <= 0:
                validation['errors'].append('Item quantity must be greater than 0')
            
            if price <= 0:
                validation['warnings'].append('Item price not set or zero')
            
            total_value += quantity * price
        
        # Order value validation
        if total_value > 10000000:  # 1 crore
            validation['warnings'].append('High value order - requires approval')
        
        # Delivery date validation
        delivery_date = order_data.get('delivery_date')
        if delivery_date:
            try:
                delivery_dt = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                if delivery_dt < datetime.now():
                    validation['errors'].append('Delivery date cannot be in the past')
                elif delivery_dt < datetime.now() + timedelta(days=1):
                    validation['warnings'].append('Very short delivery timeline')
            except:
                validation['errors'].append('Invalid delivery date format')
        
        validation['valid'] = len(validation['errors']) == 0
        return validation
    
    def optimize_order_pricing(self, order_data: Dict):
        """AI optimization of order pricing"""
        try:
            response = requests.post(f"{self.ai_service_url}/sales/optimize-pricing", json=order_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_pricing_optimization(order_data)
    
    def analyze_inventory_availability(self, order_data: Dict):
        """AI analysis of inventory availability for order"""
        availability_analysis = {
            'available': True,
            'items_analysis': [],
            'alternatives': [],
            'recommendations': []
        }
        
        items = order_data.get('items', [])
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            # Simulate inventory check
            item_analysis = {
                'product_id': product_id,
                'requested_quantity': quantity,
                'available_quantity': quantity + 100,  # Simulated
                'status': 'available',
                'lead_time_days': 0
            }
            
            # Simulate low stock scenario
            if product_id and str(product_id).endswith('1'):
                item_analysis['available_quantity'] = max(0, quantity - 50)
                if item_analysis['available_quantity'] < quantity:
                    item_analysis['status'] = 'partial'
                    availability_analysis['available'] = False
                    
                    # Suggest alternatives
                    availability_analysis['alternatives'].append({
                        'original_product_id': product_id,
                        'alternative_product_id': product_id + 1,
                        'reason': 'Similar quality grade available'
                    })
            
            availability_analysis['items_analysis'].append(item_analysis)
        
        if not availability_analysis['available']:
            availability_analysis['recommendations'] = [
                'Consider partial shipment',
                'Suggest alternative products',
                'Adjust delivery timeline'
            ]
        
        return availability_analysis
    
    def optimize_delivery_schedule(self, order_data: Dict):
        """AI optimization of delivery schedule"""
        optimization = {
            'optimized_date': None,
            'delivery_cost': 0,
            'route_efficiency': 0.85,
            'recommendations': []
        }
        
        requested_date = order_data.get('delivery_date')
        customer_location = order_data.get('delivery_address', {})
        
        if requested_date:
            try:
                requested_dt = datetime.fromisoformat(requested_date.replace('Z', '+00:00'))
                
                # Optimize for route efficiency
                optimized_dt = requested_dt
                
                # Check if it's a weekend
                if optimized_dt.weekday() >= 5:  # Saturday or Sunday
                    optimized_dt = optimized_dt + timedelta(days=(7 - optimized_dt.weekday()))
                    optimization['recommendations'].append('Moved to weekday for better delivery efficiency')
                
                optimization['optimized_date'] = optimized_dt.isoformat()
                
                # Calculate delivery cost based on distance (simulated)
                city = customer_location.get('city', '').lower()
                if city in ['mumbai', 'pune', 'nashik']:
                    optimization['delivery_cost'] = 500
                    optimization['route_efficiency'] = 0.95
                else:
                    optimization['delivery_cost'] = 1500
                    optimization['route_efficiency'] = 0.75
                
            except:
                optimization['recommendations'].append('Invalid delivery date provided')
        
        return optimization
    
    def assess_order_risk(self, order_data: Dict):
        """AI assessment of order risk factors"""
        risk_assessment = {
            'overall_risk': 'low',
            'risk_score': 0,
            'risk_factors': [],
            'mitigation_strategies': []
        }
        
        # Customer risk factors
        customer_id = order_data.get('customer_id')
        if customer_id:
            # Simulate customer risk analysis
            if customer_id % 10 == 0:  # Every 10th customer
                risk_assessment['risk_factors'].append('Customer has payment delays history')
                risk_assessment['risk_score'] += 30
        
        # Order value risk
        total_value = sum(item.get('quantity', 0) * item.get('unit_price', 0) 
                         for item in order_data.get('items', []))
        
        if total_value > 5000000:  # 50 lakhs
            risk_assessment['risk_factors'].append('High value order')
            risk_assessment['risk_score'] += 20
        
        # Delivery timeline risk
        delivery_date = order_data.get('delivery_date')
        if delivery_date:
            try:
                delivery_dt = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
                days_to_delivery = (delivery_dt - datetime.now()).days
                
                if days_to_delivery < 3:
                    risk_assessment['risk_factors'].append('Very tight delivery schedule')
                    risk_assessment['risk_score'] += 25
            except:
                pass
        
        # Determine overall risk
        if risk_assessment['risk_score'] >= 50:
            risk_assessment['overall_risk'] = 'high'
            risk_assessment['mitigation_strategies'] = [
                'Require advance payment',
                'Get management approval',
                'Confirm inventory allocation'
            ]
        elif risk_assessment['risk_score'] >= 25:
            risk_assessment['overall_risk'] = 'medium'
            risk_assessment['mitigation_strategies'] = [
                'Confirm payment terms',
                'Validate delivery capacity'
            ]
        
        return risk_assessment
    
    def forecast_revenue(self, period: str, territory_id: Optional[int] = None):
        """AI revenue forecasting"""
        forecast = {
            'period': period,
            'territory_id': territory_id,
            'forecast_amount': 0,
            'confidence_interval': {},
            'growth_rate': 0,
            'key_drivers': [],
            'risks': []
        }
        
        # Simulate revenue forecast based on period
        base_revenue = 15000000  # 1.5 crore monthly base
        
        if period == 'monthly':
            forecast['forecast_amount'] = base_revenue * (1 + np.random.normal(0.05, 0.1))
        elif period == 'quarterly':
            forecast['forecast_amount'] = base_revenue * 3 * (1 + np.random.normal(0.08, 0.15))
        elif period == 'yearly':
            forecast['forecast_amount'] = base_revenue * 12 * (1 + np.random.normal(0.12, 0.2))
        
        # Confidence interval
        forecast['confidence_interval'] = {
            'lower_bound': forecast['forecast_amount'] * 0.85,
            'upper_bound': forecast['forecast_amount'] * 1.15,
            'confidence_level': 0.80
        }
        
        # Growth rate calculation
        forecast['growth_rate'] = np.random.normal(0.08, 0.05)  # 8% average growth
        
        # Key drivers
        forecast['key_drivers'] = [
            'Seasonal demand increase',
            'New customer acquisitions',
            'Premium product mix shift',
            'Market expansion'
        ]
        
        # Risks
        forecast['risks'] = [
            'Monsoon impact on supply',
            'Price volatility',
            'Competition pressure',
            'Economic slowdown'
        ]
        
        return forecast
    
    def forecast_product_demand(self, product_category: str, period: str):
        """AI demand forecasting for products"""
        demand_forecast = {
            'product_category': product_category,
            'period': period,
            'forecasted_demand': {},
            'seasonal_factors': {},
            'trend_analysis': {},
            'recommendations': []
        }
        
        # Simulate demand for different rice varieties
        rice_varieties = ['Basmati', 'Jasmine', 'Sona Masoori', 'IR64', 'Ponni']
        
        for variety in rice_varieties:
            base_demand = np.random.randint(500, 2000)  # tons
            seasonal_factor = 1 + np.random.normal(0, 0.2)
            
            demand_forecast['forecasted_demand'][variety] = {
                'quantity_tons': base_demand * seasonal_factor,
                'growth_rate': np.random.normal(0.05, 0.1),
                'confidence': np.random.uniform(0.7, 0.9)
            }
        
        # Seasonal factors
        demand_forecast['seasonal_factors'] = {
            'festival_season': 1.3,
            'wedding_season': 1.2,
            'monsoon_impact': 0.9,
            'harvest_season': 1.1
        }
        
        # Recommendations
        demand_forecast['recommendations'] = [
            'Increase Basmati inventory for festival season',
            'Focus on premium varieties for higher margins',
            'Plan procurement based on harvest forecasts'
        ]
        
        return demand_forecast
    
    def analyze_sales_performance_detailed(self, performance_data: Dict):
        """Detailed AI analysis of sales performance"""
        analysis = {
            'performance_score': 0,
            'key_metrics': {},
            'trends': {},
            'benchmarks': {},
            'insights': []
        }
        
        # Calculate performance score
        revenue_achievement = performance_data.get('revenue_achievement', 0.8)
        volume_achievement = performance_data.get('volume_achievement', 0.85)
        customer_acquisition = performance_data.get('new_customers', 0)
        
        performance_score = (revenue_achievement * 0.4 + 
                           volume_achievement * 0.3 + 
                           min(customer_acquisition / 10, 1) * 0.3) * 100
        
        analysis['performance_score'] = performance_score
        
        # Key metrics
        analysis['key_metrics'] = {
            'revenue_achievement': revenue_achievement,
            'volume_achievement': volume_achievement,
            'average_order_value': performance_data.get('avg_order_value', 0),
            'conversion_rate': performance_data.get('conversion_rate', 0.15),
            'customer_retention': performance_data.get('retention_rate', 0.85)
        }
        
        # Insights
        if revenue_achievement < 0.8:
            analysis['insights'].append('Revenue target achievement below expectations')
        
        if volume_achievement > revenue_achievement:
            analysis['insights'].append('Volume growth outpacing revenue - check pricing strategy')
        
        if customer_acquisition < 5:
            analysis['insights'].append('Low new customer acquisition - focus on lead generation')
        
        return analysis
    
    def optimize_quote_pricing(self, quote_data: Dict):
        """AI optimization of quote pricing"""
        optimization = {
            'optimized_pricing': {},
            'pricing_strategy': '',
            'margin_analysis': {},
            'competitive_position': '',
            'recommendations': []
        }
        
        items = quote_data.get('items', [])
        customer_tier = quote_data.get('customer_tier', 'standard')
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            base_price = item.get('unit_price', 0)
            
            # Apply AI pricing optimization
            optimized_price = base_price
            
            # Volume discount
            if quantity > 1000:  # tons
                optimized_price *= 0.95  # 5% discount
                optimization['recommendations'].append(f'Volume discount applied for product {product_id}')
            
            # Customer tier pricing
            if customer_tier == 'premium':
                optimized_price *= 1.02  # 2% premium
            elif customer_tier == 'gold':
                optimized_price *= 0.98  # 2% discount
            
            # Market positioning
            market_factor = np.random.uniform(0.95, 1.05)
            optimized_price *= market_factor
            
            optimization['optimized_pricing'][product_id] = {
                'original_price': base_price,
                'optimized_price': round(optimized_price, 2),
                'discount_percentage': round((1 - optimized_price/base_price) * 100, 2)
            }
        
        # Pricing strategy
        optimization['pricing_strategy'] = 'value_based'
        optimization['competitive_position'] = 'competitive'
        
        return optimization
    
    def calculate_win_probability(self, quote_data: Dict):
        """AI calculation of quote win probability"""
        win_probability = {
            'probability': 0.0,
            'confidence': 0.0,
            'factors': {},
            'recommendations': []
        }
        
        # Base probability
        base_prob = 0.3
        
        # Customer relationship factor
        customer_tier = quote_data.get('customer_tier', 'standard')
        if customer_tier == 'premium':
            base_prob += 0.2
        elif customer_tier == 'gold':
            base_prob += 0.1
        
        # Quote value factor
        quote_value = sum(item.get('quantity', 0) * item.get('unit_price', 0) 
                         for item in quote_data.get('items', []))
        
        if quote_value > 1000000:  # 10 lakhs
            base_prob += 0.1
        
        # Competitive pricing factor
        pricing_competitiveness = np.random.uniform(0.7, 1.0)
        base_prob += (pricing_competitiveness - 0.85) * 0.5
        
        # Response time factor
        quote_age_days = quote_data.get('quote_age_days', 1)
        if quote_age_days <= 2:
            base_prob += 0.1
        elif quote_age_days > 7:
            base_prob -= 0.1
        
        win_probability['probability'] = max(0.05, min(0.95, base_prob))
        win_probability['confidence'] = 0.75
        
        # Factors
        win_probability['factors'] = {
            'customer_relationship': customer_tier,
            'quote_value': quote_value,
            'pricing_competitiveness': pricing_competitiveness,
            'response_timeliness': quote_age_days <= 2
        }
        
        # Recommendations
        if win_probability['probability'] < 0.4:
            win_probability['recommendations'] = [
                'Review pricing strategy',
                'Enhance value proposition',
                'Accelerate follow-up'
            ]
        
        return win_probability
    
    def analyze_conversion_funnel(self, funnel_data: Dict):
        """AI analysis of sales conversion funnel"""
        analysis = {
            'funnel_efficiency': 0.0,
            'stage_conversion_rates': {},
            'bottlenecks': [],
            'improvement_opportunities': [],
            'benchmark_comparison': {}
        }
        
        # Calculate stage conversion rates
        stages = ['leads', 'qualified_leads', 'quotes', 'orders']
        conversion_rates = {}
        
        for i in range(len(stages) - 1):
            current_stage = funnel_data.get(stages[i], 0)
            next_stage = funnel_data.get(stages[i + 1], 0)
            
            if current_stage > 0:
                conversion_rate = next_stage / current_stage
                conversion_rates[f"{stages[i]}_to_{stages[i+1]}"] = conversion_rate
            else:
                conversion_rates[f"{stages[i]}_to_{stages[i+1]}"] = 0
        
        analysis['stage_conversion_rates'] = conversion_rates
        
        # Overall funnel efficiency
        total_leads = funnel_data.get('leads', 0)
        total_orders = funnel_data.get('orders', 0)
        
        if total_leads > 0:
            analysis['funnel_efficiency'] = total_orders / total_leads
        
        # Identify bottlenecks
        benchmark_rates = {
            'leads_to_qualified_leads': 0.3,
            'qualified_leads_to_quotes': 0.6,
            'quotes_to_orders': 0.25
        }
        
        for stage, rate in conversion_rates.items():
            benchmark = benchmark_rates.get(stage, 0.3)
            if rate < benchmark * 0.8:  # 20% below benchmark
                analysis['bottlenecks'].append({
                    'stage': stage,
                    'current_rate': rate,
                    'benchmark_rate': benchmark,
                    'gap': benchmark - rate
                })
        
        # Improvement opportunities
        if conversion_rates.get('leads_to_qualified_leads', 0) < 0.25:
            analysis['improvement_opportunities'].append('Improve lead qualification process')
        
        if conversion_rates.get('quotes_to_orders', 0) < 0.2:
            analysis['improvement_opportunities'].append('Enhance quote follow-up and closing techniques')
        
        return analysis
    
    def _fallback_pricing_optimization(self, order_data: Dict):
        """Fallback pricing optimization when AI service is unavailable"""
        optimization = {
            'optimized_pricing': {},
            'total_discount': 0,
            'margin_impact': 0,
            'recommendations': []
        }
        
        items = order_data.get('items', [])
        total_quantity = sum(item.get('quantity', 0) for item in items)
        
        # Simple volume-based optimization
        if total_quantity > 1000:  # tons
            optimization['total_discount'] = 0.05  # 5%
            optimization['recommendations'].append('Volume discount applied')
        elif total_quantity > 500:
            optimization['total_discount'] = 0.03  # 3%
            optimization['recommendations'].append('Moderate volume discount applied')
        
        return optimization
    
    def identify_cross_sell_opportunities(self, customer_id: Optional[int], order_id: Optional[int]):
        """AI identification of cross-sell opportunities"""
        opportunities = []
        
        # Simulate cross-sell analysis
        base_products = ['Basmati Rice', 'Jasmine Rice', 'Sona Masoori']
        complementary_products = {
            'Basmati Rice': ['Premium Basmati', 'Organic Basmati', 'Aged Basmati'],
            'Jasmine Rice': ['Thai Jasmine', 'Premium Jasmine', 'Fragrant Rice'],
            'Sona Masoori': ['Premium Sona Masoori', 'Parboiled Rice', 'Brown Rice']
        }
        
        for base_product in base_products:
            for complement in complementary_products.get(base_product, []):
                opportunities.append({
                    'product_name': complement,
                    'base_product': base_product,
                    'cross_sell_probability': np.random.uniform(0.2, 0.8),
                    'potential_revenue': np.random.randint(50000, 500000),
                    'recommendation_reason': f'Customers who buy {base_product} often purchase {complement}'
                })
        
        # Sort by probability
        opportunities.sort(key=lambda x: x['cross_sell_probability'], reverse=True)
        
        return opportunities[:5]  # Top 5 opportunities
    
    def identify_upsell_opportunities(self, customer_id: Optional[int], order_id: Optional[int]):
        """AI identification of upsell opportunities"""
        opportunities = []
        
        # Simulate upsell analysis
        upsell_scenarios = [
            {
                'current_product': 'Standard Basmati',
                'upsell_product': 'Premium Basmati',
                'price_difference': 5000,  # per ton
                'upsell_probability': 0.6,
                'value_proposition': 'Better aroma and longer grains'
            },
            {
                'current_product': 'Regular Rice',
                'upsell_product': 'Organic Rice',
                'price_difference': 8000,  # per ton
                'upsell_probability': 0.4,
                'value_proposition': 'Health benefits and premium positioning'
            },
            {
                'current_product': 'Bulk Packaging',
                'upsell_product': 'Branded Packaging',
                'price_difference': 2000,  # per ton
                'upsell_probability': 0.7,
                'value_proposition': 'Better shelf appeal and brand recognition'
            }
        ]
        
        return upsell_scenarios
