import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

class AISupplyChainService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def optimize_purchase_order(self, po_data: Dict):
        """AI optimization for purchase orders"""
        try:
            response = requests.post(f"{self.ai_service_url}/supply-chain/optimize-po", json=po_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_po_optimization(po_data)
    
    def predict_supplier_performance(self, supplier_data: Dict, order_details: Dict):
        """Predict supplier performance for upcoming order"""
        try:
            prediction_data = {**supplier_data, **order_details}
            response = requests.post(f"{self.ai_service_url}/supply-chain/predict-performance", json=prediction_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_performance_prediction(supplier_data)
    
    def recommend_suppliers(self, procurement_request: Dict):
        """AI-powered supplier recommendations"""
        try:
            response = requests.post(f"{self.ai_service_url}/supply-chain/recommend-suppliers", json=procurement_request)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_supplier_recommendations(procurement_request)
    
    def optimize_inventory_levels(self, inventory_data: Dict):
        """AI optimization for inventory levels"""
        try:
            response = requests.post(f"{self.ai_service_url}/supply-chain/optimize-inventory", json=inventory_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_inventory_optimization(inventory_data)
    
    def assess_supply_risk(self, supplier_id: int, order_data: Dict):
        """Assess supply chain risks"""
        try:
            risk_data = {'supplier_id': supplier_id, **order_data}
            response = requests.post(f"{self.ai_service_url}/supply-chain/assess-risk", json=risk_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_risk_assessment(supplier_id, order_data)
    
    def predict_delivery_date(self, supplier_id: int, order_details: Dict):
        """Predict accurate delivery date"""
        try:
            prediction_data = {'supplier_id': supplier_id, **order_details}
            response = requests.post(f"{self.ai_service_url}/supply-chain/predict-delivery", json=prediction_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_delivery_prediction(order_details)
    
    def optimize_procurement_strategy(self, historical_data: List[Dict], requirements: Dict):
        """Optimize overall procurement strategy"""
        try:
            strategy_data = {'historical_data': historical_data, 'requirements': requirements}
            response = requests.post(f"{self.ai_service_url}/supply-chain/optimize-strategy", json=strategy_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_strategy_optimization(historical_data, requirements)
    
    # Fallback methods
    def _fallback_po_optimization(self, po_data: Dict):
        """Fallback PO optimization"""
        recommendations = []
        
        # Quantity optimization
        total_value = po_data.get('total_amount', 0)
        if total_value > 100000:
            recommendations.append("Consider splitting large order for better cash flow")
        
        # Timing optimization
        delivery_date = datetime.fromisoformat(po_data.get('expected_delivery_date', datetime.now().isoformat()))
        if delivery_date < datetime.now() + timedelta(days=7):
            recommendations.append("Rush order may incur additional costs")
        
        return {
            'optimized_parameters': {
                'suggested_delivery_date': (datetime.now() + timedelta(days=10)).isoformat(),
                'bulk_discount_available': total_value > 50000
            },
            'recommendations': recommendations,
            'cost_savings_potential': min(total_value * 0.05, 5000)
        }
    
    def _fallback_performance_prediction(self, supplier_data: Dict):
        """Fallback performance prediction"""
        base_score = supplier_data.get('overall_score', 3.5)
        
        return {
            'predicted_quality_score': min(5.0, base_score + np.random.uniform(-0.2, 0.2)),
            'predicted_delivery_performance': min(100, (base_score / 5) * 100 + np.random.uniform(-5, 5)),
            'confidence': 0.75,
            'risk_factors': ['Weather conditions', 'Market volatility'] if base_score < 4.0 else []
        }
    
    def _fallback_supplier_recommendations(self, procurement_request: Dict):
        """Fallback supplier recommendations"""
        return {
            'recommended_suppliers': [
                {
                    'supplier_id': 1,
                    'match_score': 85,
                    'reasons': ['High quality rating', 'Competitive pricing', 'Reliable delivery']
                },
                {
                    'supplier_id': 2,
                    'match_score': 78,
                    'reasons': ['Good track record', 'Local supplier', 'Flexible terms']
                }
            ],
            'procurement_strategy': 'multi_supplier',
            'estimated_savings': procurement_request.get('estimated_cost', 0) * 0.08
        }
    
    def _fallback_inventory_optimization(self, inventory_data: Dict):
        """Fallback inventory optimization"""
        current_stock = inventory_data.get('current_stock', 1000)
        monthly_usage = inventory_data.get('monthly_usage', 500)
        
        optimal_stock = monthly_usage * 2  # 2 months safety stock
        reorder_point = monthly_usage * 0.5  # Reorder at 2 weeks
        
        return {
            'optimal_stock_level': optimal_stock,
            'reorder_point': reorder_point,
            'order_quantity': max(monthly_usage, optimal_stock - current_stock),
            'cost_optimization': {
                'carrying_cost_reduction': abs(current_stock - optimal_stock) * 0.1,
                'stockout_risk': 'low' if current_stock > reorder_point else 'medium'
            }
        }
    
    def _fallback_risk_assessment(self, supplier_id: int, order_data: Dict):
        """Fallback risk assessment"""
        order_value = order_data.get('total_amount', 0)
        
        risk_level = 'low'
        if order_value > 100000:
            risk_level = 'medium'
        if order_value > 500000:
            risk_level = 'high'
        
        return {
            'overall_risk': risk_level,
            'risk_factors': {
                'financial_risk': 'low',
                'delivery_risk': 'medium' if order_value > 50000 else 'low',
                'quality_risk': 'low',
                'market_risk': 'medium'
            },
            'mitigation_strategies': [
                'Consider payment terms adjustment',
                'Request delivery confirmation',
                'Implement quality checkpoints'
            ],
            'confidence': 0.8
        }
    
    def _fallback_delivery_prediction(self, order_details: Dict):
        """Fallback delivery prediction"""
        base_days = order_details.get('standard_delivery_days', 7)
        
        return {
            'predicted_delivery_date': (datetime.now() + timedelta(days=base_days + 2)).isoformat(),
            'confidence': 0.7,
            'factors_affecting_delivery': [
                'Supplier workload',
                'Transportation availability',
                'Weather conditions'
            ]
        }
    
    def _fallback_strategy_optimization(self, historical_data: List[Dict], requirements: Dict):
        """Fallback strategy optimization"""
        return {
            'recommended_strategy': 'balanced_sourcing',
            'supplier_diversification': {
                'primary_suppliers': 2,
                'backup_suppliers': 1,
                'split_ratio': [60, 30, 10]
            },
            'cost_optimization': {
                'bulk_purchasing_opportunities': True,
                'seasonal_procurement': True,
                'estimated_annual_savings': requirements.get('annual_budget', 1000000) * 0.12
            },
            'risk_mitigation': [
                'Maintain 2-month safety stock',
                'Diversify supplier base',
                'Implement supplier performance monitoring'
            ]
        }