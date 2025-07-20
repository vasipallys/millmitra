from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models.sales import Customer, SalesOrder, SalesOrderItem, Quotation, QuotationItem, SalesLead
from database import db
import uuid

class SalesService:
    
    def generate_customer_code(self):
        """Generate unique customer code"""
        prefix = "CUST"
        count = Customer.query.count() + 1
        return f"{prefix}{count:06d}"
    
    def generate_order_number(self):
        """Generate unique order number"""
        prefix = "SO"
        today = datetime.now().strftime("%y%m%d")
        count = SalesOrder.query.filter(
            func.date(SalesOrder.created_at) == datetime.now().date()
        ).count() + 1
        return f"{prefix}{today}{count:03d}"
    
    def generate_quotation_number(self):
        """Generate unique quotation number"""
        prefix = "QT"
        today = datetime.now().strftime("%y%m%d")
        count = Quotation.query.filter(
            func.date(Quotation.created_at) == datetime.now().date()
        ).count() + 1
        return f"{prefix}{today}{count:03d}"
    
    def generate_lead_number(self):
        """Generate unique lead number"""
        prefix = "LD"
        today = datetime.now().strftime("%y%m%d")
        count = SalesLead.query.filter(
            func.date(SalesLead.created_at) == datetime.now().date()
        ).count() + 1
        return f"{prefix}{today}{count:03d}"
    
    # Customer Management
    def create_customer(self, user, customer_data, ai_analysis=None):
        """Create new customer with AI insights"""
        customer = Customer(
            customer_code=self.generate_customer_code(),
            name=customer_data['name'],
            company_name=customer_data.get('company_name'),
            customer_type=customer_data.get('customer_type', 'retail'),
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            address=customer_data.get('address'),
            city=customer_data.get('city'),
            state=customer_data.get('state'),
            pincode=customer_data.get('pincode'),
            gst_number=customer_data.get('gst_number'),
            pan_number=customer_data.get('pan_number'),
            credit_limit=customer_data.get('credit_limit', 0),
            payment_terms=customer_data.get('payment_terms', 'cash'),
            created_by=user.id
        )
        
        # Apply AI insights
        if ai_analysis:
            customer.customer_score = ai_analysis.get('customer_score')
            customer.risk_rating = ai_analysis.get('risk_rating', 'medium')
            customer.preferred_products = ai_analysis.get('preferred_products', [])
        
        db.session.add(customer)
        db.session.commit()
        
        return customer
    
    def update_customer_metrics(self, customer_id):
        """Update customer metrics based on order history"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return None
        
        orders = SalesOrder.query.filter_by(
            customer_id=customer_id,
            status='completed'
        ).all()
        
        customer.total_orders = len(orders)
        customer.total_value = sum(order.total_amount for order in orders)
        customer.average_order_value = customer.total_value / customer.total_orders if customer.total_orders > 0 else 0
        
        if orders:
            customer.last_order_date = max(order.order_date for order in orders)
        
        db.session.commit()
        return customer
    
    # Sales Order Management
    def create_sales_order(self, user, order_data, ai_insights=None):
        """Create new sales order with AI optimization"""
        order = SalesOrder(
            order_number=self.generate_order_number(),
            customer_id=order_data['customer_id'],
            quotation_id=order_data.get('quotation_id'),
            order_date=datetime.fromisoformat(order_data.get('order_date', datetime.now().isoformat())),
            delivery_date=datetime.fromisoformat(order_data['delivery_date']) if order_data.get('delivery_date') else None,
            order_type=order_data.get('order_type', 'standard'),
            payment_terms=order_data.get('payment_terms'),
            delivery_address=order_data.get('delivery_address'),
            created_by=user.id
        )
        
        # Apply AI insights
        if ai_insights:
            order.fulfillment_prediction = ai_insights.get('fulfillment_prediction')
            order.risk_assessment = ai_insights.get('risk_assessment')
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        subtotal = 0
        for item_data in order_data.get('items', []):
            item = SalesOrderItem(
                order_id=order.id,
                product_name=item_data['product_name'],
                product_variety=item_data.get('product_variety'),
                product_grade=item_data.get('product_grade'),
                quantity=item_data['quantity'],
                unit=item_data.get('unit', 'quintal'),
                unit_price=item_data['unit_price'],
                total_price=item_data['quantity'] * item_data['unit_price']
            )
            subtotal += item.total_price
            db.session.add(item)
        
        # Calculate totals
        order.subtotal = subtotal
        order.tax_amount = order_data.get('tax_amount', subtotal * 0.18)  # Default 18% GST
        order.discount_amount = order_data.get('discount_amount', 0)
        order.total_amount = order.subtotal + order.tax_amount - order.discount_amount
        
        db.session.commit()
        
        # Update customer metrics
        self.update_customer_metrics(order.customer_id)
        
        return order
    
    def update_order_status(self, order_id, status, user):
        """Update order status with validation"""
        order = SalesOrder.query.get(order_id)
        if not order:
            return None
        
        valid_transitions = {
            'draft': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        if status not in valid_transitions.get(order.status, []):
            raise ValueError(f"Invalid status transition from {order.status} to {status}")
        
        order.status = status
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        return order
    
    # Quotation Management
    def create_quotation(self, user, quotation_data, ai_insights=None):
        """Create new quotation with AI pricing"""
        quotation = Quotation(
            quotation_number=self.generate_quotation_number(),
            customer_id=quotation_data['customer_id'],
            quotation_date=datetime.fromisoformat(quotation_data.get('quotation_date', datetime.now().isoformat())),
            valid_until=datetime.fromisoformat(quotation_data['valid_until']) if quotation_data.get('valid_until') else None,
            payment_terms=quotation_data.get('payment_terms'),
            delivery_terms=quotation_data.get('delivery_terms'),
            notes=quotation_data.get('notes'),
            created_by=user.id
        )
        
        # Apply AI insights
        if ai_insights:
            quotation.conversion_probability = ai_insights.get('conversion_probability')
            quotation.competitive_analysis = ai_insights.get('competitive_analysis')
        
        db.session.add(quotation)
        db.session.flush()
        
        # Add quotation items
        subtotal = 0
        for item_data in quotation_data.get('items', []):
            item = QuotationItem(
                quotation_id=quotation.id,
                product_name=item_data['product_name'],
                product_variety=item_data.get('product_variety'),
                product_grade=item_data.get('product_grade'),
                quantity=item_data['quantity'],
                unit=item_data.get('unit', 'quintal'),
                unit_price=item_data['unit_price'],
                total_price=item_data['quantity'] * item_data['unit_price'],
                specifications=item_data.get('specifications'),
                delivery_timeline=item_data.get('delivery_timeline')
            )
            subtotal += item.total_price
            db.session.add(item)
        
        # Calculate totals
        quotation.subtotal = subtotal
        quotation.tax_amount = quotation_data.get('tax_amount', subtotal * 0.18)
        quotation.discount_amount = quotation_data.get('discount_amount', 0)
        quotation.total_amount = quotation.subtotal + quotation.tax_amount - quotation.discount_amount
        
        db.session.commit()
        return quotation
    
    def convert_quotation_to_order(self, quotation_id, user, modifications=None):
        """Convert quotation to sales order"""
        quotation = Quotation.query.get(quotation_id)
        if not quotation:
            return None
        
        if quotation.status != 'accepted':
            raise ValueError("Only accepted quotations can be converted to orders")
        
        # Create order data from quotation
        order_data = {
            'customer_id': quotation.customer_id,
            'quotation_id': quotation.id,
            'order_type': 'standard',
            'payment_terms': quotation.payment_terms,
            'items': []
        }
        
        # Copy items from quotation
        for item in quotation.items:
            order_data['items'].append({
                'product_name': item.product_name,
                'product_variety': item.product_variety,
                'product_grade': item.product_grade,
                'quantity': item.quantity,
                'unit': item.unit,
                'unit_price': item.unit_price
            })
        
        # Apply modifications if any
        if modifications:
            order_data.update(modifications)
        
        return self.create_sales_order(user, order_data)
    
    # Lead Management
    def create_lead(self, user, lead_data, ai_scoring=None):
        """Create new sales lead with AI scoring"""
        lead = SalesLead(
            lead_number=self.generate_lead_number(),
            name=lead_data['name'],
            company_name=lead_data.get('company_name'),
            email=lead_data.get('email'),
            phone=lead_data.get('phone'),
            source=lead_data.get('source'),
            product_interest=lead_data.get('product_interest'),
            estimated_value=lead_data.get('estimated_value'),
            expected_closure_date=datetime.fromisoformat(lead_data['expected_closure_date']) if lead_data.get('expected_closure_date') else None,
            assigned_to=lead_data.get('assigned_to'),
            created_by=user.id
        )
        
        # Apply AI scoring
        if ai_scoring:
            lead.lead_score = ai_scoring.get('lead_score')
            lead.qualification_status = ai_scoring.get('qualification_status')
            lead.next_action = ai_scoring.get('next_action')
        
        db.session.add(lead)
        db.session.commit()
        
        return lead
    
    def update_lead_status(self, lead_id, status, user):
        """Update lead status"""
        lead = SalesLead.query.get(lead_id)
        if not lead:
            return None
        
        lead.status = status
        lead.updated_at = datetime.utcnow()
        
        db.session.commit()
        return lead
    
    # Analytics and Reporting
    def get_sales_dashboard_data(self, days=30):
        """Get sales dashboard analytics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Current period metrics
        current_orders = SalesOrder.query.filter(
            SalesOrder.created_at >= start_date
        ).all()
        
        current_revenue = sum(order.total_amount for order in current_orders if order.status == 'completed')
        current_order_count = len(current_orders)
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_orders = SalesOrder.query.filter(
            and_(SalesOrder.created_at >= prev_start, SalesOrder.created_at < start_date)
        ).all()
        
        prev_revenue = sum(order.total_amount for order in prev_orders if order.status == 'completed')
        prev_order_count = len(prev_orders)
        
        # Calculate growth
        revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        order_growth = ((current_order_count - prev_order_count) / prev_order_count * 100) if prev_order_count > 0 else 0
        
        # Top customers
        top_customers = db.session.query(
            Customer.name,
            func.sum(SalesOrder.total_amount).label('total_value'),
            func.count(SalesOrder.id).label('order_count')
        ).join(SalesOrder).filter(
            SalesOrder.created_at >= start_date,
            SalesOrder.status == 'completed'
        ).group_by(Customer.id).order_by(func.sum(SalesOrder.total_amount).desc()).limit(5).all()
        
        # Sales pipeline
        pipeline_data = db.session.query(
            SalesOrder.status,
            func.count(SalesOrder.id).label('count'),
            func.sum(SalesOrder.total_amount).label('value')
        ).filter(
            SalesOrder.status.in_(['draft', 'confirmed', 'processing'])
        ).group_by(SalesOrder.status).all()
        
        return {
            'current_revenue': current_revenue,
            'revenue_growth': revenue_growth,
            'current_orders': current_order_count,
            'order_growth': order_growth,
            'average_order_value': current_revenue / current_order_count if current_order_count > 0 else 0,
            'top_customers': [
                {
                    'name': customer.name,
                    'total_value': customer.total_value,
                    'order_count': customer.order_count
                } for customer in top_customers
            ],
            'pipeline': [
                {
                    'status': item.status,
                    'count': item.count,
                    'value': item.value
                } for item in pipeline_data
            ]
        }
    
    def get_customer_analytics(self, customer_id):
        """Get detailed customer analytics"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return None
        
        # Order history
        orders = SalesOrder.query.filter_by(customer_id=customer_id).order_by(SalesOrder.order_date.desc()).all()
        
        # Monthly trends
        monthly_data = db.session.query(
            func.date_trunc('month', SalesOrder.order_date).label('month'),
            func.sum(SalesOrder.total_amount).label('revenue'),
            func.count(SalesOrder.id).label('orders')
        ).filter(
            SalesOrder.customer_id == customer_id,
            SalesOrder.status == 'completed'
        ).group_by(func.date_trunc('month', SalesOrder.order_date)).all()
        
        # Product preferences
        product_data = db.session.query(
            SalesOrderItem.product_name,
            func.sum(SalesOrderItem.quantity).label('total_quantity'),
            func.sum(SalesOrderItem.total_price).label('total_value')
        ).join(SalesOrder).filter(
            SalesOrder.customer_id == customer_id,
            SalesOrder.status == 'completed'
        ).group_by(SalesOrderItem.product_name).all()
        
        return {
            'customer': customer.to_dict(),
            'order_history': [order.to_dict() for order in orders],
            'monthly_trends': [
                {
                    'month': item.month.isoformat(),
                    'revenue': item.revenue,
                    'orders': item.orders
                } for item in monthly_data
            ],
            'product_preferences': [
                {
                    'product': item.product_name,
                    'quantity': item.total_quantity,
                    'value': item.total_value
                } for item in product_data
            ]
        }