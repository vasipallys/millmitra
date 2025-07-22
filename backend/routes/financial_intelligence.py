"""
Financial Intelligence Routes
AI-powered financial analytics and smart payment management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from models import Payment, Expense, User, Farmer, Customer, Transaction, Invoice
from services.financial_intelligence_service import FinancialIntelligenceService
from extensions import db

financial_intelligence_bp = Blueprint('financial_intelligence', __name__)
financial_service = FinancialIntelligenceService()

@financial_intelligence_bp.route('/cash-flow/analyze', methods=['POST'])
@jwt_required()
def analyze_cash_flow():
    """Comprehensive cash flow analysis with AI predictions"""
    try:
        data = request.get_json()
        period_days = data.get('period_days', 30)
        
        result = financial_service.analyze_cash_flow(period_days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Cash flow analysis failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/payment/schedule', methods=['POST'])
@jwt_required()
def smart_payment_scheduling():
    """AI-powered optimal payment scheduling"""
    try:
        data = request.get_json()
        
        farmer_id = data.get('farmer_id')
        amount = data.get('amount')
        payment_type = data.get('payment_type', 'procurement')
        
        if not farmer_id or not amount:
            return jsonify({'error': 'Farmer ID and amount are required'}), 400
        
        result = financial_service.smart_payment_scheduling(farmer_id, amount, payment_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Payment scheduling failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/forecast', methods=['GET'])
@jwt_required()
def financial_forecasting():
    """Advanced financial forecasting using AI"""
    try:
        forecast_days = request.args.get('days', 90, type=int)
        
        result = financial_service.financial_forecasting(forecast_days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Financial forecasting failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/payment/optimize', methods=['GET'])
@jwt_required()
def payment_optimization():
    """Optimize payment processes using AI"""
    try:
        result = financial_service.payment_optimization()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Payment optimization failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/health-score', methods=['GET'])
@jwt_required()
def financial_health_score():
    """Calculate comprehensive financial health score"""
    try:
        result = financial_service.financial_health_score()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Financial health calculation failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/invoice/process', methods=['POST'])
@jwt_required()
def automated_invoice_processing():
    """AI-powered automated invoice processing"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user context to invoice data
        data['created_by'] = user_id
        
        result = financial_service.automated_invoice_processing(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Invoice processing failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def financial_dashboard():
    """Get comprehensive financial intelligence dashboard"""
    try:
        # Get cash flow analysis
        cash_flow = financial_service.analyze_cash_flow(30)
        
        # Get financial health score
        health_score = financial_service.financial_health_score()
        
        # Get payment optimization
        payment_opt = financial_service.payment_optimization()
        
        # Get recent transactions
        recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(10).all()
        
        # Get pending invoices
        pending_invoices = Invoice.query.filter_by(status='pending').limit(5).all()
        
        # Calculate key metrics
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        monthly_revenue = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= month_start
        ).scalar() or 0
        
        monthly_expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= month_start
        ).scalar() or 0
        
        dashboard_data = {
            'summary': {
                'monthly_revenue': float(monthly_revenue),
                'monthly_expenses': float(monthly_expenses),
                'monthly_profit': float(monthly_revenue - monthly_expenses),
                'profit_margin': ((monthly_revenue - monthly_expenses) / monthly_revenue * 100) if monthly_revenue > 0 else 0,
                'pending_payments': payment_opt.get('analysis', {}).get('total_pending_payments', 0),
                'pending_amount': payment_opt.get('analysis', {}).get('total_pending_amount', 0)
            },
            'cash_flow': cash_flow.get('summary', {}),
            'health_score': health_score,
            'payment_optimization': payment_opt.get('analysis', {}),
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'pending_invoices': [i.to_dict() for i in pending_invoices]
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Dashboard loading failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/insights', methods=['GET'])
@jwt_required()
def financial_insights():
    """Get AI-generated financial insights and recommendations"""
    try:
        # Get various analyses
        cash_flow = financial_service.analyze_cash_flow(30)
        health_score = financial_service.financial_health_score()
        forecast = financial_service.financial_forecasting(30)
        
        # Compile insights
        insights = []
        
        # Cash flow insights
        if cash_flow.get('success'):
            net_flow = cash_flow['summary']['net_cash_flow']
            if net_flow > 0:
                insights.append({
                    'category': 'cash_flow',
                    'type': 'positive',
                    'title': 'Positive Cash Flow',
                    'description': f'Strong cash flow of ₹{net_flow:,.0f} this month',
                    'recommendation': 'Consider investing surplus cash for better returns'
                })
            else:
                insights.append({
                    'category': 'cash_flow',
                    'type': 'warning',
                    'title': 'Negative Cash Flow',
                    'description': f'Cash outflow of ₹{abs(net_flow):,.0f} this month',
                    'recommendation': 'Review expenses and accelerate collections'
                })
        
        # Health score insights
        if health_score.get('success'):
            score = health_score['overall_score']
            grade = health_score['health_grade']
            
            if score >= 80:
                insights.append({
                    'category': 'financial_health',
                    'type': 'positive',
                    'title': f'Excellent Financial Health (Grade {grade})',
                    'description': f'Overall financial score: {score}/100',
                    'recommendation': 'Maintain current financial practices'
                })
            elif score >= 60:
                insights.append({
                    'category': 'financial_health',
                    'type': 'warning',
                    'title': f'Moderate Financial Health (Grade {grade})',
                    'description': f'Overall financial score: {score}/100',
                    'recommendation': 'Focus on improving key financial ratios'
                })
            else:
                insights.append({
                    'category': 'financial_health',
                    'type': 'critical',
                    'title': f'Poor Financial Health (Grade {grade})',
                    'description': f'Overall financial score: {score}/100',
                    'recommendation': 'Immediate action required to improve finances'
                })
        
        # Forecast insights
        if forecast.get('success') and forecast.get('key_insights'):
            for insight in forecast['key_insights']:
                insights.append({
                    'category': 'forecast',
                    'type': 'positive' if insight['impact'] == 'positive' else 'neutral',
                    'title': 'Financial Forecast',
                    'description': insight['insight'],
                    'recommendation': 'Monitor trends and adjust strategy accordingly'
                })
        
        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Insights generation failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/reports/cash-flow', methods=['GET'])
@jwt_required()
def cash_flow_report():
    """Generate detailed cash flow report"""
    try:
        period_days = request.args.get('days', 30, type=int)
        
        result = financial_service.analyze_cash_flow(period_days)
        
        if result['success']:
            # Add additional report formatting
            report = {
                'report_type': 'Cash Flow Analysis',
                'period': result['period'],
                'summary': result['summary'],
                'daily_data': result['daily_data'],
                'predictions': result['predictions'],
                'patterns': result['patterns'],
                'recommendations': result['recommendations'],
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': get_jwt_identity()
            }
            
            return jsonify({
                'success': True,
                'report': report
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Cash flow report generation failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/reports/financial-health', methods=['GET'])
@jwt_required()
def financial_health_report():
    """Generate detailed financial health report"""
    try:
        result = financial_service.financial_health_score()
        
        if result['success']:
            # Add additional report context
            report = {
                'report_type': 'Financial Health Assessment',
                'overall_assessment': {
                    'score': result['overall_score'],
                    'grade': result['health_grade'],
                    'status': result['health_status']
                },
                'component_analysis': result['component_scores'],
                'financial_ratios': result['financial_ratios'],
                'recommendations': result['recommendations'],
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': get_jwt_identity()
            }
            
            return jsonify({
                'success': True,
                'report': report
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Financial health report generation failed: {str(e)}'}), 500

@financial_intelligence_bp.route('/alerts', methods=['GET'])
@jwt_required()
def financial_alerts():
    """Get financial alerts and warnings"""
    try:
        alerts = []
        
        # Check cash flow
        cash_flow = financial_service.analyze_cash_flow(7)  # Last 7 days
        if cash_flow.get('success'):
            net_flow = cash_flow['summary']['net_cash_flow']
            if net_flow < -50000:
                alerts.append({
                    'type': 'critical',
                    'category': 'cash_flow',
                    'title': 'Critical Cash Flow Alert',
                    'message': f'Negative cash flow of ₹{abs(net_flow):,.0f} in the last 7 days',
                    'action_required': True,
                    'created_at': datetime.utcnow().isoformat()
                })
        
        # Check overdue payments
        overdue_payments = Payment.query.filter(
            Payment.status == 'pending',
            Payment.due_date < datetime.utcnow()
        ).count()
        
        if overdue_payments > 0:
            alerts.append({
                'type': 'warning',
                'category': 'payments',
                'title': 'Overdue Payments',
                'message': f'{overdue_payments} payments are overdue',
                'action_required': True,
                'created_at': datetime.utcnow().isoformat()
            })
        
        # Check financial health
        health = financial_service.financial_health_score()
        if health.get('success') and health['overall_score'] < 60:
            alerts.append({
                'type': 'warning',
                'category': 'financial_health',
                'title': 'Poor Financial Health',
                'message': f'Financial health score is {health["overall_score"]}/100',
                'action_required': True,
                'created_at': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'alert_count': len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Alert generation failed: {str(e)}'}), 500
