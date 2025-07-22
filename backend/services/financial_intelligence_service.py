"""
Financial Intelligence Service
AI-powered financial analytics, payment management, and predictive insights
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from decimal import Decimal

from extensions import db
from models import Payment, Expense, User, Farmer, Customer, Transaction, Invoice

class FinancialIntelligenceService:
    def __init__(self):
        self.payment_terms = {
            'immediate': 0,
            'net_7': 7,
            'net_15': 15,
            'net_30': 30,
            'net_45': 45,
            'net_60': 60
        }
        
        self.risk_factors = {
            'payment_history': 0.4,
            'amount_size': 0.2,
            'customer_age': 0.15,
            'seasonal_factors': 0.15,
            'market_conditions': 0.1
        }

    def analyze_cash_flow(self, period_days: int = 30) -> Dict:
        """Comprehensive cash flow analysis with AI predictions"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get transactions for the period
            transactions = Transaction.query.filter(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).all()
            
            # Calculate cash flow metrics
            cash_inflows = []
            cash_outflows = []
            daily_balances = {}
            
            for transaction in transactions:
                date_key = transaction.transaction_date.strftime('%Y-%m-%d')
                
                if transaction.transaction_type == 'income':
                    cash_inflows.append({
                        'date': date_key,
                        'amount': float(transaction.amount),
                        'source': transaction.description
                    })
                else:
                    cash_outflows.append({
                        'date': date_key,
                        'amount': float(transaction.amount),
                        'category': transaction.category
                    })
                
                # Calculate daily balance
                if date_key not in daily_balances:
                    daily_balances[date_key] = 0
                
                if transaction.transaction_type == 'income':
                    daily_balances[date_key] += float(transaction.amount)
                else:
                    daily_balances[date_key] -= float(transaction.amount)
            
            # Calculate key metrics
            total_inflows = sum(item['amount'] for item in cash_inflows)
            total_outflows = sum(item['amount'] for item in cash_outflows)
            net_cash_flow = total_inflows - total_outflows
            
            # Predict future cash flow
            future_predictions = self._predict_cash_flow(daily_balances, period_days)
            
            # Calculate cash flow ratios
            operating_cash_ratio = total_inflows / total_outflows if total_outflows > 0 else 0
            cash_flow_margin = (net_cash_flow / total_inflows * 100) if total_inflows > 0 else 0
            
            # Identify cash flow patterns
            patterns = self._identify_cash_flow_patterns(daily_balances)
            
            return {
                'success': True,
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': period_days
                },
                'summary': {
                    'total_inflows': total_inflows,
                    'total_outflows': total_outflows,
                    'net_cash_flow': net_cash_flow,
                    'operating_cash_ratio': operating_cash_ratio,
                    'cash_flow_margin': cash_flow_margin
                },
                'daily_data': daily_balances,
                'inflows': cash_inflows,
                'outflows': cash_outflows,
                'predictions': future_predictions,
                'patterns': patterns,
                'recommendations': self._generate_cash_flow_recommendations(net_cash_flow, patterns)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Cash flow analysis failed: {str(e)}'}

    def smart_payment_scheduling(self, farmer_id: int, amount: float, payment_type: str = 'procurement') -> Dict:
        """AI-powered optimal payment scheduling"""
        try:
            farmer = Farmer.query.get(farmer_id)
            if not farmer:
                return {'success': False, 'error': 'Farmer not found'}
            
            # Analyze farmer's payment history
            payment_history = self._analyze_farmer_payment_history(farmer_id)
            
            # Calculate risk score
            risk_score = self._calculate_payment_risk(farmer_id, amount)
            
            # Determine optimal payment terms
            optimal_terms = self._determine_optimal_payment_terms(farmer_id, amount, risk_score)
            
            # Calculate payment schedule
            payment_schedule = self._generate_payment_schedule(amount, optimal_terms)
            
            # Predict cash flow impact
            cash_flow_impact = self._predict_payment_impact(amount, optimal_terms)
            
            return {
                'success': True,
                'farmer_info': {
                    'id': farmer_id,
                    'name': farmer.name,
                    'payment_history': payment_history
                },
                'payment_analysis': {
                    'amount': amount,
                    'risk_score': risk_score,
                    'recommended_terms': optimal_terms,
                    'payment_schedule': payment_schedule,
                    'cash_flow_impact': cash_flow_impact
                },
                'recommendations': self._generate_payment_recommendations(risk_score, optimal_terms)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Payment scheduling failed: {str(e)}'}

    def financial_forecasting(self, forecast_days: int = 90) -> Dict:
        """Advanced financial forecasting using AI"""
        try:
            # Get historical data
            historical_data = self._get_historical_financial_data(forecast_days * 2)
            
            # Revenue forecasting
            revenue_forecast = self._forecast_revenue(historical_data, forecast_days)
            
            # Expense forecasting
            expense_forecast = self._forecast_expenses(historical_data, forecast_days)
            
            # Profit forecasting
            profit_forecast = self._calculate_profit_forecast(revenue_forecast, expense_forecast)
            
            # Cash position forecasting
            cash_forecast = self._forecast_cash_position(historical_data, forecast_days)
            
            # Seasonal analysis
            seasonal_analysis = self._analyze_seasonal_patterns(historical_data)
            
            # Risk assessment
            financial_risks = self._assess_financial_risks(historical_data)
            
            return {
                'success': True,
                'forecast_period': {
                    'start_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'end_date': (datetime.utcnow() + timedelta(days=forecast_days)).strftime('%Y-%m-%d'),
                    'days': forecast_days
                },
                'revenue_forecast': revenue_forecast,
                'expense_forecast': expense_forecast,
                'profit_forecast': profit_forecast,
                'cash_forecast': cash_forecast,
                'seasonal_analysis': seasonal_analysis,
                'risk_assessment': financial_risks,
                'key_insights': self._generate_forecast_insights(revenue_forecast, expense_forecast, profit_forecast)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Financial forecasting failed: {str(e)}'}

    def payment_optimization(self) -> Dict:
        """Optimize payment processes using AI"""
        try:
            # Analyze pending payments
            pending_payments = Payment.query.filter_by(status='pending').all()
            
            # Group payments by priority
            payment_priorities = self._prioritize_payments(pending_payments)
            
            # Optimize payment batching
            payment_batches = self._optimize_payment_batching(pending_payments)
            
            # Calculate cost savings
            cost_savings = self._calculate_optimization_savings(payment_batches)
            
            # Generate payment recommendations
            recommendations = self._generate_payment_optimization_recommendations(payment_priorities, payment_batches)
            
            return {
                'success': True,
                'analysis': {
                    'total_pending_payments': len(pending_payments),
                    'total_pending_amount': sum(float(p.amount) for p in pending_payments),
                    'payment_priorities': payment_priorities,
                    'optimized_batches': payment_batches,
                    'estimated_savings': cost_savings
                },
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Payment optimization failed: {str(e)}'}

    def financial_health_score(self) -> Dict:
        """Calculate comprehensive financial health score"""
        try:
            # Get financial metrics
            current_ratio = self._calculate_current_ratio()
            debt_to_equity = self._calculate_debt_to_equity_ratio()
            profit_margin = self._calculate_profit_margin()
            cash_flow_ratio = self._calculate_cash_flow_ratio()
            inventory_turnover = self._calculate_inventory_turnover()
            
            # Calculate component scores (0-100)
            liquidity_score = min(100, current_ratio * 50)
            leverage_score = max(0, 100 - (debt_to_equity * 50))
            profitability_score = max(0, min(100, profit_margin * 5))
            efficiency_score = min(100, inventory_turnover * 10)
            cash_score = min(100, cash_flow_ratio * 50)
            
            # Weighted overall score
            weights = {
                'liquidity': 0.25,
                'leverage': 0.20,
                'profitability': 0.25,
                'efficiency': 0.15,
                'cash_flow': 0.15
            }
            
            overall_score = (
                liquidity_score * weights['liquidity'] +
                leverage_score * weights['leverage'] +
                profitability_score * weights['profitability'] +
                efficiency_score * weights['efficiency'] +
                cash_score * weights['cash_flow']
            )
            
            # Determine health grade
            if overall_score >= 90:
                health_grade = 'A'
                health_status = 'Excellent'
            elif overall_score >= 80:
                health_grade = 'B'
                health_status = 'Good'
            elif overall_score >= 70:
                health_grade = 'C'
                health_status = 'Fair'
            elif overall_score >= 60:
                health_grade = 'D'
                health_status = 'Poor'
            else:
                health_grade = 'F'
                health_status = 'Critical'
            
            return {
                'success': True,
                'overall_score': round(overall_score, 1),
                'health_grade': health_grade,
                'health_status': health_status,
                'component_scores': {
                    'liquidity': round(liquidity_score, 1),
                    'leverage': round(leverage_score, 1),
                    'profitability': round(profitability_score, 1),
                    'efficiency': round(efficiency_score, 1),
                    'cash_flow': round(cash_score, 1)
                },
                'financial_ratios': {
                    'current_ratio': round(current_ratio, 2),
                    'debt_to_equity': round(debt_to_equity, 2),
                    'profit_margin': round(profit_margin, 2),
                    'cash_flow_ratio': round(cash_flow_ratio, 2),
                    'inventory_turnover': round(inventory_turnover, 2)
                },
                'recommendations': self._generate_health_recommendations(overall_score, health_grade)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Financial health calculation failed: {str(e)}'}

    def automated_invoice_processing(self, invoice_data: Dict) -> Dict:
        """AI-powered automated invoice processing"""
        try:
            # Validate invoice data
            validation_result = self._validate_invoice_data(invoice_data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['errors']}
            
            # Extract and process invoice information
            processed_data = self._process_invoice_data(invoice_data)
            
            # Calculate amounts and taxes
            financial_calculations = self._calculate_invoice_financials(processed_data)
            
            # Generate invoice number
            invoice_number = self._generate_invoice_number()
            
            # Create invoice record
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=processed_data['customer_id'],
                invoice_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=processed_data['payment_terms']),
                subtotal=financial_calculations['subtotal'],
                tax_amount=financial_calculations['tax_amount'],
                total_amount=financial_calculations['total_amount'],
                status='pending',
                created_by=processed_data['created_by']
            )
            
            # Store invoice items
            invoice.set_invoice_items(processed_data['items'])
            
            db.session.add(invoice)
            db.session.commit()
            
            # Generate payment prediction
            payment_prediction = self._predict_invoice_payment(invoice)
            
            return {
                'success': True,
                'invoice': {
                    'invoice_number': invoice_number,
                    'total_amount': float(financial_calculations['total_amount']),
                    'due_date': invoice.due_date.strftime('%Y-%m-%d'),
                    'status': invoice.status
                },
                'financial_details': financial_calculations,
                'payment_prediction': payment_prediction,
                'recommendations': self._generate_invoice_recommendations(invoice, payment_prediction)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Invoice processing failed: {str(e)}'}

    # Helper methods for financial calculations and predictions
    def _predict_cash_flow(self, daily_balances: Dict, period_days: int) -> List[Dict]:
        """Predict future cash flow based on historical patterns"""
        try:
            # Simple trend-based prediction
            values = list(daily_balances.values())
            if len(values) < 7:
                return []
            
            # Calculate trend
            recent_avg = np.mean(values[-7:])
            overall_avg = np.mean(values)
            trend = (recent_avg - overall_avg) / len(values)
            
            predictions = []
            base_date = datetime.utcnow()
            
            for i in range(1, 31):  # Predict next 30 days
                predicted_date = base_date + timedelta(days=i)
                predicted_value = recent_avg + (trend * i)
                
                predictions.append({
                    'date': predicted_date.strftime('%Y-%m-%d'),
                    'predicted_cash_flow': round(predicted_value, 2),
                    'confidence': max(0.5, 1.0 - (i * 0.02))  # Decreasing confidence over time
                })
            
            return predictions
            
        except Exception as e:
            print(f"Cash flow prediction error: {e}")
            return []

    def _identify_cash_flow_patterns(self, daily_balances: Dict) -> Dict:
        """Identify patterns in cash flow data"""
        try:
            values = list(daily_balances.values())
            if len(values) < 7:
                return {'pattern': 'insufficient_data'}
            
            # Calculate volatility
            volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
            
            # Identify trend
            recent_trend = np.mean(values[-7:]) - np.mean(values[:-7]) if len(values) > 7 else 0
            
            # Classify pattern
            if volatility < 0.1:
                pattern_type = 'stable'
            elif volatility < 0.3:
                pattern_type = 'moderate_volatility'
            else:
                pattern_type = 'high_volatility'
            
            trend_direction = 'increasing' if recent_trend > 0 else 'decreasing' if recent_trend < 0 else 'stable'
            
            return {
                'pattern': pattern_type,
                'trend': trend_direction,
                'volatility': round(volatility, 3),
                'trend_strength': abs(recent_trend)
            }
            
        except Exception as e:
            print(f"Pattern identification error: {e}")
            return {'pattern': 'unknown'}

    def _generate_cash_flow_recommendations(self, net_cash_flow: float, patterns: Dict) -> List[Dict]:
        """Generate AI recommendations for cash flow improvement"""
        recommendations = []
        
        if net_cash_flow < 0:
            recommendations.append({
                'category': 'cash_flow_improvement',
                'priority': 'high',
                'recommendation': 'Implement faster collection processes to improve cash inflows',
                'expected_impact': 'Reduce collection period by 15-20%'
            })
        
        if patterns.get('pattern') == 'high_volatility':
            recommendations.append({
                'category': 'cash_flow_stability',
                'priority': 'medium',
                'recommendation': 'Diversify revenue streams to reduce cash flow volatility',
                'expected_impact': 'Improve cash flow predictability by 25%'
            })
        
        if patterns.get('trend') == 'decreasing':
            recommendations.append({
                'category': 'revenue_optimization',
                'priority': 'high',
                'recommendation': 'Review pricing strategy and explore new market opportunities',
                'expected_impact': 'Potential 10-15% revenue increase'
            })
        
        return recommendations

    def _analyze_farmer_payment_history(self, farmer_id: int) -> Dict:
        """Analyze farmer's payment history for risk assessment"""
        try:
            payments = Payment.query.filter_by(farmer_id=farmer_id).order_by(Payment.payment_date.desc()).limit(20).all()
            
            if not payments:
                return {
                    'total_payments': 0,
                    'average_amount': 0,
                    'payment_frequency': 'unknown',
                    'reliability_score': 0.5
                }
            
            total_amount = sum(float(p.amount) for p in payments)
            avg_amount = total_amount / len(payments)
            
            # Calculate payment frequency
            if len(payments) > 1:
                date_diffs = [(payments[i].payment_date - payments[i+1].payment_date).days 
                             for i in range(len(payments)-1)]
                avg_frequency = np.mean(date_diffs)
            else:
                avg_frequency = 30  # Default
            
            # Calculate reliability score based on payment consistency
            reliability_score = min(1.0, len(payments) / 10.0)  # More payments = higher reliability
            
            return {
                'total_payments': len(payments),
                'total_amount': total_amount,
                'average_amount': avg_amount,
                'payment_frequency_days': avg_frequency,
                'reliability_score': reliability_score,
                'last_payment_date': payments[0].payment_date.strftime('%Y-%m-%d') if payments else None
            }
            
        except Exception as e:
            print(f"Payment history analysis error: {e}")
            return {'total_payments': 0, 'reliability_score': 0.5}

    def _calculate_payment_risk(self, farmer_id: int, amount: float) -> float:
        """Calculate payment risk score (0-1, higher = more risky)"""
        try:
            # Get farmer payment history
            history = self._analyze_farmer_payment_history(farmer_id)
            
            # Risk factors
            amount_risk = min(1.0, amount / 100000)  # Higher amounts = higher risk
            history_risk = 1.0 - history['reliability_score']
            frequency_risk = max(0, (history.get('payment_frequency_days', 30) - 30) / 60)
            
            # Weighted risk score
            risk_score = (
                amount_risk * 0.4 +
                history_risk * 0.4 +
                frequency_risk * 0.2
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            print(f"Risk calculation error: {e}")
            return 0.5  # Default medium risk

    def _determine_optimal_payment_terms(self, farmer_id: int, amount: float, risk_score: float) -> str:
        """Determine optimal payment terms based on risk analysis"""
        if risk_score < 0.2:
            return 'net_30'
        elif risk_score < 0.4:
            return 'net_15'
        elif risk_score < 0.6:
            return 'net_7'
        else:
            return 'immediate'

    def _generate_payment_schedule(self, amount: float, terms: str) -> List[Dict]:
        """Generate payment schedule based on terms"""
        payment_date = datetime.utcnow() + timedelta(days=self.payment_terms[terms])
        
        return [{
            'payment_date': payment_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'description': f'Payment due ({terms})'
        }]

    def _predict_payment_impact(self, amount: float, terms: str) -> Dict:
        """Predict impact of payment on cash flow"""
        days_delay = self.payment_terms[terms]
        
        return {
            'cash_flow_impact': -amount,
            'impact_date': (datetime.utcnow() + timedelta(days=days_delay)).strftime('%Y-%m-%d'),
            'liquidity_impact': 'low' if amount < 50000 else 'medium' if amount < 200000 else 'high'
        }

    def _generate_payment_recommendations(self, risk_score: float, terms: str) -> List[Dict]:
        """Generate payment recommendations"""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append({
                'category': 'risk_mitigation',
                'recommendation': 'Consider requiring advance payment or collateral',
                'priority': 'high'
            })
        
        if terms == 'immediate':
            recommendations.append({
                'category': 'payment_terms',
                'recommendation': 'Immediate payment required due to high risk profile',
                'priority': 'high'
            })
        
        return recommendations

    # Additional helper methods for invoice processing and financial calculations
    def _validate_invoice_data(self, invoice_data: Dict) -> Dict:
        """Validate invoice data"""
        errors = []

        if 'customer_id' not in invoice_data:
            errors.append('Customer ID is required')
        if 'items' not in invoice_data or not invoice_data['items']:
            errors.append('Invoice items are required')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _process_invoice_data(self, invoice_data: Dict) -> Dict:
        """Process and normalize invoice data"""
        return {
            'customer_id': invoice_data['customer_id'],
            'items': invoice_data['items'],
            'payment_terms': invoice_data.get('payment_terms', 30),
            'created_by': invoice_data.get('created_by', 1)
        }

    def _calculate_invoice_financials(self, processed_data: Dict) -> Dict:
        """Calculate invoice financial amounts"""
        subtotal = sum(item['quantity'] * item['unit_price'] for item in processed_data['items'])
        tax_rate = 0.18  # 18% GST
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'tax_rate': tax_rate
        }

    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        return f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _predict_invoice_payment(self, invoice) -> Dict:
        """Predict invoice payment likelihood and timing"""
        # Simplified prediction based on customer history and amount
        customer_id = invoice.customer_id
        amount = float(invoice.total_amount)

        # Get customer payment history
        customer_payments = Payment.query.filter_by(customer_id=customer_id).limit(10).all()

        if customer_payments:
            avg_payment_days = np.mean([(p.payment_date - p.created_at).days for p in customer_payments])
            payment_reliability = len([p for p in customer_payments if p.status == 'completed']) / len(customer_payments)
        else:
            avg_payment_days = 30
            payment_reliability = 0.7  # Default

        # Predict payment probability
        if amount < 50000:
            payment_probability = min(0.95, payment_reliability + 0.1)
        elif amount < 200000:
            payment_probability = payment_reliability
        else:
            payment_probability = max(0.5, payment_reliability - 0.1)

        return {
            'payment_probability': round(payment_probability, 2),
            'predicted_payment_days': round(avg_payment_days, 0),
            'risk_level': 'low' if payment_probability > 0.8 else 'medium' if payment_probability > 0.6 else 'high'
        }

    def _generate_invoice_recommendations(self, invoice, payment_prediction: Dict) -> List[Dict]:
        """Generate invoice-specific recommendations"""
        recommendations = []

        if payment_prediction['risk_level'] == 'high':
            recommendations.append({
                'category': 'payment_risk',
                'recommendation': 'Consider requiring advance payment or shorter payment terms',
                'priority': 'high'
            })

        if payment_prediction['predicted_payment_days'] > 45:
            recommendations.append({
                'category': 'collection',
                'recommendation': 'Implement proactive collection follow-up process',
                'priority': 'medium'
            })

        return recommendations

    # Financial ratio and metric calculations
    def _calculate_current_ratio(self) -> float:
        """Calculate current ratio (current assets / current liabilities)"""
        # In a real implementation, this would query actual balance sheet data
        return 1.5  # Placeholder

    def _calculate_debt_to_equity_ratio(self) -> float:
        """Calculate debt to equity ratio"""
        return 0.3  # Placeholder

    def _calculate_profit_margin(self) -> float:
        """Calculate profit margin from recent transactions"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        transactions = Transaction.query.filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()

        revenue = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
        expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')

        return ((revenue - expenses) / revenue * 100) if revenue > 0 else 0

    def _calculate_cash_flow_ratio(self) -> float:
        """Calculate cash flow ratio"""
        return 1.2  # Placeholder

    def _calculate_inventory_turnover(self) -> float:
        """Calculate inventory turnover ratio"""
        return 6.0  # Placeholder

    def _generate_health_recommendations(self, overall_score: float, health_grade: str) -> List[Dict]:
        """Generate financial health improvement recommendations"""
        recommendations = []

        if overall_score < 70:
            recommendations.append({
                'category': 'urgent_action',
                'priority': 'high',
                'recommendation': 'Immediate attention required to improve financial health',
                'action': 'Review cash flow management and reduce unnecessary expenses'
            })

        if health_grade in ['D', 'F']:
            recommendations.append({
                'category': 'liquidity_improvement',
                'priority': 'high',
                'recommendation': 'Focus on improving liquidity and cash flow',
                'action': 'Accelerate collections and optimize payment terms'
            })

        if overall_score < 80:
            recommendations.append({
                'category': 'efficiency_improvement',
                'priority': 'medium',
                'recommendation': 'Improve operational efficiency to boost profitability',
                'action': 'Analyze cost structure and identify optimization opportunities'
            })

        return recommendations

    # Payment optimization methods
    def _prioritize_payments(self, pending_payments: List) -> Dict:
        """Prioritize pending payments based on various factors"""
        high_priority = []
        medium_priority = []
        low_priority = []

        for payment in pending_payments:
            amount = float(payment.amount)
            days_pending = (datetime.utcnow() - payment.created_at).days

            # Priority scoring
            priority_score = 0
            if amount > 100000:
                priority_score += 3
            elif amount > 50000:
                priority_score += 2
            else:
                priority_score += 1

            if days_pending > 7:
                priority_score += 2
            elif days_pending > 3:
                priority_score += 1

            # Categorize
            if priority_score >= 4:
                high_priority.append(payment.to_dict())
            elif priority_score >= 2:
                medium_priority.append(payment.to_dict())
            else:
                low_priority.append(payment.to_dict())

        return {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority
        }

    def _optimize_payment_batching(self, pending_payments: List) -> List[Dict]:
        """Optimize payment batching for efficiency"""
        # Group payments by similar characteristics
        batches = []

        # Group by payment method and amount range
        bank_transfers = [p for p in pending_payments if getattr(p, 'payment_method', 'bank') == 'bank']
        cash_payments = [p for p in pending_payments if getattr(p, 'payment_method', 'bank') == 'cash']

        if bank_transfers:
            batches.append({
                'batch_type': 'bank_transfer',
                'payments': [p.to_dict() for p in bank_transfers],
                'total_amount': sum(float(p.amount) for p in bank_transfers),
                'processing_cost': len(bank_transfers) * 25,  # ₹25 per transfer
                'recommended_date': datetime.utcnow().strftime('%Y-%m-%d')
            })

        if cash_payments:
            batches.append({
                'batch_type': 'cash',
                'payments': [p.to_dict() for p in cash_payments],
                'total_amount': sum(float(p.amount) for p in cash_payments),
                'processing_cost': 0,  # No processing cost for cash
                'recommended_date': datetime.utcnow().strftime('%Y-%m-%d')
            })

        return batches

    def _calculate_optimization_savings(self, payment_batches: List[Dict]) -> Dict:
        """Calculate potential savings from payment optimization"""
        total_processing_cost = sum(batch['processing_cost'] for batch in payment_batches)

        # Estimate savings from batching (reduced administrative overhead)
        estimated_savings = total_processing_cost * 0.15  # 15% savings from batching

        return {
            'processing_cost_savings': estimated_savings,
            'administrative_time_saved_hours': len(payment_batches) * 0.5,  # 30 minutes per batch
            'total_estimated_savings': estimated_savings + (len(payment_batches) * 0.5 * 500)  # ₹500/hour labor cost
        }

    def _generate_payment_optimization_recommendations(self, payment_priorities: Dict, payment_batches: List[Dict]) -> List[Dict]:
        """Generate payment optimization recommendations"""
        recommendations = []

        high_priority_count = len(payment_priorities['high_priority'])
        if high_priority_count > 0:
            recommendations.append({
                'category': 'urgent_payments',
                'priority': 'high',
                'recommendation': f'Process {high_priority_count} high-priority payments immediately',
                'action': 'Review and approve high-priority payments today'
            })

        if len(payment_batches) > 1:
            recommendations.append({
                'category': 'batch_processing',
                'priority': 'medium',
                'recommendation': 'Implement batch processing to reduce costs',
                'action': 'Schedule batch payments for optimal efficiency'
            })

        return recommendations
