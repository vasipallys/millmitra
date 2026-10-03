"""
Compliance and GST Routes
Automated regulatory compliance and tax management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import Transaction, Invoice, Customer, User
from services.compliance_gst_service import ComplianceGSTService
from extensions import db

compliance_gst_bp = Blueprint('compliance_gst', __name__)
compliance_service = ComplianceGSTService()

@compliance_gst_bp.route('/gst/calculate', methods=['POST'])
@jwt_required()
def calculate_gst():
    """Calculate GST for a transaction"""
    try:
        data = request.get_json()
        
        amount = data.get('amount')
        product_category = data.get('product_category', 'processed_rice')
        transaction_type = data.get('transaction_type', 'sale')
        
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400
        
        result = compliance_service.calculate_gst(amount, product_category, transaction_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'GST calculation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/invoice/generate', methods=['POST'])
@jwt_required()
def generate_gst_invoice():
    """Generate GST-compliant invoice"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user context
        data['created_by'] = user_id
        
        result = compliance_service.generate_gst_invoice(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Invoice generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/gstr1/<int:month>/<int:year>', methods=['GET'])
@jwt_required()
def generate_gstr1_report(month, year):
    """Generate GSTR-1 report"""
    try:
        result = compliance_service.generate_gstr1_report(month, year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'GSTR-1 generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/gstr3b/<int:month>/<int:year>', methods=['GET'])
@jwt_required()
def generate_gstr3b_report(month, year):
    """Generate GSTR-3B report"""
    try:
        result = compliance_service.generate_gstr3b_report(month, year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'GSTR-3B generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/compliance/status', methods=['GET'])
@jwt_required()
def check_compliance_status():
    """Check overall compliance status"""
    try:
        result = compliance_service.check_compliance_status()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Compliance check failed: {str(e)}'}), 500

@compliance_gst_bp.route('/gstin/validate', methods=['POST'])
@jwt_required()
def validate_gstin():
    """Validate GSTIN format and checksum"""
    try:
        data = request.get_json()
        gstin = data.get('gstin')
        
        if not gstin:
            return jsonify({'error': 'GSTIN is required'}), 400
        
        result = compliance_service.validate_gstin(gstin)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'GSTIN validation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/pan/validate', methods=['POST'])
@jwt_required()
def validate_pan():
    """Validate PAN format"""
    try:
        data = request.get_json()
        pan = data.get('pan')
        
        if not pan:
            return jsonify({'error': 'PAN is required'}), 400
        
        result = compliance_service.validate_pan(pan)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'PAN validation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_compliance_report():
    """Generate comprehensive compliance report"""
    try:
        data = request.get_json()
        
        report_type = data.get('report_type')
        period = data.get('period', {})
        
        if not report_type:
            return jsonify({'error': 'Report type is required'}), 400
        
        result = compliance_service.generate_compliance_report(report_type, period)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def compliance_dashboard():
    """Get compliance dashboard data"""
    try:
        result = compliance_service.get_compliance_dashboard_data()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Dashboard loading failed: {str(e)}'}), 500

@compliance_gst_bp.route('/calendar/<int:year>', methods=['GET'])
@jwt_required()
def compliance_calendar(year):
    """Get compliance calendar with due dates"""
    try:
        result = compliance_service.get_compliance_calendar(year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Calendar generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/tds/calculate', methods=['POST'])
@jwt_required()
def calculate_tds():
    """Calculate TDS for payment"""
    try:
        data = request.get_json()
        
        payment_amount = data.get('payment_amount')
        payment_type = data.get('payment_type')
        vendor_type = data.get('vendor_type', 'individual')
        
        if not payment_amount or not payment_type:
            return jsonify({'error': 'Payment amount and type are required'}), 400
        
        result = compliance_service.auto_calculate_tds(payment_amount, payment_type, vendor_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'TDS calculation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/tds/certificate', methods=['POST'])
@jwt_required()
def generate_tds_certificate():
    """Generate TDS certificate"""
    try:
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        quarter = data.get('quarter')
        year = data.get('year')
        
        if not all([payment_id, quarter, year]):
            return jsonify({'error': 'Payment ID, quarter, and year are required'}), 400
        
        result = compliance_service.generate_tds_certificate(payment_id, quarter, year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'TDS certificate generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/export/gst', methods=['POST'])
@jwt_required()
def export_gst_data():
    """Export GST data in various formats"""
    try:
        data = request.get_json()
        
        format_type = data.get('format', 'json')
        month = data.get('month')
        year = data.get('year')
        
        if not month or not year:
            return jsonify({'error': 'Month and year are required'}), 400
        
        result = compliance_service.export_gst_data(format_type, month, year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@compliance_gst_bp.route('/reconcile/gst', methods=['POST'])
@jwt_required()
def reconcile_gst_data():
    """Reconcile GST data between books and returns"""
    try:
        data = request.get_json()
        
        month = data.get('month')
        year = data.get('year')
        
        if not month or not year:
            return jsonify({'error': 'Month and year are required'}), 400
        
        result = compliance_service.reconcile_gst_data(month, year)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'GST reconciliation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/tax/summary', methods=['POST'])
@jwt_required()
def tax_summary():
    """Get comprehensive tax summary"""
    try:
        data = request.get_json()
        
        period = data.get('period', {})
        
        if not period.get('start_date') or not period.get('end_date'):
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        result = compliance_service.get_tax_summary(period)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Tax summary generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/reminders', methods=['GET'])
@jwt_required()
def compliance_reminders():
    """Get compliance reminders"""
    try:
        result = compliance_service.schedule_compliance_reminders()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Reminder generation failed: {str(e)}'}), 500

@compliance_gst_bp.route('/check/automated', methods=['POST'])
@jwt_required()
def automated_compliance_check():
    """Run automated compliance checks"""
    try:
        result = compliance_service.automated_compliance_check()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Automated compliance check failed: {str(e)}'}), 500

@compliance_gst_bp.route('/invoice/<invoice_id>/gst-details', methods=['GET'])
@jwt_required()
def get_invoice_gst_details(invoice_id):
    """Get GST details for a specific invoice"""
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        invoice_data = invoice.get_invoice_items()
        
        if not invoice_data:
            return jsonify({'error': 'Invoice GST details not found'}), 404
        
        return jsonify({
            'success': True,
            'invoice_gst_details': invoice_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get invoice GST details: {str(e)}'}), 500

@compliance_gst_bp.route('/hsn/codes', methods=['GET'])
@jwt_required()
def get_hsn_codes():
    """Get HSN codes for rice products"""
    try:
        hsn_codes = {
            '1006': {
                'description': 'Rice',
                'sub_codes': {
                    '100610': 'Rice in the husk (paddy or rough)',
                    '100620': 'Husked (brown) rice',
                    '100630': 'Semi-milled or wholly milled rice',
                    '100640': 'Broken rice'
                }
            },
            '2302': {
                'description': 'Brans, sharps and other residues',
                'sub_codes': {
                    '230240': 'Of rice'
                }
            }
        }
        
        return jsonify({
            'success': True,
            'hsn_codes': hsn_codes
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get HSN codes: {str(e)}'}), 500

@compliance_gst_bp.route('/gst/rates', methods=['GET'])
@jwt_required()
def get_gst_rates():
    """Get current GST rates for different products"""
    try:
        gst_rates = compliance_service.gst_rates
        
        return jsonify({
            'success': True,
            'gst_rates': gst_rates,
            'effective_date': '01-07-2017',
            'last_updated': '01-01-2024'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get GST rates: {str(e)}'}), 500

@compliance_gst_bp.route('/compliance/requirements', methods=['GET'])
@jwt_required()
def get_compliance_requirements():
    """Get compliance requirements for rice mill"""
    try:
        requirements = compliance_service.compliance_requirements
        
        return jsonify({
            'success': True,
            'compliance_requirements': requirements
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get compliance requirements: {str(e)}'}), 500


@compliance_gst_bp.route('/filings', methods=['GET'])
@jwt_required()
def list_gst_filings():
    from models.gst_filing import GstFilingRecord
    rows = GstFilingRecord.query.order_by(GstFilingRecord.recorded_at.desc()).all()
    return jsonify({'success': True, 'filings': [row.to_dict() for row in rows]})


@compliance_gst_bp.route('/filings', methods=['POST'])
@jwt_required()
def record_gst_filing():
    from models.gst_filing import GstFilingRecord
    from utils import current_user as load_user
    user = load_user()
    data = request.get_json() or {}
    form = (data.get('form') or data.get('task') or '').strip()
    if not form:
        return jsonify({'success': False, 'message': 'form is required'}), 400
    row = GstFilingRecord(
        form=form[:40],
        due_date=(data.get('due_date') or data.get('date') or '')[:20],
        amount=float(data.get('amount') or 0),
        notes=data.get('notes') or 'Recorded in MillMitra. Not a GSTN filing receipt.',
        status='recorded',
        created_by=user.id if user else None,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({'success': True, 'filing': row.to_dict()}), 201
