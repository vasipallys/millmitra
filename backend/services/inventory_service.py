from models import PaddyStock, ProductStock, User
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import uuid

class InventoryService:
    
    def get_paddy_stock(self, variety=None, location=None, low_stock=False):
        """Get paddy stock with filtering"""
        
        query = PaddyStock.query
        
        if variety:
            query = query.filter(PaddyStock.variety == variety)
        
        if location:
            query = query.filter(PaddyStock.storage_location == location)
        
        if low_stock:
            # Get reorder rules to determine low stock threshold
            reorder_rules = {rule.item_variety: rule.min_quantity 
                           for rule in ReorderRule.query.filter_by(item_type='paddy').all()}
            
            low_stock_items = []
            for stock in query.all():
                threshold = reorder_rules.get(stock.variety, 100)  # Default threshold
                if stock.quantity <= threshold:
                    low_stock_items.append(stock.to_dict())
            
            return low_stock_items
        
        stocks = query.order_by(PaddyStock.variety, PaddyStock.created_at.desc()).all()
        return [stock.to_dict() for stock in stocks]
    
    def add_paddy_stock(self, user: User, stock_data: dict, quality_assessment: dict):
        """Add new paddy stock"""
        
        stock = PaddyStock(
            variety=stock_data['variety'],
            quantity=stock_data['quantity'],
            unit=stock_data.get('unit', 'kg'),
            purchase_price=stock_data.get('purchase_price'),
            supplier_id=stock_data.get('supplier_id'),
            quality_grade=quality_assessment.get('suggested_grade', stock_data.get('quality_grade', 'A')),
            moisture_content=stock_data.get('moisture_content'),
            harvest_date=datetime.fromisoformat(stock_data['harvest_date']) if stock_data.get('harvest_date') else None,
            expiry_date=datetime.fromisoformat(stock_data['expiry_date']) if stock_data.get('expiry_date') else None,
            storage_location=stock_data.get('storage_location'),
            batch_number=stock_data.get('batch_number', self._generate_batch_number())
        )
        
        # Create stock movement record
        movement = StockMovement(
            movement_type='in',
            reference_type='purchase',
            paddy_stock_id=stock.id,
            quantity=stock_data['quantity'],
            unit_price=stock_data.get('purchase_price'),
            total_value=stock_data['quantity'] * stock_data.get('purchase_price', 0),
            notes=f"Initial stock addition - {stock_data.get('notes', '')}",
            created_by=user.id
        )
        
        db.session.add(stock)
        db.session.add(movement)
        db.session.commit()
        from services.notification_service import paddy_stock_added
        paddy_stock_added(stock)
        
        return stock
    
    def update_paddy_stock(self, stock_id: int, user: User, update_data: dict):
        """Update paddy stock"""
        
        stock = PaddyStock.query.get_or_404(stock_id)
        
        # Track quantity changes
        old_quantity = stock.quantity
        new_quantity = update_data.get('quantity', stock.quantity)
        
        # Update stock fields
        for field in ['variety', 'quantity', 'purchase_price', 'quality_grade', 
                     'moisture_content', 'storage_location']:
            if field in update_data:
                setattr(stock, field, update_data[field])
        
        stock.updated_at = datetime.utcnow()
        
        # Create movement record if quantity changed
        if old_quantity != new_quantity:
            movement_type = 'in' if new_quantity > old_quantity else 'out'
            quantity_diff = abs(new_quantity - old_quantity)
            
            movement = StockMovement(
                movement_type=movement_type,
                reference_type='adjustment',
                paddy_stock_id=stock.id,
                quantity=quantity_diff,
                notes=f"Stock adjustment - {update_data.get('notes', 'Manual update')}",
                created_by=user.id
            )
            db.session.add(movement)
        
        db.session.commit()
        return stock
    
    def get_product_stock(self, product_type=None, grade=None, packaging=None):
        """Get product stock with filtering"""
        
        query = ProductStock.query
        
        if product_type:
            query = query.filter(ProductStock.product_type == product_type)
        
        if grade:
            query = query.filter(ProductStock.grade == grade)
        
        if packaging:
            query = query.filter(ProductStock.packaging_type == packaging)
        
        stocks = query.order_by(ProductStock.product_type, ProductStock.grade).all()
        return [stock.to_dict() for stock in stocks]
    
    def add_product_stock(self, user: User, stock_data: dict, pricing_suggestion: dict):
        """Add new product stock"""
        
        stock = ProductStock(
            product_type=stock_data['product_type'],
            grade=stock_data['grade'],
            quantity=stock_data['quantity'],
            unit=stock_data.get('unit', 'kg'),
            price_per_kg=pricing_suggestion.get('suggested_price', stock_data.get('price_per_kg')),
            packaging_type=stock_data.get('packaging_type', 'bulk'),
            production_date=datetime.fromisoformat(stock_data['production_date']) if stock_data.get('production_date') else None,
            expiry_date=datetime.fromisoformat(stock_data['expiry_date']) if stock_data.get('expiry_date') else None,
            storage_location=stock_data.get('storage_location'),
            quality_score=stock_data.get('quality_score'),
            batch_reference=stock_data.get('batch_reference')
        )
        
        # Create stock movement record
        movement = StockMovement(
            movement_type='in',
            reference_type='production',
            product_stock_id=stock.id,
            quantity=stock_data['quantity'],
            unit_price=stock.price_per_kg,
            total_value=stock_data['quantity'] * (stock.price_per_kg or 0),
            notes=f"Product stock addition - {stock_data.get('notes', '')}",
            created_by=user.id
        )
        
        db.session.add(stock)
        db.session.add(movement)
        db.session.commit()
        
        return stock
    
    def get_stock_movements(self, start_date=None, end_date=None, movement_type=None, page=1, per_page=50):
        """Get stock movements with filtering and pagination"""
        
        query = StockMovement.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(StockMovement.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(StockMovement.created_at <= end_dt)
        
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        
        query = query.order_by(StockMovement.created_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'movements': [movement.to_dict() for movement in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    def create_stock_movement(self, user: User, movement_data: dict):
        """Create a stock movement record"""
        
        movement = StockMovement(
            movement_type=movement_data['movement_type'],
            reference_type=movement_data.get('reference_type'),
            reference_id=movement_data.get('reference_id'),
            paddy_stock_id=movement_data.get('paddy_stock_id'),
            product_stock_id=movement_data.get('product_stock_id'),
            quantity=movement_data['quantity'],
            unit_price=movement_data.get('unit_price'),
            total_value=movement_data.get('total_value'),
            notes=movement_data.get('notes'),
            created_by=user.id
        )
        
        # Update stock quantities
        if movement_data.get('paddy_stock_id'):
            stock = PaddyStock.query.get(movement_data['paddy_stock_id'])
            if movement_data['movement_type'] == 'in':
                stock.quantity += movement_data['quantity']
            else:
                stock.quantity -= movement_data['quantity']
        
        if movement_data.get('product_stock_id'):
            stock = ProductStock.query.get(movement_data['product_stock_id'])
            if movement_data['movement_type'] == 'in':
                stock.quantity += movement_data['quantity']
            else:
                stock.quantity -= movement_data['quantity']
        
        db.session.add(movement)
        db.session.commit()
        
        return movement
    
    def get_inventory_overview(self):
        """Get comprehensive inventory overview"""
        
        # Paddy stock summary
        paddy_summary = db.session.query(
            PaddyStock.variety,
            func.sum(PaddyStock.quantity).label('total_quantity'),
            func.sum(PaddyStock.quantity * PaddyStock.purchase_price).label('total_value'),
            func.count(PaddyStock.id).label('stock_count')
        ).group_by(PaddyStock.variety).all()
        
        # Product stock summary
        product_summary = db.session.query(
            ProductStock.product_type,
            ProductStock.grade,
            func.sum(ProductStock.quantity).label('total_quantity'),
            func.sum(ProductStock.quantity * ProductStock.price_per_kg).label('total_value'),
            func.count(ProductStock.id).label('stock_count')
        ).group_by(ProductStock.product_type, ProductStock.grade).all()
        
        # Recent movements
        recent_movements = StockMovement.query.order_by(
            StockMovement.created_at.desc()
        ).limit(10).all()
        
        return {
            'paddy_summary': [
                {
                    'variety': item.variety,
                    'quantity': float(item.total_quantity or 0),
                    'value': float(item.total_value or 0),
                    'stock_count': item.stock_count
                } for item in paddy_summary
            ],
            'product_summary': [
                {
                    'product_type': item.product_type,
                    'grade': item.grade,
                    'quantity': float(item.total_quantity or 0),
                    'value': float(item.total_value or 0),
                    'stock_count': item.stock_count
                } for item in product_summary
            ],
            'recent_movements': [movement.to_dict() for movement in recent_movements]
        }
    
    def calculate_inventory_turnover(self, days: int):
        """Calculate inventory turnover metrics"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Calculate turnover for each variety
        turnover_data = []
        
        varieties = db.session.query(PaddyStock.variety).distinct().all()
        
        for variety_tuple in varieties:
            variety = variety_tuple[0]
            
            # Average inventory
            avg_inventory = db.session.query(
                func.avg(PaddyStock.quantity)
            ).filter(PaddyStock.variety == variety).scalar() or 0
            
            # Total outbound movements
            total_outbound = db.session.query(
                func.sum(StockMovement.quantity)
            ).join(PaddyStock).filter(
                PaddyStock.variety == variety,
                StockMovement.movement_type == 'out',
                StockMovement.created_at >= start_date
            ).scalar() or 0
            
            turnover_ratio = (total_outbound / avg_inventory) if avg_inventory > 0 else 0
            
            turnover_data.append({
                'variety': variety,
                'avg_inventory': float(avg_inventory),
                'total_outbound': float(total_outbound),
                'turnover_ratio': float(turnover_ratio),
                'days_of_supply': (avg_inventory / (total_outbound / days)) if total_outbound > 0 else float('inf')
            })
        
        return turnover_data
    
    def get_inventory_valuation(self):
        """Get current inventory valuation"""
        
        # Paddy valuation
        paddy_valuation = db.session.query(
            func.sum(PaddyStock.quantity * PaddyStock.purchase_price).label('total_value')
        ).scalar() or 0
        
        # Product valuation
        product_valuation = db.session.query(
            func.sum(ProductStock.quantity * ProductStock.price_per_kg).label('total_value')
        ).scalar() or 0
        
        total_valuation = paddy_valuation + product_valuation
        
        return {
            'paddy_valuation': float(paddy_valuation),
            'product_valuation': float(product_valuation),
            'total_valuation': float(total_valuation),
            'valuation_date': datetime.utcnow().isoformat()
        }
    
    def get_reorder_rules(self):
        """Get all reorder rules"""
        
        rules = ReorderRule.query.filter_by(is_active=True).all()
        return [rule.to_dict() for rule in rules]
    
    def create_reorder_rule(self, rule_data: dict):
        """Create a new reorder rule"""
        
        rule = ReorderRule(
            item_type=rule_data['item_type'],
            item_variety=rule_data['item_variety'],
            min_quantity=rule_data['min_quantity'],
            reorder_quantity=rule_data['reorder_quantity'],
            preferred_supplier_id=rule_data.get('preferred_supplier_id'),
            ai_optimized=rule_data.get('ai_optimized', False)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return rule
    
    def check_reorder_alerts(self):
        """Check for items that need reordering"""
        
        alerts = []
        
        # Check paddy stock
        paddy_rules = ReorderRule.query.filter_by(item_type='paddy', is_active=True).all()
        
        for rule in paddy_rules:
            current_stock = db.session.query(
                func.sum(PaddyStock.quantity)
            ).filter(PaddyStock.variety == rule.item_variety).scalar() or 0
            
            if current_stock <= rule.min_quantity:
                alerts.append({
                    'type': 'paddy',
                    'variety': rule.item_variety,
                    'current_stock': float(current_stock),
                    'min_quantity': rule.min_quantity,
                    'reorder_quantity': rule.reorder_quantity,
                    'preferred_supplier': rule.preferred_supplier.name if rule.preferred_supplier else None,
                    'urgency': 'high' if current_stock <= (rule.min_quantity * 0.5) else 'medium'
                })
        
        # Check product stock
        product_rules = ReorderRule.query.filter_by(item_type='product', is_active=True).all()
        
        for rule in product_rules:
            current_stock = db.session.query(
                func.sum(ProductStock.quantity)
            ).filter(ProductStock.product_type == rule.item_variety).scalar() or 0
            
            if current_stock <= rule.min_quantity:
                alerts.append({
                    'type': 'product',
                    'variety': rule.item_variety,
                    'current_stock': float(current_stock),
                    'min_quantity': rule.min_quantity,
                    'reorder_quantity': rule.reorder_quantity,
                    'urgency': 'high' if current_stock <= (rule.min_quantity * 0.5) else 'medium'
                })
        
        return alerts
    
    def get_suppliers(self):
        """Get all suppliers"""
        
        suppliers = Supplier.query.filter_by(is_active=True).all()
        return [supplier.to_dict() for supplier in suppliers]
    
    def create_supplier(self, supplier_data: dict):
        """Create a new supplier"""
        
        supplier = Supplier(
            name=supplier_data['name'],
            contact_person=supplier_data.get('contact_person'),
            phone=supplier_data.get('phone'),
            email=supplier_data.get('email'),
            address=supplier_data.get('address'),
            payment_terms=supplier_data.get('payment_terms')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return supplier
    
    def generate_stock_aging_report(self):
        """Generate stock aging report"""
        
        current_date = datetime.utcnow().date()
        
        # Paddy aging
        paddy_aging = db.session.query(
            PaddyStock.variety,
            PaddyStock.batch_number,
            PaddyStock.quantity,
            PaddyStock.created_at,
            func.extract('days', current_date - func.date(PaddyStock.created_at)).label('age_days')
        ).all()
        
        # Product aging
        product_aging = db.session.query(
            ProductStock.product_type,
            ProductStock.grade,
            ProductStock.quantity,
            ProductStock.production_date,
            func.extract('days', current_date - ProductStock.production_date).label('age_days')
        ).filter(ProductStock.production_date.isnot(None)).all()
        
        return {
            'paddy_aging': [
                {
                    'variety': item.variety,
                    'batch_number': item.batch_number,
                    'quantity': float(item.quantity),
                    'age_days': int(item.age_days or 0),
                    'age_category': self._get_age_category(int(item.age_days or 0))
                } for item in paddy_aging
            ],
            'product_aging': [
                {
                    'product_type': item.product_type,
                    'grade': item.grade,
                    'quantity': float(item.quantity),
                    'age_days': int(item.age_days or 0),
                    'age_category': self._get_age_category(int(item.age_days or 0))
                } for item in product_aging
            ]
        }
    
    def generate_movement_summary(self, start_date: str, end_date: str):
        """Generate stock movement summary"""
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        summary = db.session.query(
            StockMovement.movement_type,
            StockMovement.reference_type,
            func.count(StockMovement.id).label('count'),
            func.sum(StockMovement.quantity).label('total_quantity'),
            func.sum(StockMovement.total_value).label('total_value')
        ).filter(
            StockMovement.created_at >= start_dt,
            StockMovement.created_at <= end_dt
        ).group_by(
            StockMovement.movement_type,
            StockMovement.reference_type
        ).all()
        
        return [
            {
                'movement_type': item.movement_type,
                'reference_type': item.reference_type,
                'count': item.count,
                'total_quantity': float(item.total_quantity or 0),
                'total_value': float(item.total_value or 0)
            } for item in summary
        ]
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        
        low_stock_items = []
        
        # Get reorder rules
        reorder_rules = {
            f"{rule.item_type}_{rule.item_variety}": rule.min_quantity
            for rule in ReorderRule.query.filter_by(is_active=True).all()
        }
        
        # Check paddy stock
        paddy_stocks = PaddyStock.query.all()
        for stock in paddy_stocks:
            threshold = reorder_rules.get(f"paddy_{stock.variety}", 100)
            if stock.quantity <= threshold:
                low_stock_items.append({
                    'type': 'paddy',
                    'variety': stock.variety,
                    'current_quantity': stock.quantity,
                    'threshold': threshold,
                    'shortage': threshold - stock.quantity,
                    'storage_location': stock.storage_location
                })
        
        # Check product stock
        product_stocks = ProductStock.query.all()
        for stock in product_stocks:
            threshold = reorder_rules.get(f"product_{stock.product_type}", 50)
            if stock.quantity <= threshold:
                low_stock_items.append({
                    'type': 'product',
                    'variety': stock.product_type,
                    'grade': stock.grade,
                    'current_quantity': stock.quantity,
                    'threshold': threshold,
                    'shortage': threshold - stock.quantity,
                    'storage_location': stock.storage_location
                })
        
        return low_stock_items
    
    # Helper methods
    def _generate_batch_number(self):
        """Generate unique batch number"""
        today = datetime.now().strftime('%Y%m%d')
        count = PaddyStock.query.filter(
            func.date(PaddyStock.created_at) == datetime.now().date()
        ).count()
        return f"PS-{today}-{count + 1:03d}"
    
    def _get_age_category(self, age_days: int):
        """Categorize stock by age"""
        if age_days <= 30:
            return 'fresh'
        elif age_days <= 90:
            return 'good'
        elif age_days <= 180:
            return 'aging'
        else:
            return 'old'