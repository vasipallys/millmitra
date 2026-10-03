"""Seed and maintain lookup_options. Existing rows are not overwritten."""

from extensions import db
from models.lookup import LookupOption

LOCKED_GROUPS = frozenset(('batch_status', 'stock_type'))

GROUP_KEYS = (
    'product_type',
    'paddy_variety',
    'quality_grade',
    'stock_type',
    'payment_method',
    'customer_type',
    'payment_terms',
    'invoice_payment_terms',
    'invoice_category',
    'season',
    'farming_type',
    'irrigation_type',
    'crop_type',
    'payment_type',
    'farmer_payment_type',
    'order_type',
    'interaction_type',
    'priority',
    'interaction_status',
    'test_type',
    'test_stage',
    'test_method',
    'quality_test_type',
    'equipment',
    'input_source',
    'gst_transaction_type',
    'gst_supply',
    'gst_product_category',
    'report_type',
    'analysis_type',
    'customer_segment',
    'customer_status',
    'order_status',
    'payment_status',
    'batch_status',
    'target_rice_variety',
    'unit',
)


def _row(group, value, label, sort, locked=False):
    return {
        'group_key': group,
        'value': value,
        'label_en': label,
        'label_hi': label,
        'label_te': label,
        'sort_order': sort,
        'is_locked': locked or group in LOCKED_GROUPS,
    }


def seed_definitions():
    catalog = {
        'product_type': [
            ('basmati_rice', 'Basmati Rice'),
            ('jasmine_rice', 'Jasmine Rice'),
            ('long_grain_rice', 'Long Grain Rice'),
            ('short_grain_rice', 'Short Grain Rice'),
            ('white_rice', 'White Rice'),
            ('parboiled_rice', 'Parboiled Rice'),
            ('brown_rice', 'Brown Rice'),
        ],
        'paddy_variety': [
            ('basmati', 'Basmati'),
            ('jasmine', 'Jasmine'),
            ('long_grain', 'Long Grain'),
            ('short_grain', 'Short Grain'),
            ('IR64', 'IR64'),
            ('Swarna', 'Swarna'),
            ('Sona Masuri', 'Sona Masuri'),
            ('Basmati 1121', 'Basmati 1121'),
            ('Pusa Basmati', 'Pusa Basmati'),
            ('brown', 'Brown'),
        ],
        'quality_grade': [
            ('A', 'Grade A'),
            ('B', 'Grade B'),
            ('C', 'Grade C'),
            ('D', 'Grade D'),
        ],
        'stock_type': [
            ('paddy', 'Paddy stock'),
            ('product', 'Product stock'),
        ],
        'payment_method': [
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank transfer'),
            ('upi', 'UPI'),
            ('cheque', 'Cheque'),
            ('card', 'Card'),
            ('online', 'Online'),
        ],
        'customer_type': [
            ('individual', 'Individual'),
            ('business', 'Business'),
            ('distributor', 'Distributor'),
            ('retail', 'Retail'),
            ('wholesale', 'Wholesale'),
            ('export', 'Export'),
        ],
        'payment_terms': [
            ('cash', 'Cash'),
            ('credit_7', '7 days credit'),
            ('credit_15', '15 days credit'),
            ('credit_30', '30 days credit'),
            ('credit_60', '60 days credit'),
            ('immediate', 'Immediate'),
            ('15_days', '15 days'),
            ('30_days', '30 days'),
            ('45_days', '45 days'),
        ],
        'invoice_payment_terms': [
            ('Net 15', 'Net 15'),
            ('Net 30', 'Net 30'),
            ('Net 45', 'Net 45'),
            ('Net 60', 'Net 60'),
            ('Due on Receipt', 'Due on receipt'),
        ],
        'invoice_category': [
            ('raw_rice', 'Raw rice'),
            ('processed_rice', 'Processed rice'),
            ('premium_rice', 'Premium rice'),
            ('broken_rice', 'Broken rice'),
            ('rice_bran', 'Rice bran'),
        ],
        'season': [
            ('kharif', 'Kharif'),
            ('rabi', 'Rabi'),
        ],
        'farming_type': [
            ('organic', 'Organic'),
            ('conventional', 'Conventional'),
            ('mixed', 'Mixed'),
        ],
        'irrigation_type': [
            ('bore_well', 'Bore well'),
            ('canal', 'Canal'),
            ('rain_fed', 'Rain fed'),
            ('mixed', 'Mixed'),
        ],
        'crop_type': [
            ('paddy', 'Paddy'),
            ('wheat', 'Wheat'),
            ('sugarcane', 'Sugarcane'),
            ('cotton', 'Cotton'),
        ],
        'payment_type': [
            ('full', 'Full'),
            ('partial', 'Partial'),
        ],
        'farmer_payment_type': [
            ('procurement', 'Procurement'),
            ('advance', 'Advance'),
            ('bonus', 'Bonus'),
        ],
        'order_type': [
            ('standard', 'Standard'),
            ('urgent', 'Urgent'),
            ('export', 'Export'),
        ],
        'interaction_type': [
            ('call', 'Phone call'),
            ('email', 'Email'),
            ('meeting', 'Meeting'),
            ('complaint', 'Complaint'),
            ('inquiry', 'Inquiry'),
            ('feedback', 'Feedback'),
            ('support', 'Support'),
        ],
        'priority': [
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        'interaction_status': [
            ('open', 'Open'),
            ('in_progress', 'In progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        'test_type': [
            ('input', 'Input'),
            ('intermediate', 'Intermediate'),
            ('final', 'Final'),
        ],
        'test_stage': [
            ('cleaning', 'Cleaning'),
            ('dehusking', 'Dehusking'),
            ('polishing', 'Polishing'),
            ('sorting', 'Sorting'),
            ('packaging', 'Packaging'),
        ],
        'test_method': [
            ('manual', 'Manual'),
            ('automated', 'Automated'),
            ('ai', 'AI'),
        ],
        'quality_test_type': [
            ('comprehensive', 'Comprehensive'),
            ('moisture_only', 'Moisture only'),
            ('physical_properties', 'Physical properties'),
            ('visual_inspection', 'Visual inspection'),
            ('custom', 'Custom'),
        ],
        'equipment': [
            ('moisture_meter_1', 'Moisture meter #1'),
            ('moisture_meter_2', 'Moisture meter #2'),
            ('grain_analyzer', 'Grain analyzer'),
            ('color_sorter', 'Color sorter'),
            ('manual_inspection', 'Manual inspection'),
        ],
        'input_source': [
            ('procurement', 'Fresh procurement'),
            ('inventory', 'Existing stock'),
        ],
        'gst_transaction_type': [
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
        ],
        'gst_supply': [
            ('intra', 'Intra-state (CGST + SGST)'),
            ('inter', 'Inter-state (IGST)'),
        ],
        'gst_product_category': [
            ('paddy', 'Paddy (unprocessed)'),
            ('raw_rice', 'Raw rice'),
            ('processed_rice', 'Processed rice'),
            ('premium_rice', 'Premium rice'),
            ('broken_rice', 'Broken rice'),
            ('rice_bran', 'Rice bran'),
        ],
        'report_type': [
            ('production_summary', 'Production summary'),
            ('financial_performance', 'Financial performance'),
            ('quality_analysis', 'Quality analysis'),
            ('sales_performance', 'Sales performance'),
            ('operational_efficiency', 'Operational efficiency'),
        ],
        'analysis_type': [
            ('production_forecast', 'Production forecast'),
            ('demand_prediction', 'Demand prediction'),
            ('quality_prediction', 'Quality prediction'),
            ('financial_forecast', 'Financial forecast'),
            ('market_analysis', 'Market analysis'),
        ],
        'customer_segment': [
            ('premium', 'Premium'),
            ('regular', 'Regular'),
            ('budget', 'Budget'),
        ],
        'customer_status': [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('blocked', 'Blocked'),
        ],
        'order_status': [
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        'payment_status': [
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('partial', 'Partial'),
        ],
        'batch_status': [
            ('planned', 'Planned'),
            ('in_progress', 'In progress'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
        ],
        'target_rice_variety': [
            ('White Rice', 'White Rice'),
            ('Parboiled Rice', 'Parboiled Rice'),
            ('Brown Rice', 'Brown Rice'),
            ('Basmati Rice', 'Basmati Rice'),
        ],
        'unit': [
            ('kg', 'Kilogram'),
            ('quintal', 'Quintal'),
            ('ton', 'Ton'),
        ],
    }
    rows = []
    for group, items in catalog.items():
        locked = group in LOCKED_GROUPS
        for index, (value, label) in enumerate(items, start=1):
            rows.append(_row(group, value, label, index, locked))
    return rows


def _tenant_id(explicit=None):
    from services.tenant_context import current_tenant_id
    from services.tenant_migration import DEFAULT_SLUG
    if explicit:
        return explicit
    active = current_tenant_id()
    if active:
        return active
    from models.tenant import Tenant
    tenant = Tenant.query.filter_by(slug=DEFAULT_SLUG).first()
    return tenant.id if tenant else None


def ensure_lookup_options(tenant_id=None):
    tid = _tenant_id(tenant_id)
    created = 0
    for item in seed_definitions():
        exists = LookupOption.query.filter_by(
            tenant_id=tid,
            group_key=item['group_key'],
            value=item['value'],
        ).first()
        if exists:
            continue
        db.session.add(LookupOption(
            tenant_id=tid,
            group_key=item['group_key'],
            value=item['value'],
            label_en=item['label_en'],
            label_hi=item['label_hi'],
            label_te=item['label_te'],
            sort_order=item['sort_order'],
            is_active=True,
            is_locked=item['is_locked'],
        ))
        created += 1
    if created:
        db.session.commit()
    return created


def list_active(group_key=None):
    from services.tenant_scope import tq
    query = tq(LookupOption).filter_by(is_active=True)
    if group_key:
        query = query.filter_by(group_key=group_key)
    return query.order_by(
        LookupOption.group_key.asc(),
        LookupOption.sort_order.asc(),
        LookupOption.id.asc(),
    ).all()


def list_admin(group_key=None):
    from services.tenant_scope import tq
    query = tq(LookupOption)
    if group_key:
        query = query.filter_by(group_key=group_key)
    return query.order_by(
        LookupOption.group_key.asc(),
        LookupOption.sort_order.asc(),
        LookupOption.id.asc(),
    ).all()


def group_is_locked(group_key):
    return group_key in LOCKED_GROUPS


def create_option(data):
    group_key = str(data.get('group_key') or '').strip()
    value = str(data.get('value') or '').strip()
    label_en = str(data.get('label_en') or data.get('label') or '').strip()
    if not group_key or not value or not label_en:
        return None, 'group_key, value, and label_en are required'
    if group_is_locked(group_key):
        return None, 'This list is locked. Labels can be edited but values cannot be added.'
    from services.tenant_scope import tq
    if tq(LookupOption).filter_by(group_key=group_key, value=value).first():
        return None, 'That value already exists in this list'
    row = LookupOption(
        group_key=group_key,
        value=value,
        label_en=label_en,
        label_hi=str(data.get('label_hi') or '').strip(),
        label_te=str(data.get('label_te') or '').strip(),
        sort_order=int(data.get('sort_order') or 0),
        is_active=True,
        is_locked=False,
    )
    db.session.add(row)
    db.session.commit()
    return row, None


def update_option(row, data):
    if 'label_en' in data:
        label = str(data.get('label_en') or '').strip()
        if not label:
            return None, 'label_en is required'
        row.label_en = label
    if 'label_hi' in data:
        row.label_hi = str(data.get('label_hi') or '').strip()
    if 'label_te' in data:
        row.label_te = str(data.get('label_te') or '').strip()
    if 'sort_order' in data:
        row.sort_order = int(data.get('sort_order') or 0)
    if 'value' in data and str(data.get('value') or '').strip() != row.value:
        if row.is_locked or group_is_locked(row.group_key):
            return None, 'Locked rows cannot change value'
        new_value = str(data.get('value') or '').strip()
        from services.tenant_scope import tq
        clash = tq(LookupOption).filter_by(group_key=row.group_key, value=new_value).first()
        if clash and clash.id != row.id:
            return None, 'That value already exists in this list'
        row.value = new_value
    db.session.commit()
    return row, None


def set_active(row, active):
    if row.is_locked or group_is_locked(row.group_key):
        return None, 'Locked rows stay active and cannot be deactivated'
    row.is_active = bool(active)
    db.session.commit()
    return row, None
