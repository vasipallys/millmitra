import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from models.finance import FinancialTransaction, Invoice, Payment
from models.customers import Customer
from models.sales import SalesOrder

class AIFinanceService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def analyze_transaction_patterns(self, transactions: List[Dict]):
        """AI analysis of financial transaction patterns"""
        try:
            response = requests.post(f"{self.ai_service_url}/finance/analyze-patterns", json={'transactions': transactions})
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_transaction_analysis(transactions)
    
    def validate_transaction(self, transaction_data: Dict):
        """AI transaction validation and fraud detection"""
        errors = []
        warnings = []
        fraud_score = 0.0
        
        # Basic validation
        if not transaction_data.get('amount') or transaction_data['amount'] <= 0:
            errors.append("Valid amount is required")
        
        if not transaction_data.get('transaction_type'):
            errors.append("Transaction type is required")
        
        # AI fraud detection
        amount = transaction_data.get('amount', 0)
        transaction_type = transaction_data.get('transaction_type', '')
        
        # Check for unusual amounts
        if amount > 100000:
            fraud_score += 0.3
            warnings.append("Large amount transaction - verify authenticity")
        
        # Check timing patterns
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            fraud_score += 0.2
            warnings.append("Transaction outside normal business hours")
        
        # Check for duplicate transactions
        if self._check_duplicate_transaction(transaction_data):
            fraud_score += 0.4
            warnings.append("Potential duplicate transaction detected")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'fraud_score': fraud_score,
            'fraud_risk': 'high' if fraud_score > 0.7 else 'medium' if fraud_score > 0.4 else 'low'
        }
    
    def categorize_transaction(self, transaction_data: Dict):
        """AI-powered transaction categorization"""
        description = transaction_data.get('description', '').lower()
        amount = transaction_data.get('amount', 0)
        transaction_type = transaction_data.get('transaction_type', '')
        
        # AI categorization logic
        categories = {
            'raw_materials': ['paddy', 'rice', 'grain', 'purchase'],
            'utilities': ['electricity', 'water', 'gas', 'fuel'],
            'labor': ['salary', 'wages', 'overtime', 'bonus'],
            'maintenance': ['repair', 'maintenance', 'service', 'parts'],
            'marketing': ['advertising', 'promotion', 'marketing'],
            'transportation': ['transport', 'delivery', 'freight', 'shipping'],
            'administrative': ['office', 'admin', 'supplies', 'stationery']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return {
                    'category': category,
                    'subcategory': self._get_subcategory(category, description),
                    'confidence': 0.85,
                    'cost_center': self._determine_cost_center(category)
                }
        
        return {
            'category': 'miscellaneous',
            'subcategory': 'other',
            'confidence': 0.5,
            'cost_center': 'general'
        }
    
    def analyze_financial_impact(self, transaction_data: Dict):
        """Analyze financial impact of transaction"""
        impact = {
            'cash_flow_impact': 'neutral',
            'profitability_impact': 'neutral',
            'liquidity_impact': 'neutral',
            'recommendations': []
        }
        
        amount = transaction_data.get('amount', 0)
        transaction_type = transaction_data.get('transaction_type', '')
        
        if transaction_type == 'expense' and amount > 50000:
            impact['cash_flow_impact'] = 'negative'
            impact['liquidity_impact'] = 'negative'
            impact['recommendations'].append('Monitor cash flow closely')
        
        if transaction_type == 'revenue' and amount > 100000:
            impact['cash_flow_impact'] = 'positive'
            impact['profitability_impact'] = 'positive'
            impact['recommendations'].append('Consider reinvestment opportunities')
        
        return impact
    
    def predict_payment_behavior(self, invoices: List[Dict]):
        """AI prediction of customer payment behavior"""
        predictions = {}
        
        for invoice in invoices:
            customer_id = invoice.get('customer_id')
            amount = invoice.get('amount', 0)
            due_date = invoice.get('due_date')
            
            # AI payment prediction
            payment_probability = self._calculate_payment_probability(invoice)
            days_to_payment = self._predict_payment_days(invoice)
            
            predictions[invoice['id']] = {
                'payment_probability': payment_probability,
                'predicted_payment_date': self._calculate_predicted_date(due_date, days_to_payment),
                'risk_level': 'high' if payment_probability < 0.6 else 'medium' if payment_probability < 0.8 else 'low',
                'recommended_action': self._get_collection_action(payment_probability)
            }
        
        return predictions
    
    def optimize_invoice_pricing(self, invoice_data: Dict):
        """AI optimization of invoice pricing"""
        optimization = {
            'original_amount': invoice_data.get('amount', 0),
            'optimized_amount': 0,
            'optimization_factors': [],
            'margin_improvement': 0.0
        }
        
        customer_id = invoice_data.get('customer_id')
        product_items = invoice_data.get('items', [])
        
        # AI pricing optimization logic
        base_amount = invoice_data.get('amount', 0)
        optimized_amount = base_amount
        
        # Customer-based pricing
        customer_tier = self._get_customer_tier(customer_id)
        if customer_tier == 'premium':
            optimized_amount *= 1.05
            optimization['optimization_factors'].append('Premium customer pricing')
        elif customer_tier == 'budget':
            optimized_amount *= 0.98
            optimization['optimization_factors'].append('Budget customer discount')
        
        # Volume-based pricing
        total_quantity = sum(item.get('quantity', 0) for item in product_items)
        if total_quantity > 10000:
            optimized_amount *= 0.97
            optimization['optimization_factors'].append('Volume discount applied')
        
        optimization['optimized_amount'] = round(optimized_amount, 2)
        optimization['margin_improvement'] = ((optimized_amount - base_amount) / base_amount) * 100
        
        return optimization
    
    def recommend_payment_terms(self, invoice_data: Dict):
        """AI recommendation of payment terms"""
        customer_id = invoice_data.get('customer_id')
        amount = invoice_data.get('amount', 0)
        
        # AI payment terms logic
        customer_history = self._get_customer_payment_history(customer_id)
        credit_score = self._calculate_customer_credit_score(customer_history)
        
        if credit_score > 0.8:
            return {
                'payment_days': 30,
                'early_payment_discount': 2.0,
                'late_payment_penalty': 1.5,
                'credit_limit_utilization': 'low'
            }
        elif credit_score > 0.6:
            return {
                'payment_days': 21,
                'early_payment_discount': 1.5,
                'late_payment_penalty': 2.0,
                'credit_limit_utilization': 'medium'
            }
        else:
            return {
                'payment_days': 14,
                'early_payment_discount': 1.0,
                'late_payment_penalty': 3.0,
                'credit_limit_utilization': 'high'
            }
    
    def forecast_cash_flow(self, cash_flow_data: Dict, forecast_days: int):
        """AI cash flow forecasting"""
        forecast = {
            'forecast_period': forecast_days,
            'daily_forecasts': [],
            'key_insights': [],
            'risk_periods': [],
            'recommendations': []
        }
        
        # Historical data analysis
        historical_inflows = cash_flow_data.get('historical_inflows', [])
        historical_outflows = cash_flow_data.get('historical_outflows', [])
        
        # Generate daily forecasts
        for day in range(1, forecast_days + 1):
            # AI forecasting logic
            predicted_inflow = self._predict_daily_inflow(historical_inflows, day)
            predicted_outflow = self._predict_daily_outflow(historical_outflows, day)
            net_flow = predicted_inflow - predicted_outflow
            
            forecast['daily_forecasts'].append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day)).isoformat(),
                'predicted_inflow': predicted_inflow,
                'predicted_outflow': predicted_outflow,
                'net_cash_flow': net_flow,
                'cumulative_balance': self._calculate_cumulative_balance(forecast['daily_forecasts'], net_flow)
            })
        
        # Identify risk periods
        for daily_forecast in forecast['daily_forecasts']:
            if daily_forecast['cumulative_balance'] < 50000:  # Low cash threshold
                forecast['risk_periods'].append({
                    'date': daily_forecast['date'],
                    'balance': daily_forecast['cumulative_balance'],
                    'severity': 'high' if daily_forecast['cumulative_balance'] < 10000 else 'medium'
                })
        
        # Generate recommendations
        if forecast['risk_periods']:
            forecast['recommendations'].append('Consider accelerating collections')
            forecast['recommendations'].append('Delay non-critical payments')
        
        return forecast
    
    def analyze_liquidity(self, cash_flow_data: Dict):
        """AI liquidity analysis"""
        analysis = {
            'current_liquidity_ratio': 0.0,
            'quick_ratio': 0.0,
            'cash_ratio': 0.0,
            'liquidity_score': 0.0,
            'liquidity_trend': 'stable',
            'recommendations': []
        }
        
        current_assets = cash_flow_data.get('current_assets', 0)
        current_liabilities = cash_flow_data.get('current_liabilities', 0)
        cash_equivalents = cash_flow_data.get('cash_equivalents', 0)
        inventory = cash_flow_data.get('inventory_value', 0)
        
        # Calculate ratios
        if current_liabilities > 0:
            analysis['current_liquidity_ratio'] = current_assets / current_liabilities
            analysis['quick_ratio'] = (current_assets - inventory) / current_liabilities
            analysis['cash_ratio'] = cash_equivalents / current_liabilities
        
        # Calculate liquidity score
        liquidity_score = (analysis['current_liquidity_ratio'] * 0.4 + 
                          analysis['quick_ratio'] * 0.4 + 
                          analysis['cash_ratio'] * 0.2)
        analysis['liquidity_score'] = min(1.0, liquidity_score / 2.0)
        
        # Generate recommendations
        if analysis['current_liquidity_ratio'] < 1.5:
            analysis['recommendations'].append('Improve current ratio by reducing short-term debt')
        
        if analysis['quick_ratio'] < 1.0:
            analysis['recommendations'].append('Increase liquid assets or reduce current liabilities')
        
        return analysis
    
    def optimize_profitability(self, profitability_data: Dict):
        """AI profitability optimization"""
        optimization = {
            'current_metrics': {},
            'optimization_opportunities': [],
            'potential_improvements': {},
            'implementation_roadmap': []
        }
        
        gross_margin = profitability_data.get('gross_margin', 0)
        operating_margin = profitability_data.get('operating_margin', 0)
        net_margin = profitability_data.get('net_margin', 0)
        
        optimization['current_metrics'] = {
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'net_margin': net_margin
        }
        
        # Identify optimization opportunities
        if gross_margin < 0.25:  # 25%
            optimization['optimization_opportunities'].append({
                'area': 'Cost of Goods Sold',
                'current_performance': gross_margin,
                'target_performance': 0.30,
                'potential_impact': 'high',
                'strategies': ['Negotiate better supplier rates', 'Improve production efficiency']
            })
        
        if operating_margin < 0.15:  # 15%
            optimization['optimization_opportunities'].append({
                'area': 'Operating Expenses',
                'current_performance': operating_margin,
                'target_performance': 0.20,
                'potential_impact': 'medium',
                'strategies': ['Reduce administrative costs', 'Optimize energy consumption']
            })
        
        return optimization
    
    def analyze_profit_margins(self, profitability_data: Dict):
        """AI analysis of profit margins"""
        analysis = {
            'margin_trends': {},
            'benchmark_comparison': {},
            'margin_drivers': [],
            'improvement_areas': []
        }
        
        # Analyze margin trends
        historical_margins = profitability_data.get('historical_margins', [])
        if historical_margins:
            analysis['margin_trends'] = {
                'trend_direction': self._calculate_trend_direction(historical_margins),
                'volatility': self._calculate_margin_volatility(historical_margins),
                'seasonal_patterns': self._identify_seasonal_patterns(historical_margins)
            }
        
        # Benchmark comparison
        industry_benchmarks = {
            'gross_margin': 0.28,
            'operating_margin': 0.18,
            'net_margin': 0.12
        }
        
        current_margins = profitability_data.get('current_margins', {})
        for margin_type, benchmark in industry_benchmarks.items():
            current_value = current_margins.get(margin_type, 0)
            analysis['benchmark_comparison'][margin_type] = {
                'current': current_value,
                'benchmark': benchmark,
                'variance': current_value - benchmark,
                'performance': 'above' if current_value > benchmark else 'below'
            }
        
        return analysis

    def analyze_financial_trends(self, financial_data: Dict):
        """AI analysis of financial trends"""
        insights = []
        
        profit_margin = (financial_data['profit'] / financial_data['revenue'] * 100) if financial_data['revenue'] > 0 else 0
        
        if profit_margin > 20:
            insights.append({
                'type': 'positive',
                'message': f'Excellent profit margin of {profit_margin:.1f}%',
                'recommendation': 'Consider expansion opportunities'
            })
        elif profit_margin < 5:
            insights.append({
                'type': 'warning',
                'message': f'Low profit margin of {profit_margin:.1f}%',
                'recommendation': 'Review cost structure and pricing strategy'
            })
        
        # Cash flow analysis
        net_position = financial_data['net_position']
        if net_position < 0:
            insights.append({
                'type': 'alert',
                'message': 'Negative cash position detected',
                'recommendation': 'Accelerate collections and manage payables'
            })
        
        return insights

    def predict_cash_flow(self, historical_data: List[Dict], forecast_days: int = 30):
        """AI cash flow prediction"""
        if not historical_data:
            return self._generate_default_forecast(forecast_days)
        
        # Simple trend analysis
        daily_inflows = [d.get('inflow', 0) for d in historical_data[-30:]]
        daily_outflows = [d.get('outflow', 0) for d in historical_data[-30:]]
        
        avg_inflow = sum(daily_inflows) / len(daily_inflows) if daily_inflows else 50000
        avg_outflow = sum(daily_outflows) / len(daily_outflows) if daily_outflows else 45000
        
        forecast = []
        current_balance = historical_data[-1].get('balance', 100000) if historical_data else 100000
        
        for day in range(1, forecast_days + 1):
            predicted_inflow = self._predict_daily_inflow(daily_inflows, day)
            predicted_outflow = self._predict_daily_outflow(daily_outflows, day)
            
            current_balance += predicted_inflow - predicted_outflow
            
            forecast.append({
                'day': day,
                'predicted_inflow': predicted_inflow,
                'predicted_outflow': predicted_outflow,
                'predicted_balance': current_balance,
                'confidence': max(0.6, 1 - (day * 0.02))  # Decreasing confidence
            })
        
        return {
            'forecast': forecast,
            'summary': {
                'avg_daily_inflow': avg_inflow,
                'avg_daily_outflow': avg_outflow,
                'net_daily_flow': avg_inflow - avg_outflow
            }
        }

    def _generate_default_forecast(self, days: int):
        """Generate default forecast when no historical data"""
        forecast = []
        balance = 100000
        
        for day in range(1, days + 1):
            inflow = 50000 + np.random.randint(-10000, 20000)
            outflow = 45000 + np.random.randint(-8000, 15000)
            balance += inflow - outflow
            
            forecast.append({
                'day': day,
                'predicted_inflow': inflow,
                'predicted_outflow': outflow,
                'predicted_balance': balance,
                'confidence': 0.7
            })
        
        return {'forecast': forecast}
    
    def _fallback_transaction_analysis(self, transactions: List[Dict]):
        """Fallback analysis when AI service is unavailable"""
        return {
            'total_transactions': len(transactions),
            'total_amount': sum(t.get('amount', 0) for t in transactions),
            'transaction_types': self._count_transaction_types(transactions),
            'average_amount': sum(t.get('amount', 0) for t in transactions) / len(transactions) if transactions else 0
        }
    
    def _check_duplicate_transaction(self, transaction_data: Dict):
        """Check for potential duplicate transactions"""
        # Simplified duplicate detection
        return False
    
    def _get_subcategory(self, category: str, description: str):
        """Get subcategory based on category and description"""
        subcategories = {
            'raw_materials': 'paddy_purchase',
            'utilities': 'electricity',
            'labor': 'regular_wages',
            'maintenance': 'equipment_repair',
            'marketing': 'advertising',
            'transportation': 'delivery',
            'administrative': 'office_supplies'
        }
        return subcategories.get(category, 'other')
    
    def _determine_cost_center(self, category: str):
        """Determine cost center based on category"""
        cost_centers = {
            'raw_materials': 'production',
            'utilities': 'production',
            'labor': 'production',
            'maintenance': 'production',
            'marketing': 'sales',
            'transportation': 'logistics',
            'administrative': 'admin'
        }
        return cost_centers.get(category, 'general')
    
    def _calculate_payment_probability(self, invoice: Dict):
        """Calculate probability of payment"""
        # Simplified calculation
        amount = invoice.get('amount', 0)
        customer_id = invoice.get('customer_id')
        
        base_probability = 0.8
        
        # Adjust based on amount
        if amount > 100000:
            base_probability -= 0.1
        
        return max(0.1, min(1.0, base_probability))
    
    def _predict_payment_days(self, invoice: Dict):
        """Predict days until payment"""
        # Simplified prediction
        return 25 + np.random.randint(-10, 15)
    
    def _calculate_predicted_date(self, due_date: str, days_to_payment: int):
        """Calculate predicted payment date"""
        if due_date:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            predicted = due + timedelta(days=days_to_payment)
            return predicted.isoformat()
        return None
    
    def _get_collection_action(self, payment_probability: float):
        """Get recommended collection action"""
        if payment_probability < 0.6:
            return 'immediate_follow_up'
        elif payment_probability < 0.8:
            return 'gentle_reminder'
        else:
            return 'standard_follow_up'
    
    def _get_customer_tier(self, customer_id: int):
        """Get customer tier for pricing"""
        # Simplified tier determination
        return 'regular'
    
    def _get_customer_payment_history(self, customer_id: int):
        """Get customer payment history"""
        # Simplified history
        return {'average_days_to_pay': 28, 'payment_success_rate': 0.85}
    
    def _calculate_customer_credit_score(self, payment_history: Dict):
        """Calculate customer credit score"""
        success_rate = payment_history.get('payment_success_rate', 0.5)
        avg_days = payment_history.get('average_days_to_pay', 30)
        
        # Simple scoring algorithm
        score = success_rate * 0.7 + (1 - min(avg_days / 60, 1)) * 0.3
        return max(0.1, min(1.0, score))
    
    def _predict_daily_inflow(self, historical_inflows: List, day: int):
        """Predict daily cash inflow"""
        if not historical_inflows:
            return 50000 + np.random.randint(-10000, 20000)
        
        avg_inflow = sum(historical_inflows) / len(historical_inflows)
        return avg_inflow + np.random.randint(-5000, 10000)
    
    def _predict_daily_outflow(self, historical_outflows: List, day: int):
        """Predict daily cash outflow"""
        if not historical_outflows:
            return 40000 + np.random.randint(-8000, 15000)
        
        avg_outflow = sum(historical_outflows) / len(historical_outflows)
        return avg_outflow + np.random.randint(-3000, 8000)
    
    def _calculate_cumulative_balance(self, forecasts: List, net_flow: float):
        """Calculate cumulative balance"""
        if not forecasts:
            return 100000 + net_flow  # Starting balance
        
        return forecasts[-1]['cumulative_balance'] + net_flow
    
    def _count_transaction_types(self, transactions: List[Dict]):
        """Count transactions by type"""
        types = {}
        for transaction in transactions:
            t_type = transaction.get('transaction_type', 'unknown')
            types[t_type] = types.get(t_type, 0) + 1
        return types
    
    def _calculate_trend_direction(self, historical_margins: List):
        """Calculate trend direction of margins"""
        if len(historical_margins) < 2:
            return 'stable'
        
        recent_avg = sum(historical_margins[-3:]) / min(3, len(historical_margins))
        older_avg = sum(historical_margins[:3]) / min(3, len(historical_margins))
        
        if recent_avg > older_avg * 1.05:
            return 'improving'
        elif recent_avg < older_avg * 0.95:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_margin_volatility(self, historical_margins: List):
        """Calculate margin volatility"""
        if len(historical_margins) < 2:
            return 0.0
        
        return np.std(historical_margins) / np.mean(historical_margins) if np.mean(historical_margins) > 0 else 0.0
    
    def _identify_seasonal_patterns(self, historical_margins: List):
        """Identify seasonal patterns in margins"""
        # Simplified seasonal analysis
        return {
            'has_seasonality': len(historical_margins) > 12,
            'peak_months': [3, 4, 10, 11],  # Harvest seasons
            'low_months': [7, 8, 9]
        }

