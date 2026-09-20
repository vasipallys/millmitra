from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Payment, Expense, Budget
from models.financial import Invoice, Transaction
from models.sales import Customer, SalesOrder
from models.inventory import ProductStock
from extensions import db
from datetime import datetime, timedelta
from utils import current_user
from sqlalchemy import or_, func
import uuid

finance_bp = Blueprint('finance', __name__)


class _FinanceStub:
    class _Result:
        id = None
        account_code = None
        account_name = None
        account_type = None
        entry_number = None
        description = None
        invoice_number = None
        total_amount = 0
        payment_number = None
        amount = 0

        def to_dict(self):
            return {}

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            if name.startswith(('create_', 'record_')):
                return self._Result()
            return {}
        return _call


finance_service = _FinanceStub()
ai_finance = _FinanceStub()


def _find_product_stock(item):
    stock_pk = item.get('product_stock_id') or item.get('stock_id')
    if stock_pk not in (None, ''):
        try:
            stock = ProductStock.query.get(int(stock_pk))
            if stock:
                return stock
        except (TypeError, ValueError):
            pass
    product_id = item.get('product_id')
    if product_id:
        stock = ProductStock.query.filter_by(product_id=str(product_id)).first()
        if stock:
            return stock
    name = (item.get('description') or item.get('variety') or item.get('product_name') or '').strip()
    if not name:
        return None
    return ProductStock.query.filter(
        or_(
            ProductStock.product_name.ilike(f'%{name}%'),
            ProductStock.variety.ilike(f'%{name}%'),
            ProductStock.product_type.ilike(f'%{name}%'),
        )
    ).order_by(ProductStock.quantity.desc()).first()


def _deduct_invoice_stock(items):
    shortages = []
    for item in items:
        qty = float(item.get('quantity', 0) or 0)
        if qty <= 0:
            continue
        stock = _find_product_stock(item)
        label = item.get('description') or item.get('variety') or 'line item'
        if not stock:
            shortages.append(f'No product stock matching "{label}"')
            continue
        available = stock.quantity or 0
        if available < qty:
            shortages.append(
                f'Insufficient stock for {stock.product_name or stock.variety}: '
                f'{available:.0f} kg available, {qty:.0f} kg billed'
            )
            continue
        stock.quantity = available - qty
        if stock.quantity <= 0:
            stock.status = 'sold'
    return shortages


def _month_key(dt):
    return dt.strftime('%Y-%m') if dt else None


# Simple endpoints for frontend compatibility
@finance_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get invoices list for frontend compatibility"""
    limit = request.args.get('limit', 10, type=int)
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(limit).all()
    payload = []
    for invoice in invoices:
        customer = Customer.query.get(invoice.customer_id) if invoice.customer_id else None
        payload.append({
            **invoice.to_dict(),
            'customer_name': customer.name if customer else None,
            'customer': {'id': customer.id, 'name': customer.name} if customer else None,
            'amount': invoice.total_amount,
            'date': invoice.invoice_date.isoformat() if invoice.invoice_date else None
        })
    return jsonify({
        'invoices': payload,
        'total': Invoice.query.count(),
        'message': 'Invoices loaded successfully'
    })

@finance_bp.route('/cash-flow', methods=['GET'])
@jwt_required()
def get_cash_flow():
    period = request.args.get('period', 'monthly')
    months = {}
    for invoice in Invoice.query.all():
        key = _month_key(invoice.invoice_date)
        if not key:
            continue
        months.setdefault(key, {'date': key, 'inflow': 0, 'outflow': 0, 'netFlow': 0})
        months[key]['inflow'] += invoice.total_amount or 0
    try:
        for expense in Expense.query.all():
            key = _month_key(getattr(expense, 'expense_date', None) or getattr(expense, 'created_at', None))
            if not key:
                continue
            months.setdefault(key, {'date': key, 'inflow': 0, 'outflow': 0, 'netFlow': 0})
            months[key]['outflow'] += getattr(expense, 'amount', 0) or 0
    except Exception:
        db.session.rollback()
    series = []
    for key in sorted(months.keys())[-6:]:
        row = months[key]
        row['netFlow'] = row['inflow'] - row['outflow']
        series.append(row)
    inflow = sum(r['inflow'] for r in series)
    outflow = sum(r['outflow'] for r in series)
    return jsonify({
        'period': period,
        'inflow': inflow,
        'outflow': outflow,
        'net_flow': inflow - outflow,
        'series': series,
        'cash_flow': series,
        'message': 'Cash flow data loaded successfully'
    })

@finance_bp.route('/accounts-receivable', methods=['GET'])
@jwt_required()
def get_accounts_receivable():
    now = datetime.utcnow()
    unpaid = Invoice.query.filter(Invoice.status.in_(['pending', 'overdue', 'partial'])).all()
    overdue = [inv for inv in unpaid if inv.due_date and inv.due_date < now]
    aging = {'0-30': 0, '31-60': 0, '61-90': 0, '90+': 0}
    for inv in unpaid:
        days = (now - (inv.due_date or inv.invoice_date or now)).days if (inv.due_date or inv.invoice_date) else 0
        amount = inv.total_amount or 0
        if days <= 30:
            aging['0-30'] += amount
        elif days <= 60:
            aging['31-60'] += amount
        elif days <= 90:
            aging['61-90'] += amount
        else:
            aging['90+'] += amount
    outstanding = sum(inv.total_amount or 0 for inv in unpaid)
    overdue_amount = sum(inv.total_amount or 0 for inv in overdue)
    receivables = {
        'total_outstanding': outstanding,
        'overdue_amount': overdue_amount,
        'total_overdue': overdue_amount,
        'overdue_count': len(overdue),
        'current_amount': outstanding - overdue_amount,
        'aging': aging
    }
    return jsonify({
        **receivables,
        'receivables': receivables,
        'message': 'Accounts receivable loaded successfully'
    })

@finance_bp.route('/financial-summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    period_days = request.args.get('period_days', 30, type=int)
    start = datetime.utcnow() - timedelta(days=period_days)
    invoices = Invoice.query.filter(Invoice.invoice_date >= start).all()
    payments = Payment.query.filter(Payment.payment_date >= start).all() if hasattr(Payment, 'payment_date') else Payment.query.all()
    total_revenue = sum(inv.total_amount or 0 for inv in invoices if (inv.status or '') != 'cancelled')
    collected = sum(p.amount or 0 for p in payments)
    unpaid = Invoice.query.filter(Invoice.status.in_(['pending', 'overdue', 'partial'])).all()
    outstanding = sum(inv.total_amount or 0 for inv in unpaid)
    total_expenses = 0
    try:
        total_expenses = sum(getattr(e, 'amount', 0) or 0 for e in Expense.query.all())
    except Exception:
        db.session.rollback()
    net_profit = total_revenue - total_expenses
    summary = {
        'period_days': period_days,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'profit_margin': (net_profit / total_revenue * 100) if total_revenue else 0,
        'cash_position': collected,
        'outstanding_receivables': outstanding
    }
    return jsonify({
        **summary,
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
    user = current_user()
    data = request.get_json() or {}
    items = data.get('items') or data.get('invoice_items') or []
    subtotal = float(data.get('subtotal', 0) or 0)
    if not subtotal and items:
        subtotal = sum(float(item.get('quantity', 0) or 0) * float(item.get('unit_price', 0) or 0) for item in items)
    tax_amount = float(data.get('tax_amount', subtotal * 0.05) or 0)
    total_amount = float(data.get('total_amount', subtotal + tax_amount) or 0)

    invoice_date = datetime.utcnow()
    if data.get('invoice_date'):
        try:
            invoice_date = datetime.strptime(data['invoice_date'][:10], '%Y-%m-%d')
        except ValueError:
            pass
    due_date = invoice_date + timedelta(days=30)
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'][:10], '%Y-%m-%d')
        except ValueError:
            pass

    shortages = _deduct_invoice_stock(items)
    if shortages:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '; '.join(shortages)
        }), 400

    count = Invoice.query.count() + 1
    invoice = Invoice(
        invoice_number=f'INV{count:06d}',
        customer_id=data.get('customer_id'),
        invoice_date=invoice_date,
        due_date=due_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        payment_terms=data.get('payment_terms', 'net_30'),
        notes=data.get('notes'),
        invoice_items=items,
        created_by=user.id if user else None
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify({
        'success': True,
        'invoice': invoice.to_dict()
    }), 201

@finance_bp.route('/payments', methods=['POST'])
@jwt_required()
def record_payment():
    user = current_user()
    data = request.get_json() or {}
    amount = float(data.get('amount', 0) or 0)
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400

    payment_date = datetime.utcnow()
    if data.get('payment_date'):
        try:
            payment_date = datetime.strptime(str(data['payment_date'])[:10], '%Y-%m-%d')
        except ValueError:
            pass

    payment = Payment(
        payment_id=f'PAY{datetime.utcnow().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}',
        payment_type=data.get('payment_type', 'received'),
        payment_category=data.get('payment_category', 'customer_payment'),
        customer_id=data.get('customer_id'),
        farmer_id=data.get('farmer_id'),
        sales_order_id=data.get('sales_order_id'),
        amount=amount,
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number') or data.get('invoice_id'),
        payment_date=payment_date,
        status='cleared',
        description=data.get('notes'),
        created_by=user.id if user else None
    )
    db.session.add(payment)

    if data.get('invoice_id'):
        invoice = Invoice.query.get(data.get('invoice_id'))
        if invoice:
            invoice.status = 'paid'

    db.session.commit()
    result = payment.to_dict()
    result['payment_number'] = payment.payment_id
    return jsonify({
        'success': True,
        'payment': result
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


