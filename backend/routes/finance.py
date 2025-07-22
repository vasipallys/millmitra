from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Payment, Expense, Budget
# Temporarily disabled until services are fixed
# from services.finance_service import FinanceService
# from services.ai_finance_service import AIFinanceService

finance_bp = Blueprint('finance', __name__)
# Temporarily disabled until services are fixed
# finance_service = FinanceService()
# ai_finance = AIFinanceService()

# Simple endpoints for frontend compatibility
@finance_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get invoices list for frontend compatibility"""
    limit = request.args.get('limit', 10, type=int)

    # Mock invoice data for now
    invoices = [
        {
            'id': 1,
            'invoice_number': 'INV-001',
            'customer_name': 'ABC Rice Traders',
            'amount': 50000,
            'status': 'paid',
            'date': '2024-01-15'
        },
        {
            'id': 2,
            'invoice_number': 'INV-002',
            'customer_name': 'XYZ Distributors',
            'amount': 75000,
            'status': 'pending',
            'date': '2024-01-20'
        }
    ]

    return jsonify({
        'invoices': invoices[:limit],
        'total': len(invoices),
        'message': 'Invoices loaded successfully'
    })

@finance_bp.route('/cash-flow', methods=['GET'])
@jwt_required()
def get_cash_flow():
    """Get cash flow data for frontend compatibility"""
    period = request.args.get('period', 'monthly')

    cash_flow = {
        'period': period,
        'inflow': 250000,
        'outflow': 180000,
        'net_flow': 70000,
        'balance': 320000,
        'trend': 'positive'
    }

    return jsonify({
        'cash_flow': cash_flow,
        'message': 'Cash flow data loaded successfully'
    })

@finance_bp.route('/accounts-receivable', methods=['GET'])
@jwt_required()
def get_accounts_receivable():
    """Get accounts receivable for frontend compatibility"""

    receivables = {
        'total_outstanding': 125000,
        'overdue_amount': 25000,
        'current_amount': 100000,
        'aging': {
            '0-30': 75000,
            '31-60': 30000,
            '61-90': 15000,
            '90+': 5000
        }
    }

    return jsonify({
        'receivables': receivables,
        'message': 'Accounts receivable loaded successfully'
    })

@finance_bp.route('/financial-summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    """Get financial summary for frontend compatibility"""
    period_days = request.args.get('period_days', 30, type=int)

    summary = {
        'period_days': period_days,
        'total_revenue': 500000,
        'total_expenses': 350000,
        'net_profit': 150000,
        'profit_margin': 30.0,
        'cash_position': 320000
    }

    return jsonify({
        'summary': summary,
        'message': 'Financial summary loaded successfully'
    })

@finance_bp.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    account = finance_service.create_chart_of_accounts(user, data)
    
    return jsonify({
        'success': True,
        'account': {
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type
        }
    }), 201

@finance_bp.route('/journal-entries', methods=['POST'])
@jwt_required()
def create_journal_entry():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI analysis of transaction
    ai_analysis = ai_finance.analyze_financial_impact(data)
    
    entry = finance_service.create_journal_entry(user, data)
    
    return jsonify({
        'success': True,
        'entry': {
            'id': entry.id,
            'entry_number': entry.entry_number,
            'description': entry.description
        },
        'ai_analysis': ai_analysis
    }), 201

@finance_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    invoice = finance_service.create_invoice(user, data)
    
    return jsonify({
        'success': True,
        'invoice': {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'total_amount': invoice.total_amount
        }
    }), 201

@finance_bp.route('/payments', methods=['POST'])
@jwt_required()
def record_payment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    payment = finance_service.record_payment(user, data)
    
    return jsonify({
        'success': True,
        'payment': {
            'id': payment.id,
            'payment_number': payment.payment_number,
            'amount': payment.amount
        }
    }), 201

@finance_bp.route('/summary')
@jwt_required()
def get_summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    summary = finance_service.get_financial_summary(start_date, end_date)
    
    # AI insights
    ai_insights = ai_finance.analyze_financial_trends(summary)
    
    return jsonify({
        'summary': summary,
        'ai_insights': ai_insights
    })

@finance_bp.route('/aging-report')
@jwt_required()
def get_aging_report():
    report_type = request.args.get('type', 'receivables')
    aging_data = finance_service.get_aging_report(report_type)
    
    return jsonify({
        'aging_report': aging_data,
        'report_type': report_type
    })


