from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_, or_
from models.finance import ChartOfAccounts, JournalEntry, Invoice, Payment, Budget
from models.user import User
from database import db

class FinanceService:
    def __init__(self):
        pass
    
    def create_chart_of_accounts(self, user: User, account_data: Dict):
        """Create new chart of accounts entry"""
        account = ChartOfAccounts(
            account_code=account_data['account_code'],
            account_name=account_data['account_name'],
            account_type=account_data['account_type'],
            parent_account_id=account_data.get('parent_account_id')
        )
        
        db.session.add(account)
        db.session.commit()
        return account
    
    def create_journal_entry(self, user: User, entry_data: Dict):
        """Create journal entry"""
        entry = JournalEntry(
            entry_number=self._generate_entry_number(),
            account_id=entry_data['account_id'],
            transaction_date=datetime.fromisoformat(entry_data['transaction_date']),
            description=entry_data['description'],
            debit_amount=entry_data.get('debit_amount', 0.0),
            credit_amount=entry_data.get('credit_amount', 0.0),
            reference_type=entry_data.get('reference_type'),
            reference_id=entry_data.get('reference_id'),
            created_by=user.id
        )
        
        db.session.add(entry)
        db.session.commit()
        return entry
    
    def create_invoice(self, user: User, invoice_data: Dict):
        """Create new invoice"""
        invoice = Invoice(
            invoice_number=self._generate_invoice_number(invoice_data['invoice_type']),
            invoice_type=invoice_data['invoice_type'],
            customer_id=invoice_data.get('customer_id'),
            supplier_id=invoice_data.get('supplier_id'),
            invoice_date=datetime.fromisoformat(invoice_data['invoice_date']),
            due_date=datetime.fromisoformat(invoice_data['due_date']),
            subtotal=invoice_data['subtotal'],
            tax_amount=invoice_data.get('tax_amount', 0.0),
            discount_amount=invoice_data.get('discount_amount', 0.0),
            total_amount=invoice_data['total_amount']
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Add invoice items
        for item_data in invoice_data.get('items', []):
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_name=item_data['product_name'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(item)
        
        db.session.commit()
        return invoice
    
    def record_payment(self, user: User, payment_data: Dict):
        """Record payment against invoice"""
        payment = Payment(
            payment_number=self._generate_payment_number(),
            invoice_id=payment_data['invoice_id'],
            payment_date=datetime.fromisoformat(payment_data['payment_date']),
            amount=payment_data['amount'],
            payment_method=payment_data['payment_method'],
            reference_number=payment_data.get('reference_number'),
            notes=payment_data.get('notes'),
            created_by=user.id
        )
        
        db.session.add(payment)
        
        # Update invoice paid amount
        invoice = Invoice.query.get(payment_data['invoice_id'])
        if invoice:
            invoice.paid_amount += payment_data['amount']
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
        
        db.session.commit()
        return payment
    
    def get_financial_summary(self, start_date: str, end_date: str):
        """Get financial summary for period"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Revenue
        revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.invoice_type == 'sales',
                Invoice.invoice_date.between(start, end)
            )
        ).scalar() or 0
        
        # Expenses
        expenses = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.invoice_type == 'purchase',
                Invoice.invoice_date.between(start, end)
            )
        ).scalar() or 0
        
        # Outstanding receivables
        receivables = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount)).filter(
            and_(
                Invoice.invoice_type == 'sales',
                Invoice.status != 'paid'
            )
        ).scalar() or 0
        
        # Outstanding payables
        payables = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount)).filter(
            and_(
                Invoice.invoice_type == 'purchase',
                Invoice.status != 'paid'
            )
        ).scalar() or 0
        
        return {
            'revenue': revenue,
            'expenses': expenses,
            'profit': revenue - expenses,
            'receivables': receivables,
            'payables': payables,
            'net_position': receivables - payables
        }
    
    def get_aging_report(self, report_type: str = 'receivables'):
        """Get aging report for receivables or payables"""
        today = datetime.now()
        
        invoice_type = 'sales' if report_type == 'receivables' else 'purchase'
        
        invoices = Invoice.query.filter(
            and_(
                Invoice.invoice_type == invoice_type,
                Invoice.status != 'paid'
            )
        ).all()
        
        aging_buckets = {
            'current': 0,
            '1-30_days': 0,
            '31-60_days': 0,
            '61-90_days': 0,
            'over_90_days': 0
        }
        
        for invoice in invoices:
            outstanding = invoice.total_amount - invoice.paid_amount
            days_overdue = (today - invoice.due_date).days
            
            if days_overdue <= 0:
                aging_buckets['current'] += outstanding
            elif days_overdue <= 30:
                aging_buckets['1-30_days'] += outstanding
            elif days_overdue <= 60:
                aging_buckets['31-60_days'] += outstanding
            elif days_overdue <= 90:
                aging_buckets['61-90_days'] += outstanding
            else:
                aging_buckets['over_90_days'] += outstanding
        
        return aging_buckets
    
    def _generate_entry_number(self):
        """Generate unique journal entry number"""
        today = datetime.now()
        prefix = f"JE{today.strftime('%Y%m')}"
        
        last_entry = JournalEntry.query.filter(
            JournalEntry.entry_number.like(f"{prefix}%")
        ).order_by(JournalEntry.id.desc()).first()
        
        if last_entry:
            last_num = int(last_entry.entry_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def _generate_invoice_number(self, invoice_type: str):
        """Generate unique invoice number"""
        today = datetime.now()
        prefix = f"{'SI' if invoice_type == 'sales' else 'PI'}{today.strftime('%Y%m')}"
        
        last_invoice = Invoice.query.filter(
            and_(
                Invoice.invoice_number.like(f"{prefix}%"),
                Invoice.invoice_type == invoice_type
            )
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            last_num = int(last_invoice.invoice_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def _generate_payment_number(self):
        """Generate unique payment number"""
        today = datetime.now()
        prefix = f"PAY{today.strftime('%Y%m')}"
        
        last_payment = Payment.query.filter(
            Payment.payment_number.like(f"{prefix}%")
        ).order_by(Payment.id.desc()).first()
        
        if last_payment:
            last_num = int(last_payment.payment_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"

