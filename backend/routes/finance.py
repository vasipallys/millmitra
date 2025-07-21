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
def get_financial_summary():
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


