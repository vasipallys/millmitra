"""
Compliance and GST Service
Automated regulatory compliance and tax management for rice mill operations
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
import re

from extensions import db
from services.tenant_scope import tq, t_get, t_get_or_404
from models import Transaction, Invoice, Customer, Farmer, ProductionBatch

class ComplianceGSTService:
    def __init__(self):
        # GST rates for different rice categories
        self.gst_rates = {
            'raw_rice': 5.0,      # 5% GST on raw rice
            'processed_rice': 5.0, # 5% GST on processed rice
            'premium_rice': 5.0,   # 5% GST on premium varieties
            'broken_rice': 5.0,    # 5% GST on broken rice
            'rice_bran': 5.0,      # 5% GST on rice bran
            'paddy': 0.0,          # 0% GST on paddy (agricultural produce)
            'services': 18.0       # 18% GST on services
        }
        
        # Compliance requirements
        self.compliance_requirements = {
            'gst_filing': {
                'gstr1_monthly': True,
                'gstr3b_monthly': True,
                'gstr9_annual': True,
                'due_dates': {
                    'gstr1': 11,  # 11th of next month
                    'gstr3b': 20, # 20th of next month
                    'gstr9': 31   # 31st December of next year
                }
            },
            'fssai': {
                'license_required': True,
                'renewal_period_months': 12,
                'compliance_checks': ['hygiene', 'quality', 'labeling']
            },
            'pollution_control': {
                'consent_to_operate': True,
                'water_pollution_clearance': True,
                'air_pollution_clearance': True
            },
            'labor_compliance': {
                'pf_registration': True,
                'esi_registration': True,
                'minimum_wage_compliance': True
            }
        }

    def calculate_gst(self, amount: float, product_category: str, transaction_type: str = 'sale') -> Dict:
        """Calculate GST for a transaction"""
        try:
            # Get applicable GST rate
            gst_rate = self.gst_rates.get(product_category, 5.0)
            
            # Calculate GST amounts
            base_amount = Decimal(str(amount))
            gst_rate_decimal = Decimal(str(gst_rate))
            
            if transaction_type == 'sale':
                # For sales, GST is added to the base amount
                gst_amount = (base_amount * gst_rate_decimal / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                total_amount = base_amount + gst_amount
                
                # Split GST into CGST and SGST (equal halves for intra-state)
                cgst = (gst_amount / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                sgst = gst_amount - cgst
                igst = Decimal('0.00')  # For inter-state transactions
                
            else:  # purchase
                # For purchases, GST is included in the amount
                total_amount = base_amount
                gst_amount = (base_amount * gst_rate_decimal / (100 + gst_rate_decimal)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                base_amount = total_amount - gst_amount
                
                cgst = (gst_amount / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                sgst = gst_amount - cgst
                igst = Decimal('0.00')
            
            return {
                'success': True,
                'base_amount': float(base_amount),
                'gst_rate': float(gst_rate),
                'gst_amount': float(gst_amount),
                'cgst': float(cgst),
                'sgst': float(sgst),
                'igst': float(igst),
                'total_amount': float(total_amount),
                'product_category': product_category,
                'transaction_type': transaction_type
            }
            
        except Exception as e:
            return {'success': False, 'error': f'GST calculation failed: {str(e)}'}

    def generate_gst_invoice(self, invoice_data: Dict) -> Dict:
        """Generate GST-compliant invoice"""
        try:
            # Validate required fields
            required_fields = ['customer_id', 'items', 'invoice_date']
            for field in required_fields:
                if field not in invoice_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Get customer details
            customer = t_get(Customer, invoice_data['customer_id'])
            if not customer:
                return {'success': False, 'error': 'Customer not found'}
            
            # Generate invoice number
            invoice_number = self._generate_gst_invoice_number()
            
            # Calculate line items with GST
            invoice_items = []
            total_base_amount = Decimal('0.00')
            total_gst_amount = Decimal('0.00')
            total_cgst = Decimal('0.00')
            total_sgst = Decimal('0.00')
            total_igst = Decimal('0.00')
            
            for item in invoice_data['items']:
                line_amount = Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
                
                # Calculate GST for this line item
                gst_calc = self.calculate_gst(
                    float(line_amount), 
                    item.get('product_category', 'processed_rice'),
                    'sale'
                )
                
                if not gst_calc['success']:
                    return gst_calc
                
                invoice_item = {
                    'description': item['description'],
                    'hsn_code': item.get('hsn_code', '1006'),  # HSN code for rice
                    'quantity': item['quantity'],
                    'unit': item.get('unit', 'KG'),
                    'unit_price': item['unit_price'],
                    'line_amount': gst_calc['base_amount'],
                    'gst_rate': gst_calc['gst_rate'],
                    'cgst': gst_calc['cgst'],
                    'sgst': gst_calc['sgst'],
                    'igst': gst_calc['igst'],
                    'total_amount': gst_calc['total_amount']
                }
                
                invoice_items.append(invoice_item)
                
                total_base_amount += Decimal(str(gst_calc['base_amount']))
                total_gst_amount += Decimal(str(gst_calc['gst_amount']))
                total_cgst += Decimal(str(gst_calc['cgst']))
                total_sgst += Decimal(str(gst_calc['sgst']))
                total_igst += Decimal(str(gst_calc['igst']))
            
            # Create GST invoice
            gst_invoice = {
                'invoice_number': invoice_number,
                'invoice_date': invoice_data['invoice_date'],
                'customer_details': {
                    'name': customer.name,
                    'address': getattr(customer, 'address', ''),
                    'gstin': getattr(customer, 'gstin', ''),
                    'state_code': getattr(customer, 'state_code', ''),
                    'phone': getattr(customer, 'phone', ''),
                    'email': getattr(customer, 'email', '')
                },
                'supplier_details': {
                    'name': 'Rice Mill Management System',
                    'address': 'Mill Address',
                    'gstin': 'MILL_GSTIN_NUMBER',
                    'state_code': '06',  # Haryana state code
                    'phone': '+91-XXXXXXXXXX',
                    'email': 'info@ricemill.com'
                },
                'items': invoice_items,
                'totals': {
                    'base_amount': float(total_base_amount),
                    'total_cgst': float(total_cgst),
                    'total_sgst': float(total_sgst),
                    'total_igst': float(total_igst),
                    'total_gst': float(total_gst_amount),
                    'grand_total': float(total_base_amount + total_gst_amount)
                },
                'payment_terms': invoice_data.get('payment_terms', 'Net 30'),
                'due_date': invoice_data.get('due_date'),
                'place_of_supply': invoice_data.get('place_of_supply', 'Haryana'),
                'reverse_charge': invoice_data.get('reverse_charge', False)
            }
            
            # Store invoice in database
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=invoice_data['customer_id'],
                invoice_date=datetime.fromisoformat(invoice_data['invoice_date']),
                due_date=datetime.fromisoformat(invoice_data['due_date']) if invoice_data.get('due_date') else None,
                subtotal=float(total_base_amount),
                tax_amount=float(total_gst_amount),
                total_amount=float(total_base_amount + total_gst_amount),
                status='pending',
                created_by=invoice_data.get('created_by', 1)
            )
            
            invoice.set_invoice_items(gst_invoice)
            db.session.add(invoice)
            db.session.commit()
            
            return {
                'success': True,
                'invoice': gst_invoice,
                'invoice_id': invoice.id
            }
            
        except Exception as e:
            return {'success': False, 'error': f'GST invoice generation failed: {str(e)}'}

    def generate_gstr1_report(self, month: int, year: int) -> Dict:
        """Generate GSTR-1 report for the specified month"""
        try:
            # Get date range for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get all invoices for the period
            invoices = tq(Invoice).filter(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            ).all()
            
            # Process invoices for GSTR-1
            b2b_invoices = []  # Business to Business
            b2c_invoices = []  # Business to Consumer
            total_taxable_value = Decimal('0.00')
            total_tax_amount = Decimal('0.00')
            
            for invoice in invoices:
                invoice_data = invoice.get_invoice_items()
                
                if not invoice_data:
                    continue
                
                customer = t_get(Customer, invoice.customer_id)
                customer_gstin = getattr(customer, 'gstin', '') if customer else ''
                
                invoice_summary = {
                    'invoice_number': invoice.invoice_number,
                    'invoice_date': invoice.invoice_date.strftime('%d-%m-%Y'),
                    'customer_name': customer.name if customer else 'Unknown',
                    'customer_gstin': customer_gstin,
                    'place_of_supply': invoice_data.get('place_of_supply', 'Haryana'),
                    'taxable_value': invoice_data['totals']['base_amount'],
                    'cgst': invoice_data['totals']['total_cgst'],
                    'sgst': invoice_data['totals']['total_sgst'],
                    'igst': invoice_data['totals']['total_igst'],
                    'total_tax': invoice_data['totals']['total_gst'],
                    'invoice_value': invoice_data['totals']['grand_total']
                }
                
                # Categorize based on customer GSTIN
                if customer_gstin and len(customer_gstin) == 15:
                    b2b_invoices.append(invoice_summary)
                else:
                    b2c_invoices.append(invoice_summary)
                
                total_taxable_value += Decimal(str(invoice_summary['taxable_value']))
                total_tax_amount += Decimal(str(invoice_summary['total_tax']))
            
            # Generate GSTR-1 summary
            gstr1_report = {
                'period': f"{month:02d}-{year}",
                'generated_on': datetime.utcnow().isoformat(),
                'summary': {
                    'total_invoices': len(invoices),
                    'b2b_invoices': len(b2b_invoices),
                    'b2c_invoices': len(b2c_invoices),
                    'total_taxable_value': float(total_taxable_value),
                    'total_tax_amount': float(total_tax_amount),
                    'total_invoice_value': float(total_taxable_value + total_tax_amount)
                },
                'b2b_details': b2b_invoices,
                'b2c_details': b2c_invoices,
                'hsn_summary': self._generate_hsn_summary(invoices),
                'filing_status': 'draft',
                'due_date': self._get_gstr1_due_date(month, year)
            }
            
            return {
                'success': True,
                'gstr1_report': gstr1_report
            }
            
        except Exception as e:
            return {'success': False, 'error': f'GSTR-1 generation failed: {str(e)}'}

    def generate_gstr3b_report(self, month: int, year: int) -> Dict:
        """Generate GSTR-3B report for the specified month"""
        try:
            # Get date range
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get outward supplies (sales)
            sales_invoices = tq(Invoice).filter(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            ).all()
            
            # Calculate outward supplies
            outward_taxable = Decimal('0.00')
            outward_cgst = Decimal('0.00')
            outward_sgst = Decimal('0.00')
            outward_igst = Decimal('0.00')
            
            for invoice in sales_invoices:
                invoice_data = invoice.get_invoice_items()
                if invoice_data:
                    outward_taxable += Decimal(str(invoice_data['totals']['base_amount']))
                    outward_cgst += Decimal(str(invoice_data['totals']['total_cgst']))
                    outward_sgst += Decimal(str(invoice_data['totals']['total_sgst']))
                    outward_igst += Decimal(str(invoice_data['totals']['total_igst']))
            
            # Get inward supplies (purchases) - simplified
            # In a real implementation, this would come from purchase invoices
            inward_taxable = Decimal('500000.00')  # Mock data
            inward_cgst = Decimal('12500.00')
            inward_sgst = Decimal('12500.00')
            inward_igst = Decimal('0.00')
            
            # Calculate net tax liability
            net_cgst = outward_cgst - inward_cgst
            net_sgst = outward_sgst - inward_sgst
            net_igst = outward_igst - inward_igst
            
            # GSTR-3B report structure
            gstr3b_report = {
                'period': f"{month:02d}-{year}",
                'generated_on': datetime.utcnow().isoformat(),
                'outward_supplies': {
                    'taxable_value': float(outward_taxable),
                    'cgst': float(outward_cgst),
                    'sgst': float(outward_sgst),
                    'igst': float(outward_igst),
                    'total_tax': float(outward_cgst + outward_sgst + outward_igst)
                },
                'inward_supplies': {
                    'taxable_value': float(inward_taxable),
                    'cgst': float(inward_cgst),
                    'sgst': float(inward_sgst),
                    'igst': float(inward_igst),
                    'total_tax': float(inward_cgst + inward_sgst + inward_igst)
                },
                'net_tax_liability': {
                    'cgst': float(max(net_cgst, 0)),
                    'sgst': float(max(net_sgst, 0)),
                    'igst': float(max(net_igst, 0)),
                    'total': float(max(net_cgst, 0) + max(net_sgst, 0) + max(net_igst, 0))
                },
                'input_tax_credit': {
                    'cgst': float(inward_cgst),
                    'sgst': float(inward_sgst),
                    'igst': float(inward_igst),
                    'total': float(inward_cgst + inward_sgst + inward_igst)
                },
                'filing_status': 'draft',
                'due_date': self._get_gstr3b_due_date(month, year)
            }
            
            return {
                'success': True,
                'gstr3b_report': gstr3b_report
            }
            
        except Exception as e:
            return {'success': False, 'error': f'GSTR-3B generation failed: {str(e)}'}

    def check_compliance_status(self) -> Dict:
        """Check overall compliance status"""
        try:
            compliance_status = {
                'overall_status': 'compliant',
                'compliance_score': 0,
                'checks': [],
                'alerts': [],
                'recommendations': []
            }
            
            # Check GST compliance
            gst_compliance = self._check_gst_compliance()
            compliance_status['checks'].append(gst_compliance)
            
            # Check FSSAI compliance
            fssai_compliance = self._check_fssai_compliance()
            compliance_status['checks'].append(fssai_compliance)
            
            # Check pollution control compliance
            pollution_compliance = self._check_pollution_compliance()
            compliance_status['checks'].append(pollution_compliance)
            
            # Check labor compliance
            labor_compliance = self._check_labor_compliance()
            compliance_status['checks'].append(labor_compliance)
            
            # Calculate overall compliance score
            total_score = sum(check['score'] for check in compliance_status['checks'])
            compliance_status['compliance_score'] = total_score / len(compliance_status['checks'])
            
            # Determine overall status
            if compliance_status['compliance_score'] >= 90:
                compliance_status['overall_status'] = 'excellent'
            elif compliance_status['compliance_score'] >= 75:
                compliance_status['overall_status'] = 'good'
            elif compliance_status['compliance_score'] >= 60:
                compliance_status['overall_status'] = 'fair'
            else:
                compliance_status['overall_status'] = 'poor'
            
            # Generate alerts for non-compliant items
            for check in compliance_status['checks']:
                if check['score'] < 80:
                    compliance_status['alerts'].append({
                        'type': 'compliance_issue',
                        'category': check['category'],
                        'message': f"{check['category']} compliance needs attention",
                        'severity': 'high' if check['score'] < 60 else 'medium'
                    })
            
            # Generate recommendations
            compliance_status['recommendations'] = self._generate_compliance_recommendations(compliance_status['checks'])
            
            return {
                'success': True,
                'compliance_status': compliance_status
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Compliance check failed: {str(e)}'}

    def validate_gstin(self, gstin: str) -> Dict:
        """Validate GSTIN format and checksum"""
        try:
            if not gstin or len(gstin) != 15:
                return {'valid': False, 'error': 'GSTIN must be 15 characters long'}
            
            # GSTIN format: 2 digits state code + 10 digits PAN + 1 digit entity code + 1 digit Z + 1 digit checksum
            gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
            
            if not re.match(gstin_pattern, gstin):
                return {'valid': False, 'error': 'Invalid GSTIN format'}
            
            # Extract components
            state_code = gstin[:2]
            pan = gstin[2:12]
            entity_code = gstin[12]
            z_char = gstin[13]
            checksum = gstin[14]
            
            # Validate state code (01-37)
            if not (1 <= int(state_code) <= 37):
                return {'valid': False, 'error': 'Invalid state code'}
            
            # Validate checksum (simplified)
            calculated_checksum = self._calculate_gstin_checksum(gstin[:14])
            if calculated_checksum != checksum:
                return {'valid': False, 'error': 'Invalid checksum'}
            
            return {
                'valid': True,
                'state_code': state_code,
                'pan': pan,
                'entity_code': entity_code,
                'checksum_valid': True
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'GSTIN validation failed: {str(e)}'}

    def generate_compliance_report(self, report_type: str, period: Dict) -> Dict:
        """Generate comprehensive compliance report"""
        try:
            if report_type == 'monthly_gst':
                return self._generate_monthly_gst_report(period)
            elif report_type == 'annual_compliance':
                return self._generate_annual_compliance_report(period)
            elif report_type == 'audit_trail':
                return self._generate_audit_trail_report(period)
            else:
                return {'success': False, 'error': 'Invalid report type'}
                
        except Exception as e:
            return {'success': False, 'error': f'Report generation failed: {str(e)}'}

    # Helper methods
    def _generate_gst_invoice_number(self) -> str:
        """Generate GST-compliant invoice number"""
        return f"GST{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _generate_hsn_summary(self, invoices: List) -> List[Dict]:
        """Generate HSN-wise summary for GSTR-1"""
        hsn_summary = {}
        
        for invoice in invoices:
            invoice_data = invoice.get_invoice_items()
            if not invoice_data:
                continue
                
            for item in invoice_data.get('items', []):
                hsn_code = item.get('hsn_code', '1006')
                
                if hsn_code not in hsn_summary:
                    hsn_summary[hsn_code] = {
                        'hsn_code': hsn_code,
                        'description': 'Rice and Rice Products',
                        'uqc': 'KGS',
                        'total_quantity': 0,
                        'total_value': 0,
                        'taxable_value': 0,
                        'cgst': 0,
                        'sgst': 0,
                        'igst': 0
                    }
                
                hsn_summary[hsn_code]['total_quantity'] += item.get('quantity', 0)
                hsn_summary[hsn_code]['total_value'] += item.get('total_amount', 0)
                hsn_summary[hsn_code]['taxable_value'] += item.get('line_amount', 0)
                hsn_summary[hsn_code]['cgst'] += item.get('cgst', 0)
                hsn_summary[hsn_code]['sgst'] += item.get('sgst', 0)
                hsn_summary[hsn_code]['igst'] += item.get('igst', 0)
        
        return list(hsn_summary.values())

    def _get_gstr1_due_date(self, month: int, year: int) -> str:
        """Get GSTR-1 due date"""
        if month == 12:
            due_date = datetime(year + 1, 1, 11)
        else:
            due_date = datetime(year, month + 1, 11)
        return due_date.strftime('%d-%m-%Y')

    def _get_gstr3b_due_date(self, month: int, year: int) -> str:
        """Get GSTR-3B due date"""
        if month == 12:
            due_date = datetime(year + 1, 1, 20)
        else:
            due_date = datetime(year, month + 1, 20)
        return due_date.strftime('%d-%m-%Y')

    def _calculate_gstin_checksum(self, gstin_partial: str) -> str:
        """Calculate GSTIN checksum (simplified)"""
        # Simplified checksum calculation
        # In a real implementation, use the official GSTIN checksum algorithm
        checksum_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        total = sum(ord(char) for char in gstin_partial)
        return checksum_chars[total % 36]

    def _check_gst_compliance(self) -> Dict:
        """Check GST compliance status"""
        try:
            current_date = datetime.utcnow()
            current_month = current_date.month
            current_year = current_date.year

            # Check if GSTR-1 and GSTR-3B are filed for last month
            last_month = current_month - 1 if current_month > 1 else 12
            last_year = current_year if current_month > 1 else current_year - 1

            # Mock compliance check (in real implementation, check actual filing status)
            gstr1_filed = True  # Check from database
            gstr3b_filed = True  # Check from database

            score = 100
            issues = []

            if not gstr1_filed:
                score -= 25
                issues.append('GSTR-1 not filed for last month')

            if not gstr3b_filed:
                score -= 25
                issues.append('GSTR-3B not filed for last month')

            # Check for overdue returns
            overdue_returns = 0  # Calculate from database
            if overdue_returns > 0:
                score -= (overdue_returns * 10)
                issues.append(f'{overdue_returns} overdue GST returns')

            return {
                'category': 'GST Compliance',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues,
                'last_filing': {
                    'gstr1': f"{last_month:02d}-{last_year}",
                    'gstr3b': f"{last_month:02d}-{last_year}"
                }
            }

        except Exception as e:
            return {
                'category': 'GST Compliance',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking GST compliance: {str(e)}']
            }

    def _check_fssai_compliance(self) -> Dict:
        """Check FSSAI compliance status"""
        try:
            # Mock FSSAI compliance check
            license_valid = True
            license_expiry = datetime(2024, 12, 31)  # Mock expiry date
            current_date = datetime.utcnow()

            score = 100
            issues = []

            if not license_valid:
                score -= 50
                issues.append('FSSAI license invalid or expired')
            elif (license_expiry - current_date).days < 30:
                score -= 20
                issues.append('FSSAI license expiring within 30 days')

            # Check compliance requirements
            hygiene_compliance = True  # Mock data
            quality_compliance = True
            labeling_compliance = True

            if not hygiene_compliance:
                score -= 15
                issues.append('Hygiene standards not met')

            if not quality_compliance:
                score -= 15
                issues.append('Quality standards not met')

            if not labeling_compliance:
                score -= 10
                issues.append('Product labeling non-compliant')

            return {
                'category': 'FSSAI Compliance',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues,
                'license_expiry': license_expiry.strftime('%d-%m-%Y'),
                'days_to_expiry': (license_expiry - current_date).days
            }

        except Exception as e:
            return {
                'category': 'FSSAI Compliance',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking FSSAI compliance: {str(e)}']
            }

    def _check_pollution_compliance(self) -> Dict:
        """Check pollution control compliance"""
        try:
            # Mock pollution compliance check
            consent_to_operate = True
            water_clearance = True
            air_clearance = True

            score = 100
            issues = []

            if not consent_to_operate:
                score -= 40
                issues.append('Consent to Operate not obtained')

            if not water_clearance:
                score -= 30
                issues.append('Water pollution clearance pending')

            if not air_clearance:
                score -= 30
                issues.append('Air pollution clearance pending')

            return {
                'category': 'Pollution Control',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues,
                'clearances': {
                    'consent_to_operate': consent_to_operate,
                    'water_pollution': water_clearance,
                    'air_pollution': air_clearance
                }
            }

        except Exception as e:
            return {
                'category': 'Pollution Control',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking pollution compliance: {str(e)}']
            }

    def _check_labor_compliance(self) -> Dict:
        """Check labor law compliance"""
        try:
            # Mock labor compliance check
            pf_registered = True
            esi_registered = True
            minimum_wage_compliant = True

            score = 100
            issues = []

            if not pf_registered:
                score -= 35
                issues.append('PF registration required')

            if not esi_registered:
                score -= 35
                issues.append('ESI registration required')

            if not minimum_wage_compliant:
                score -= 30
                issues.append('Minimum wage compliance issues')

            return {
                'category': 'Labor Compliance',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues,
                'registrations': {
                    'pf_registered': pf_registered,
                    'esi_registered': esi_registered,
                    'minimum_wage_compliant': minimum_wage_compliant
                }
            }

        except Exception as e:
            return {
                'category': 'Labor Compliance',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking labor compliance: {str(e)}']
            }

    def _generate_compliance_recommendations(self, checks: List[Dict]) -> List[Dict]:
        """Generate compliance improvement recommendations"""
        recommendations = []

        for check in checks:
            if check['score'] < 80:
                for issue in check['issues']:
                    if 'GSTR' in issue:
                        recommendations.append({
                            'category': 'GST Filing',
                            'priority': 'high',
                            'recommendation': 'File pending GST returns immediately to avoid penalties',
                            'action': 'Complete and submit overdue GSTR-1 and GSTR-3B returns'
                        })
                    elif 'FSSAI' in issue:
                        recommendations.append({
                            'category': 'FSSAI License',
                            'priority': 'high',
                            'recommendation': 'Renew FSSAI license before expiry',
                            'action': 'Submit renewal application with required documents'
                        })
                    elif 'pollution' in issue.lower():
                        recommendations.append({
                            'category': 'Environmental Clearance',
                            'priority': 'medium',
                            'recommendation': 'Obtain required pollution control clearances',
                            'action': 'Apply for consent to operate and pollution clearances'
                        })
                    elif 'labor' in issue.lower() or 'PF' in issue or 'ESI' in issue:
                        recommendations.append({
                            'category': 'Labor Law Compliance',
                            'priority': 'medium',
                            'recommendation': 'Complete labor law registrations',
                            'action': 'Register for PF and ESI, ensure minimum wage compliance'
                        })

        return recommendations

    def _generate_monthly_gst_report(self, period: Dict) -> Dict:
        """Generate monthly GST compliance report"""
        try:
            month = period['month']
            year = period['year']

            # Get GSTR-1 and GSTR-3B data
            gstr1_data = self.generate_gstr1_report(month, year)
            gstr3b_data = self.generate_gstr3b_report(month, year)

            if not gstr1_data['success'] or not gstr3b_data['success']:
                return {'success': False, 'error': 'Failed to generate GST data'}

            report = {
                'report_type': 'Monthly GST Report',
                'period': f"{month:02d}-{year}",
                'generated_on': datetime.utcnow().isoformat(),
                'gstr1_summary': gstr1_data['gstr1_report']['summary'],
                'gstr3b_summary': gstr3b_data['gstr3b_report'],
                'compliance_status': 'compliant',
                'key_metrics': {
                    'total_sales': gstr1_data['gstr1_report']['summary']['total_invoice_value'],
                    'total_tax_collected': gstr1_data['gstr1_report']['summary']['total_tax_amount'],
                    'net_tax_liability': gstr3b_data['gstr3b_report']['net_tax_liability']['total'],
                    'input_tax_credit': gstr3b_data['gstr3b_report']['input_tax_credit']['total']
                },
                'recommendations': [
                    'File GSTR-1 by due date',
                    'File GSTR-3B by due date',
                    'Maintain proper invoice records'
                ]
            }

            return {'success': True, 'report': report}

        except Exception as e:
            return {'success': False, 'error': f'Monthly GST report generation failed: {str(e)}'}

    def _generate_annual_compliance_report(self, period: Dict) -> Dict:
        """Generate annual compliance report"""
        try:
            year = period['year']

            # Get compliance status for all areas
            compliance_status = self.check_compliance_status()

            if not compliance_status['success']:
                return compliance_status

            report = {
                'report_type': 'Annual Compliance Report',
                'year': year,
                'generated_on': datetime.utcnow().isoformat(),
                'overall_compliance': compliance_status['compliance_status'],
                'annual_summary': {
                    'total_gst_collected': 1250000,  # Mock data
                    'total_gst_paid': 1180000,
                    'compliance_score': compliance_status['compliance_status']['compliance_score'],
                    'major_violations': 0,
                    'penalties_paid': 0
                },
                'compliance_areas': compliance_status['compliance_status']['checks'],
                'recommendations': compliance_status['compliance_status']['recommendations'],
                'action_plan': [
                    'Maintain regular GST filing schedule',
                    'Renew all licenses before expiry',
                    'Conduct quarterly compliance audits',
                    'Update compliance procedures'
                ]
            }

            return {'success': True, 'report': report}

        except Exception as e:
            return {'success': False, 'error': f'Annual compliance report generation failed: {str(e)}'}

    def _generate_audit_trail_report(self, period: Dict) -> Dict:
        """Generate audit trail report"""
        try:
            start_date = datetime.fromisoformat(period['start_date'])
            end_date = datetime.fromisoformat(period['end_date'])

            # Get all transactions in the period
            transactions = tq(Transaction).filter(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).all()

            # Get all invoices in the period
            invoices = tq(Invoice).filter(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            ).all()

            audit_trail = []

            # Process transactions
            for transaction in transactions:
                audit_trail.append({
                    'date': transaction.transaction_date.strftime('%d-%m-%Y'),
                    'type': 'Transaction',
                    'reference': transaction.transaction_id,
                    'description': transaction.description,
                    'amount': transaction.amount,
                    'category': transaction.category,
                    'created_by': transaction.created_by
                })

            # Process invoices
            for invoice in invoices:
                audit_trail.append({
                    'date': invoice.invoice_date.strftime('%d-%m-%Y'),
                    'type': 'Invoice',
                    'reference': invoice.invoice_number,
                    'description': f'Invoice to customer {invoice.customer_id}',
                    'amount': invoice.total_amount,
                    'category': 'Sales',
                    'created_by': invoice.created_by
                })

            # Sort by date
            audit_trail.sort(key=lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

            report = {
                'report_type': 'Audit Trail Report',
                'period': f"{start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}",
                'generated_on': datetime.utcnow().isoformat(),
                'total_entries': len(audit_trail),
                'audit_trail': audit_trail,
                'summary': {
                    'total_transactions': len(transactions),
                    'total_invoices': len(invoices),
                    'total_value': sum(entry['amount'] for entry in audit_trail)
                }
            }

            return {'success': True, 'report': report}

        except Exception as e:
            return {'success': False, 'error': f'Audit trail report generation failed: {str(e)}'}

    def auto_calculate_tds(self, payment_amount: float, payment_type: str, vendor_type: str) -> Dict:
        """Automatically calculate TDS based on payment type and vendor"""
        try:
            # TDS rates for different payment types
            tds_rates = {
                'contractor_payment': 1.0,    # 1% for contractor payments
                'professional_fees': 10.0,    # 10% for professional services
                'rent_payment': 10.0,          # 10% for rent
                'commission': 5.0,             # 5% for commission
                'transport': 1.0,              # 1% for transport
                'other_services': 2.0          # 2% for other services
            }

            # Get applicable TDS rate
            tds_rate = tds_rates.get(payment_type, 0.0)

            # Calculate TDS amount
            tds_amount = (payment_amount * tds_rate / 100)
            net_payment = payment_amount - tds_amount

            return {
                'success': True,
                'payment_amount': payment_amount,
                'tds_rate': tds_rate,
                'tds_amount': round(tds_amount, 2),
                'net_payment': round(net_payment, 2),
                'payment_type': payment_type,
                'vendor_type': vendor_type
            }

        except Exception as e:
            return {'success': False, 'error': f'TDS calculation failed: {str(e)}'}

    def generate_tds_certificate(self, payment_id: int, quarter: str, year: int) -> Dict:
        """Generate TDS certificate (Form 16A)"""
        try:
            # Mock TDS certificate generation
            certificate = {
                'certificate_number': f"TDS{year}{quarter}{payment_id:06d}",
                'quarter': quarter,
                'year': year,
                'deductee_details': {
                    'name': 'Vendor Name',
                    'pan': 'ABCDE1234F',
                    'address': 'Vendor Address'
                },
                'deductor_details': {
                    'name': 'Rice Mill Management System',
                    'tan': 'MILL123456A',
                    'address': 'Mill Address'
                },
                'payment_details': {
                    'payment_amount': 100000,
                    'tds_rate': 1.0,
                    'tds_amount': 1000,
                    'net_payment': 99000
                },
                'generated_on': datetime.utcnow().isoformat()
            }

            return {'success': True, 'certificate': certificate}

        except Exception as e:
            return {'success': False, 'error': f'TDS certificate generation failed: {str(e)}'}

    def validate_pan(self, pan: str) -> Dict:
        """Validate PAN format"""
        try:
            if not pan or len(pan) != 10:
                return {'valid': False, 'error': 'PAN must be 10 characters long'}

            # PAN format: 5 letters + 4 digits + 1 letter
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'

            if not re.match(pan_pattern, pan):
                return {'valid': False, 'error': 'Invalid PAN format'}

            return {'valid': True, 'pan': pan}

        except Exception as e:
            return {'valid': False, 'error': f'PAN validation failed: {str(e)}'}

    def get_compliance_calendar(self, year: int) -> Dict:
        """Get compliance calendar with due dates"""
        try:
            calendar = {
                'year': year,
                'monthly_deadlines': [],
                'annual_deadlines': [],
                'quarterly_deadlines': []
            }

            # Monthly GST deadlines
            for month in range(1, 13):
                if month == 12:
                    gstr1_due = datetime(year + 1, 1, 11)
                    gstr3b_due = datetime(year + 1, 1, 20)
                else:
                    gstr1_due = datetime(year, month + 1, 11)
                    gstr3b_due = datetime(year, month + 1, 20)

                calendar['monthly_deadlines'].append({
                    'month': f"{month:02d}-{year}",
                    'gstr1_due': gstr1_due.strftime('%d-%m-%Y'),
                    'gstr3b_due': gstr3b_due.strftime('%d-%m-%Y')
                })

            # Annual deadlines
            calendar['annual_deadlines'] = [
                {
                    'deadline': f"31-12-{year + 1}",
                    'description': 'GSTR-9 Annual Return',
                    'type': 'GST'
                },
                {
                    'deadline': f"31-03-{year + 1}",
                    'description': 'Income Tax Return',
                    'type': 'Income Tax'
                },
                {
                    'deadline': f"30-06-{year + 1}",
                    'description': 'TDS Annual Return',
                    'type': 'TDS'
                }
            ]

            # Quarterly deadlines
            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            quarter_months = [6, 9, 12, 3]  # End months for each quarter

            for i, quarter in enumerate(quarters):
                if quarter_months[i] <= 12:
                    due_year = year
                else:
                    due_year = year + 1

                calendar['quarterly_deadlines'].append({
                    'quarter': quarter,
                    'tds_due': f"31-{quarter_months[i]:02d}-{due_year}",
                    'description': f'{quarter} TDS Return'
                })

            return {'success': True, 'calendar': calendar}

        except Exception as e:
            return {'success': False, 'error': f'Calendar generation failed: {str(e)}'}

    def export_gst_data(self, format_type: str, month: int, year: int) -> Dict:
        """Export GST data in various formats"""
        try:
            if format_type == 'json':
                gstr1_data = self.generate_gstr1_report(month, year)
                gstr3b_data = self.generate_gstr3b_report(month, year)

                export_data = {
                    'export_format': 'JSON',
                    'period': f"{month:02d}-{year}",
                    'gstr1': gstr1_data.get('gstr1_report', {}),
                    'gstr3b': gstr3b_data.get('gstr3b_report', {}),
                    'exported_on': datetime.utcnow().isoformat()
                }

                return {'success': True, 'export_data': export_data}

            elif format_type == 'excel':
                # In a real implementation, generate Excel file
                return {
                    'success': True,
                    'file_path': f'/exports/gst_data_{month:02d}_{year}.xlsx',
                    'download_url': f'/api/compliance/download/gst_data_{month:02d}_{year}.xlsx'
                }

            else:
                return {'success': False, 'error': 'Unsupported export format'}

        except Exception as e:
            return {'success': False, 'error': f'Export failed: {str(e)}'}

    def schedule_compliance_reminders(self) -> Dict:
        """Schedule automated compliance reminders"""
        try:
            current_date = datetime.utcnow()
            reminders = []

            # Check upcoming GST filing deadlines
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1

            gstr1_due = datetime(next_year, next_month, 11)
            gstr3b_due = datetime(next_year, next_month, 20)

            days_to_gstr1 = (gstr1_due - current_date).days
            days_to_gstr3b = (gstr3b_due - current_date).days

            if days_to_gstr1 <= 5:
                reminders.append({
                    'type': 'gst_filing',
                    'message': f'GSTR-1 due in {days_to_gstr1} days',
                    'due_date': gstr1_due.strftime('%d-%m-%Y'),
                    'priority': 'high'
                })

            if days_to_gstr3b <= 5:
                reminders.append({
                    'type': 'gst_filing',
                    'message': f'GSTR-3B due in {days_to_gstr3b} days',
                    'due_date': gstr3b_due.strftime('%d-%m-%Y'),
                    'priority': 'high'
                })

            # Check license renewals
            # Mock FSSAI license expiry check
            fssai_expiry = datetime(2024, 12, 31)
            days_to_fssai_expiry = (fssai_expiry - current_date).days

            if days_to_fssai_expiry <= 30:
                reminders.append({
                    'type': 'license_renewal',
                    'message': f'FSSAI license expires in {days_to_fssai_expiry} days',
                    'due_date': fssai_expiry.strftime('%d-%m-%Y'),
                    'priority': 'medium'
                })

            return {
                'success': True,
                'reminders': reminders,
                'reminder_count': len(reminders)
            }

        except Exception as e:
            return {'success': False, 'error': f'Reminder scheduling failed: {str(e)}'}

    def get_tax_summary(self, period: Dict) -> Dict:
        """Get comprehensive tax summary"""
        try:
            start_date = datetime.fromisoformat(period['start_date'])
            end_date = datetime.fromisoformat(period['end_date'])

            # Get all invoices in the period
            invoices = tq(Invoice).filter(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            ).all()

            total_sales = 0
            total_gst = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0

            for invoice in invoices:
                invoice_data = invoice.get_invoice_items()
                if invoice_data and 'totals' in invoice_data:
                    totals = invoice_data['totals']
                    total_sales += totals.get('base_amount', 0)
                    total_gst += totals.get('total_gst', 0)
                    total_cgst += totals.get('total_cgst', 0)
                    total_sgst += totals.get('total_sgst', 0)
                    total_igst += totals.get('total_igst', 0)

            tax_summary = {
                'period': f"{start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}",
                'total_sales': round(total_sales, 2),
                'tax_breakdown': {
                    'total_gst': round(total_gst, 2),
                    'cgst': round(total_cgst, 2),
                    'sgst': round(total_sgst, 2),
                    'igst': round(total_igst, 2)
                },
                'tax_rate_wise': {
                    '0%': {'sales': 0, 'tax': 0},
                    '5%': {'sales': round(total_sales, 2), 'tax': round(total_gst, 2)},
                    '12%': {'sales': 0, 'tax': 0},
                    '18%': {'sales': 0, 'tax': 0},
                    '28%': {'sales': 0, 'tax': 0}
                },
                'effective_tax_rate': round((total_gst / total_sales * 100) if total_sales > 0 else 0, 2),
                'invoice_count': len(invoices)
            }

            return {'success': True, 'tax_summary': tax_summary}

        except Exception as e:
            return {'success': False, 'error': f'Tax summary generation failed: {str(e)}'}

    def reconcile_gst_data(self, month: int, year: int) -> Dict:
        """Reconcile GST data between books and returns"""
        try:
            # Get GSTR-1 data (outward supplies)
            gstr1_data = self.generate_gstr1_report(month, year)

            # Get GSTR-3B data (summary)
            gstr3b_data = self.generate_gstr3b_report(month, year)

            if not gstr1_data['success'] or not gstr3b_data['success']:
                return {'success': False, 'error': 'Failed to get GST data for reconciliation'}

            gstr1_summary = gstr1_data['gstr1_report']['summary']
            gstr3b_summary = gstr3b_data['gstr3b_report']['outward_supplies']

            # Compare values
            reconciliation = {
                'period': f"{month:02d}-{year}",
                'reconciliation_date': datetime.utcnow().isoformat(),
                'comparison': {
                    'taxable_value': {
                        'gstr1': gstr1_summary['total_taxable_value'],
                        'gstr3b': gstr3b_summary['taxable_value'],
                        'difference': gstr1_summary['total_taxable_value'] - gstr3b_summary['taxable_value']
                    },
                    'tax_amount': {
                        'gstr1': gstr1_summary['total_tax_amount'],
                        'gstr3b': gstr3b_summary['total_tax'],
                        'difference': gstr1_summary['total_tax_amount'] - gstr3b_summary['total_tax']
                    }
                },
                'reconciliation_status': 'matched',
                'discrepancies': []
            }

            # Check for discrepancies
            if abs(reconciliation['comparison']['taxable_value']['difference']) > 1:
                reconciliation['reconciliation_status'] = 'discrepancy'
                reconciliation['discrepancies'].append('Taxable value mismatch between GSTR-1 and GSTR-3B')

            if abs(reconciliation['comparison']['tax_amount']['difference']) > 1:
                reconciliation['reconciliation_status'] = 'discrepancy'
                reconciliation['discrepancies'].append('Tax amount mismatch between GSTR-1 and GSTR-3B')

            return {'success': True, 'reconciliation': reconciliation}

        except Exception as e:
            return {'success': False, 'error': f'GST reconciliation failed: {str(e)}'}

    def get_compliance_dashboard_data(self) -> Dict:
        """Get comprehensive compliance dashboard data"""
        try:
            # Get overall compliance status
            compliance_status = self.check_compliance_status()

            # Get upcoming deadlines
            current_date = datetime.utcnow()
            calendar = self.get_compliance_calendar(current_date.year)

            from models.gst_filing import GstFilingRecord
            from models.financial import Invoice
            filings = tq(GstFilingRecord).order_by(GstFilingRecord.recorded_at.desc()).limit(20).all()
            recent_activities = [row.to_dict() for row in filings]
            gst_collected = 0.0
            for invoice in tq(Invoice).all():
                gst_collected += float(getattr(invoice, 'gst_amount', 0) or getattr(invoice, 'tax_amount', 0) or 0)
            metrics = {
                'recorded_checklist_rows': len(filings),
                'total_tax_on_invoices': gst_collected,
                'note': 'Checklist rows are recorded in MillMitra only. They are not GSTN filings.',
            }

            dashboard_data = {
                'compliance_overview': compliance_status.get('compliance_status', {}),
                'upcoming_deadlines': calendar.get('calendar', {}).get('monthly_deadlines', [])[:3],
                'recent_activities': recent_activities,
                'compliance_metrics': metrics,
                'alerts': compliance_status.get('compliance_status', {}).get('alerts', []),
                'quick_actions': [
                    {'action': 'File GSTR-1', 'url': '/compliance/gstr1'},
                    {'action': 'File GSTR-3B', 'url': '/compliance/gstr3b'},
                    {'action': 'Generate Invoice', 'url': '/compliance/invoice'},
                    {'action': 'View Reports', 'url': '/compliance/reports'}
                ]
            }

            return {'success': True, 'dashboard_data': dashboard_data}

        except Exception as e:
            return {'success': False, 'error': f'Dashboard data generation failed: {str(e)}'}

    def automated_compliance_check(self) -> Dict:
        """Run automated compliance checks"""
        try:
            checks_performed = []
            issues_found = []

            # Check GST filing status
            gst_check = self._check_gst_compliance()
            checks_performed.append(gst_check)
            if gst_check['score'] < 100:
                issues_found.extend(gst_check['issues'])

            # Check invoice compliance
            invoice_check = self._check_invoice_compliance()
            checks_performed.append(invoice_check)
            if invoice_check['score'] < 100:
                issues_found.extend(invoice_check['issues'])

            # Check data integrity
            data_check = self._check_data_integrity()
            checks_performed.append(data_check)
            if data_check['score'] < 100:
                issues_found.extend(data_check['issues'])

            overall_score = sum(check['score'] for check in checks_performed) / len(checks_performed)

            return {
                'success': True,
                'check_results': {
                    'overall_score': round(overall_score, 1),
                    'checks_performed': len(checks_performed),
                    'issues_found': len(issues_found),
                    'detailed_checks': checks_performed,
                    'issues': issues_found,
                    'recommendations': self._generate_compliance_recommendations(checks_performed)
                }
            }

        except Exception as e:
            return {'success': False, 'error': f'Automated compliance check failed: {str(e)}'}

    def _check_invoice_compliance(self) -> Dict:
        """Check invoice compliance with GST rules"""
        try:
            # Get recent invoices
            current_date = datetime.utcnow()
            start_date = current_date - timedelta(days=30)

            invoices = tq(Invoice).filter(
                Invoice.invoice_date >= start_date
            ).all()

            score = 100
            issues = []

            for invoice in invoices:
                invoice_data = invoice.get_invoice_items()

                # Check if invoice has GST details
                if not invoice_data or 'totals' not in invoice_data:
                    score -= 5
                    issues.append(f'Invoice {invoice.invoice_number} missing GST details')
                    continue

                # Check if customer GSTIN is present for B2B
                customer = t_get(Customer, invoice.customer_id)
                if customer and hasattr(customer, 'gstin') and customer.gstin:
                    # B2B invoice - check compliance
                    if not invoice_data.get('customer_details', {}).get('gstin'):
                        score -= 3
                        issues.append(f'Invoice {invoice.invoice_number} missing customer GSTIN')

                # Check HSN codes
                items = invoice_data.get('items', [])
                for item in items:
                    if not item.get('hsn_code'):
                        score -= 2
                        issues.append(f'Invoice {invoice.invoice_number} missing HSN code for item')

            return {
                'category': 'Invoice Compliance',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues,
                'invoices_checked': len(invoices)
            }

        except Exception as e:
            return {
                'category': 'Invoice Compliance',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking invoice compliance: {str(e)}']
            }

    def _check_data_integrity(self) -> Dict:
        """Check data integrity for compliance"""
        try:
            score = 100
            issues = []

            # Check for duplicate invoice numbers
            duplicate_invoices = db.session.query(Invoice.invoice_number).group_by(Invoice.invoice_number).having(db.func.count(Invoice.invoice_number) > 1).all()

            if duplicate_invoices:
                score -= 20
                issues.append(f'{len(duplicate_invoices)} duplicate invoice numbers found')

            # Check for missing customer details
            customers_without_details = tq(Customer).filter(
                (Customer.phone == None) | (Customer.email == None)
            ).count()

            if customers_without_details > 0:
                score -= 10
                issues.append(f'{customers_without_details} customers missing contact details')

            # Check for transactions without proper categorization
            uncategorized_transactions = tq(Transaction).filter(
                (Transaction.category == None) | (Transaction.category == '')
            ).count()

            if uncategorized_transactions > 0:
                score -= 15
                issues.append(f'{uncategorized_transactions} transactions without proper categorization')

            return {
                'category': 'Data Integrity',
                'score': max(0, score),
                'status': 'compliant' if score >= 80 else 'non_compliant',
                'issues': issues
            }

        except Exception as e:
            return {
                'category': 'Data Integrity',
                'score': 0,
                'status': 'error',
                'issues': [f'Error checking data integrity: {str(e)}']
            }
