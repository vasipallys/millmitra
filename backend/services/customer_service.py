from models.sales import Customer
from models.sales import SalesOrder
from models.user import User
from extensions import db
from services.tenant_scope import tq, t_get, t_get_or_404
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import csv
import io
import pandas as pd
from flask import make_response
import json

class CustomerService:
    
    def get_customers(self, page=1, per_page=20, search='', segment='', status='active', sort_by='name'):
        """Get customers with filtering and pagination"""
        query = tq(Customer)
        
        # Apply filters
        if search:
            search_filter = or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.customer_code.ilike(f'%{search}%'),
                Customer.business_name.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if segment:
            # Use customer_type as segment for now since segment field doesn't exist
            query = query.filter(Customer.customer_type == segment)
        
        if status != 'all':
            if status == 'active':
                query = query.filter(Customer.is_active == True)
            elif status == 'inactive':
                query = query.filter(Customer.is_active == False)
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order_by(Customer.name)
        elif sort_by == 'created_at':
            query = query.order_by(Customer.created_at.desc())
        elif sort_by == 'last_order':
            query = query.order_by(Customer.last_order_date.desc().nullslast())
        elif sort_by == 'total_value':
            # This would need a subquery for accurate sorting
            query = query.order_by(Customer.lifetime_value.desc())
        
        # Paginate
        customers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'customers': [customer.to_dict() for customer in customers.items],
            'total': customers.total,
            'pages': customers.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': customers.has_next,
            'has_prev': customers.has_prev
        }
    
    def create_customer(self, user: User, customer_data: dict):
        """Create a new customer"""
        
        customer = Customer(
            name=customer_data['name'],
            business_name=customer_data.get('business_name'),
            contact_person=customer_data.get('contact_person'),
            phone=customer_data['phone'],
            email=customer_data.get('email'),
            address=customer_data.get('address'),
            city=customer_data.get('city'),
            state=customer_data.get('state'),
            pincode=customer_data.get('pincode'),
            business_type=customer_data.get('business_type', 'retailer'),
            segment=customer_data.get('segment', 'regular'),
            credit_limit=customer_data.get('credit_limit', 0),
            payment_terms=customer_data.get('payment_terms', 'cash'),
            gst_number=customer_data.get('gst_number'),
            status='active',
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(customer)
        db.session.commit()
        
        # Create initial interaction
        initial_interaction = CustomerInteraction(
            customer_id=customer.id,
            interaction_type='registration',
            interaction_date=datetime.utcnow(),
            user_id=user.id,
            summary='Customer registered in system',
            notes=f'Customer {customer.name} added to system',
            status='completed'
        )
        
        db.session.add(initial_interaction)
        db.session.commit()
        
        return customer
    
    def update_customer(self, customer: Customer, user: User, update_data: dict):
        """Update customer information"""
        
        # Track changes for audit
        changes = {}
        for key, value in update_data.items():
            if hasattr(customer, key) and getattr(customer, key) != value:
                changes[key] = {
                    'old': getattr(customer, key),
                    'new': value
                }
                setattr(customer, key, value)
        
        customer.updated_by = user.id
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log update interaction
        if changes:
            change_summary = ', '.join([f"{k}: {v['old']} → {v['new']}" for k, v in changes.items()])
            update_interaction = CustomerInteraction(
                customer_id=customer.id,
                interaction_type='update',
                interaction_date=datetime.utcnow(),
                user_id=user.id,
                summary='Customer information updated',
                notes=f'Updated: {change_summary}',
                status='completed'
            )
            
            db.session.add(update_interaction)
            db.session.commit()
        
        return customer
    
    def add_interaction(self, customer: Customer, user: User, interaction_data: dict):
        """Add customer interaction"""
        
        interaction = CustomerInteraction(
            customer_id=customer.id,
            interaction_type=interaction_data['interaction_type'],
            interaction_date=datetime.utcnow(),
            user_id=user.id,
            summary=interaction_data.get('summary'),
            notes=interaction_data.get('notes'),
            status=interaction_data.get('status', 'completed'),
            follow_up_date=datetime.fromisoformat(interaction_data['follow_up_date']) if interaction_data.get('follow_up_date') else None,
            sentiment_score=interaction_data.get('sentiment_score'),
            sentiment_label=interaction_data.get('sentiment_label'),
            themes=json.dumps(interaction_data.get('themes', []))
        )
        
        db.session.add(interaction)
        
        # Update customer last contact date
        customer.last_contact_date = datetime.utcnow()
        
        db.session.commit()
        
        return interaction
    
    def get_customer_orders(self, customer_id: int, page: int = 1, per_page: int = 10):
        """Get customer orders with pagination"""
        orders = tq(SalesOrder).filter_by(customer_id=customer_id)\
                           .order_by(SalesOrder.order_date.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': orders.has_next,
            'has_prev': orders.has_prev
        }
    
    def get_customer_segments(self):
        """Get all customer segments"""
        segments = CustomerSegment.query.all()
        return [segment.to_dict() for segment in segments]
    
    def get_customer_analytics(self, days: int):
        """Get customer analytics for specified period"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic metrics
        total_customers = tq(Customer).filter_by(is_active=True).count()
        new_customers = tq(Customer).filter(
            Customer.created_at >= start_date,
            Customer.is_active == True
        ).count()
        
        # Segment distribution
        segments = db.session.query(
            Customer.customer_type,
            db.func.count(Customer.id).label('count')
        ).filter_by(is_active=True).group_by(Customer.customer_type).all()
        
        segment_distribution = {segment: count for segment, count in segments}
        
        # Interaction metrics
        total_interactions = CustomerInteraction.query.filter(
            CustomerInteraction.interaction_date >= start_date
        ).count()
        
        # Top customers by value
        top_customers = tq(Customer).filter_by(is_active=True).order_by(
            Customer.lifetime_value.desc()
        ).limit(10).all()
        
        # Inactive customers
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        inactive_customers = tq(Customer).filter(
            Customer.last_order_date < thirty_days_ago,
            Customer.is_active == True
        ).count()
        
        return {
            'period_days': days,
            'total_customers': total_customers,
            'new_customers': new_customers,
            'customer_growth_rate': (new_customers / total_customers * 100) if total_customers > 0 else 0,
            'segment_distribution': segment_distribution,
            'total_interactions': total_interactions,
            'avg_interactions_per_customer': total_interactions / total_customers if total_customers > 0 else 0,
            'top_customers': [c.to_dict() for c in top_customers],
            'inactive_customers': inactive_customers,
            'inactive_percentage': (inactive_customers / total_customers * 100) if total_customers > 0 else 0
        }
    
    def create_customer_note(self, customer: Customer, user: User, note_text: str, note_type: str = 'general'):
        """Create a customer note"""
        note = CustomerNote(
            customer_id=customer.id,
            user_id=user.id,
            note=note_text,
            note_type=note_type
        )
        
        db.session.add(note)
        db.session.commit()
        
        return note
    
    def get_acquisition_report(self, start_date: str = None, end_date: str = None):
        """Generate customer acquisition report"""
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        else:
            end_date = datetime.utcnow()
        
        # Daily acquisition data
        daily_acquisitions = db.session.query(
            func.date(Customer.created_at).label('date'),
            func.count(Customer.id).label('count')
        ).filter(
            Customer.created_at >= start_date,
            Customer.created_at <= end_date
        ).group_by(func.date(Customer.created_at)).all()
        
        # Acquisition by source/channel
        acquisition_by_type = db.session.query(
            Customer.business_type,
            func.count(Customer.id).label('count')
        ).filter(
            Customer.created_at >= start_date,
            Customer.created_at <= end_date
        ).group_by(Customer.business_type).all()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'daily_acquisitions': [
                {'date': date.isoformat(), 'count': count}
                for date, count in daily_acquisitions
            ],
            'acquisition_by_type': [
                {'type': btype, 'count': count}
                for btype, count in acquisition_by_type
            ],
            'total_acquired': sum(count for _, count in daily_acquisitions)
        }
    
    def get_retention_report(self, period: str = 'monthly'):
        """Generate customer retention report"""
        # This is a simplified retention calculation
        # In practice, you'd want more sophisticated cohort analysis
        
        if period == 'monthly':
            period_days = 30
        elif period == 'quarterly':
            period_days = 90
        else:
            period_days = 365
        
        current_date = datetime.utcnow()
        period_start = current_date - timedelta(days=period_days)
        
        # Customers who had orders in the period
        active_customers = db.session.query(Customer.id).join(SalesOrder).filter(
            SalesOrder.order_date >= period_start,
            SalesOrder.status != 'cancelled'
        ).distinct().count()
        
        # Total customers at start of period
        total_customers = tq(Customer).filter(
            Customer.created_at < period_start,
            Customer.is_active == True
        ).count()
        
        retention_rate = 0
        if total_customers > 0:
            retention_rate = (active_customers / total_customers) * 100
        
        return {
            'period': period,
            'retention_rate': round(retention_rate, 2),
            'active_customers': active_customers,
            'total_customers': total_customers,
            'period_start': period_start.isoformat(),
            'period_end': current_date.isoformat()
        }
    
    def get_feedback_report(self, days: int):
        """Get customer feedback report"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get feedback data
        feedback_data = CustomerFeedback.query.filter(
            CustomerFeedback.created_at >= start_date
        ).all()
        
        if not feedback_data:
            return {
                'period_days': days,
                'total_feedback': 0,
                'sentiment_distribution': {},
                'themes': [],
                'average_rating': 0
            }
        
        # Sentiment distribution
        sentiment_counts = {}
        total_rating = 0
        rating_count = 0
        themes = []
        
        for feedback in feedback_data:
            sentiment = feedback.sentiment_label or 'neutral'
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            if feedback.rating:
                total_rating += feedback.rating
                rating_count += 1
            
            if feedback.themes:
                themes.extend(json.loads(feedback.themes))
        
        # Count theme frequency
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Top themes
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'period_days': days,
            'total_feedback': len(feedback_data),
            'sentiment_distribution': sentiment_counts,
            'themes': top_themes,
            'average_rating': total_rating / rating_count if rating_count > 0 else 0,
            'feedback_details': [f.to_dict() for f in feedback_data]
        }
    
    def store_feedback(self, feedback_data: dict):
        """Store customer feedback"""
        
        feedback = CustomerFeedback(
            customer_id=feedback_data['customer_id'],
            feedback_text=feedback_data.get('feedback_text'),
            rating=feedback_data.get('rating'),
            category=feedback_data.get('category', 'general'),
            sentiment_score=feedback_data.get('ai_analysis', {}).get('score'),
            sentiment_label=feedback_data.get('ai_analysis', {}).get('label'),
            themes=json.dumps(feedback_data.get('ai_analysis', {}).get('themes', [])),
            ai_analysis=json.dumps(feedback_data.get('ai_analysis', {})),
            created_at=datetime.utcnow()
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return feedback
    
    def bulk_update_customers(self, update_data: dict):
        """Bulk update customers"""
        customer_ids = update_data.get('customer_ids', [])
        updates = update_data.get('updates', {})
        
        if not customer_ids or not updates:
            return {'success': False, 'message': 'Invalid data provided'}
        
        # Update customers
        updated_count = tq(Customer).filter(
            Customer.id.in_(customer_ids)
        ).update(updates, synchronize_session=False)
        
        db.session.commit()
        
        return {
            'success': True,
            'updated_count': updated_count,
            'message': f'Updated {updated_count} customers'
        }
    
    def export_customers(self, format_type: str = 'csv', filters: dict = None):
        """Export customers to CSV/Excel"""
        query = tq(Customer)
        
        # Apply filters if provided
        if filters:
            if filters.get('segment'):
                query = query.filter(Customer.customer_type == filters['segment'])
            if filters.get('status'):
                if filters['status'] == 'active':
                    query = query.filter(Customer.is_active == True)
                elif filters['status'] == 'inactive':
                    query = query.filter(Customer.is_active == False)
        
        customers = query.all()
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Customer Code', 'Name', 'Business Name', 'Phone', 'Email',
                'City', 'State', 'Business Type', 'Segment', 'Status',
                'Credit Limit', 'Total Orders', 'Total Value', 'Created Date'
            ])
            
            # Write data
            for customer in customers:
                writer.writerow([
                    customer.customer_code,
                    customer.name,
                    customer.business_name or '',
                    customer.phone,
                    customer.email or '',
                    customer.city or '',
                    customer.state or '',
                    customer.business_type or '',
                    customer.segment or '',
                    customer.status,
                    customer.credit_limit,
                    customer.orders.count(),
                    customer.get_total_order_value(),
                    customer.created_at.strftime('%Y-%m-%d') if customer.created_at else ''
                ])
            
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
            
            return response
        
        # Add Excel export logic here if needed
        return {'success': False, 'message': 'Format not supported'}
    
    def import_customers(self, user: User, file):
        """Import customers from CSV file"""
        
        try:
            df = pd.read_csv(file)
            imported = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Check if customer already exists
                    existing = tq(Customer).filter_by(phone=row.get('phone')).first()
                    if existing:
                        errors.append(f"Row {index + 1}: Customer with phone {row.get('phone')} already exists")
                        continue
                    
                    customer_data = {
                        'name': row.get('name'),
                        'business_name': row.get('business_name'),
                        'phone': row.get('phone'),
                        'email': row.get('email'),
                        'address': row.get('address'),
                        'city': row.get('city'),
                        'state': row.get('state'),
                        'pincode': row.get('pincode'),
                        'business_type': row.get('business_type', 'retailer'),
                        'segment': row.get('segment', 'regular'),
                        'credit_limit': row.get('credit_limit', 0)
                    }
                    
                    # Validate required fields
                    if not customer_data['name'] or not customer_data['phone']:
                        errors.append(f"Row {index + 1}: Missing required fields (name, phone)")
                        continue
                    
                    self.create_customer(user, customer_data)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            return {
                'imported': imported,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'imported': 0,
                'errors': [f"File processing error: {str(e)}"]
            }
    
    def get_communication_history(self, customer_id: int):
        """Get customer communication history"""
        interactions = CustomerInteraction.query.filter_by(
            customer_id=customer_id
        ).order_by(CustomerInteraction.interaction_date.desc()).all()
        
        return [interaction.to_dict() for interaction in interactions]
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        
        today = datetime.utcnow().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Current month stats
        total_customers = tq(Customer).filter_by(is_active=True).count()
        new_this_month = tq(Customer).filter(
            Customer.created_at >= this_month_start,
            Customer.is_active == True
        ).count()
        
        # Last month for comparison
        new_last_month = tq(Customer).filter(
            Customer.created_at >= last_month_start,
            Customer.created_at < this_month_start,
            Customer.is_active == True
        ).count()
        
        # Interactions this month
        interactions_this_month = CustomerInteraction.query.filter(
            CustomerInteraction.interaction_date >= this_month_start
        ).count()
        
        # Pending follow-ups
        pending_followups = CustomerInteraction.query.filter(
            CustomerInteraction.follow_up_date <= datetime.utcnow(),
            CustomerInteraction.status == 'pending'
        ).count()
        
        # High-value customers
        high_value_customers = tq(Customer).filter(
            Customer.lifetime_value > 100000,
            Customer.is_active == True
        ).count()
        
        # Inactive customers (no orders in 60 days)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        inactive_customers = tq(Customer).filter(
            Customer.last_order_date < sixty_days_ago,
            Customer.is_active == True
        ).count()
        
        return {
            'total_customers': total_customers,
            'new_this_month': new_this_month,
            'new_last_month': new_last_month,
            'growth_rate': ((new_this_month - new_last_month) / new_last_month * 100) if new_last_month > 0 else 0,
            'interactions_this_month': interactions_this_month,
            'pending_followups': pending_followups,
            'high_value_customers': high_value_customers,
            'inactive_customers': inactive_customers
        }

