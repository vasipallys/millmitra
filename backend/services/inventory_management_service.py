"""
Inventory Management Service
Real implementation for inventory operations
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from models.inventory import PaddyStock, ProcessedStock, StockMovement
from models.farmer import Farmer
from services.notification_service import NotificationService
from extensions import db
import uuid

class InventoryManagementService:
    
    @staticmethod
    def add_paddy_stock(data, created_by=None):
        """Add new paddy stock to inventory"""
        try:
            # Generate unique stock ID
            stock_id = f"PAD{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            # Calculate remaining quantity (initially same as received)
            remaining_quantity = data.get('quantity', 0)
            
            paddy_stock = PaddyStock(
                stock_id=stock_id,
                farmer_id=data.get('farmer_id'),
                purchase_date=datetime.now(),
                variety=data.get('variety'),
                quantity=data.get('quantity'),
                purchase_price=data.get('purchase_price'),
                total_amount=data.get('quantity', 0) * data.get('purchase_price', 0),
                
                # Quality parameters
                moisture_content=data.get('moisture_content'),
                foreign_matter=data.get('foreign_matter'),
                broken_percentage=data.get('broken_percentage'),
                chalky_percentage=data.get('chalky_percentage'),
                grain_length=data.get('grain_length'),
                grain_width=data.get('grain_width'),
                quality_grade=data.get('quality_grade', 'A'),
                
                # Storage
                warehouse_id=data.get('warehouse_id', 'WH001'),
                bin_number=data.get('bin_number'),
                storage_conditions=data.get('storage_conditions'),
                
                remaining_quantity=remaining_quantity,
                created_by=created_by
            )
            
            db.session.add(paddy_stock)
            
            # Create stock movement record
            movement = StockMovement(
                stock_id=paddy_stock.id,
                stock_type='paddy',
                movement_type='inward',
                quantity=data.get('quantity'),
                reference_type='purchase',
                reference_id=data.get('farmer_id'),
                created_by=created_by,
                notes=f"Paddy purchase from farmer - {data.get('variety')}"
            )
            
            db.session.add(movement)
            db.session.commit()
            
            # Check for low stock alerts after adding
            InventoryManagementService._check_stock_levels()
            
            return paddy_stock
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_paddy_stock(filters=None):
        """Get paddy stock with optional filters"""
        query = PaddyStock.query
        
        if filters:
            if filters.get('variety'):
                query = query.filter(PaddyStock.variety == filters['variety'])
            
            if filters.get('status'):
                query = query.filter(PaddyStock.status == filters['status'])
            
            if filters.get('farmer_id'):
                query = query.filter(PaddyStock.farmer_id == filters['farmer_id'])
            
            if filters.get('warehouse_id'):
                query = query.filter(PaddyStock.warehouse_id == filters['warehouse_id'])
            
            if filters.get('min_quantity'):
                query = query.filter(PaddyStock.remaining_quantity >= filters['min_quantity'])
        
        # Join with farmer for farmer details
        query = query.join(Farmer, PaddyStock.farmer_id == Farmer.id)
        
        stocks = query.order_by(PaddyStock.purchase_date.desc()).all()
        
        return stocks
    
    @staticmethod
    def get_stock_summary():
        """Get inventory summary statistics"""
        # Paddy stock summary
        paddy_summary = db.session.query(
            PaddyStock.variety,
            func.sum(PaddyStock.remaining_quantity).label('total_quantity'),
            func.sum(PaddyStock.total_amount).label('total_value'),
            func.count(PaddyStock.id).label('stock_count'),
            func.avg(PaddyStock.purchase_price).label('avg_price')
        ).filter(
            PaddyStock.status.in_(['stored', 'processing']),
            PaddyStock.remaining_quantity > 0
        ).group_by(PaddyStock.variety).all()
        
        # Processed stock summary
        processed_summary = db.session.query(
            ProcessedStock.product_type,
            func.sum(ProcessedStock.quantity).label('total_quantity'),
            func.sum(ProcessedStock.total_value).label('total_value'),
            func.count(ProcessedStock.id).label('stock_count')
        ).filter(
            ProcessedStock.status == 'available',
            ProcessedStock.quantity > 0
        ).group_by(ProcessedStock.product_type).all()
        
        return {
            'paddy_stocks': [
                {
                    'variety': item.variety,
                    'total_quantity': float(item.total_quantity or 0),
                    'total_value': float(item.total_value or 0),
                    'stock_count': item.stock_count,
                    'avg_price': float(item.avg_price or 0)
                } for item in paddy_summary
            ],
            'processed_stocks': [
                {
                    'product_type': item.product_type,
                    'total_quantity': float(item.total_quantity or 0),
                    'total_value': float(item.total_value or 0),
                    'stock_count': item.stock_count
                } for item in processed_summary
            ]
        }
    
    @staticmethod
    def process_paddy_to_rice(paddy_stock_id, processing_data, created_by=None):
        """Convert paddy stock to processed rice"""
        try:
            paddy_stock = PaddyStock.query.get(paddy_stock_id)
            if not paddy_stock:
                raise ValueError("Paddy stock not found")
            
            processing_quantity = processing_data.get('quantity')
            if processing_quantity > paddy_stock.remaining_quantity:
                raise ValueError("Processing quantity exceeds available stock")
            
            # Calculate rice yield (typically 65-70% of paddy)
            yield_percentage = processing_data.get('yield_percentage', 0.67)
            rice_quantity = processing_quantity * yield_percentage
            
            # Create processed stock record
            processed_stock = ProcessedStock(
                source_paddy_id=paddy_stock_id,
                product_type='rice',
                grade=processing_data.get('grade', 'A'),
                quantity=rice_quantity,
                unit='kg',
                processing_date=datetime.now(),
                processing_cost=processing_data.get('processing_cost', 0),
                total_value=rice_quantity * processing_data.get('selling_price', 0),
                selling_price=processing_data.get('selling_price', 0),
                warehouse_id=processing_data.get('warehouse_id', paddy_stock.warehouse_id),
                created_by=created_by
            )
            
            db.session.add(processed_stock)
            
            # Update paddy stock
            paddy_stock.remaining_quantity -= processing_quantity
            paddy_stock.processed_quantity += processing_quantity
            
            if paddy_stock.remaining_quantity <= 0:
                paddy_stock.status = 'processed'
            else:
                paddy_stock.status = 'processing'
            
            # Create movement records
            # Outward movement for paddy
            paddy_movement = StockMovement(
                stock_id=paddy_stock_id,
                stock_type='paddy',
                movement_type='outward',
                quantity=processing_quantity,
                reference_type='processing',
                reference_id=processed_stock.id,
                created_by=created_by,
                notes=f"Paddy processed to rice - Batch {processed_stock.batch_number}"
            )
            
            # Inward movement for processed rice
            rice_movement = StockMovement(
                stock_id=processed_stock.id,
                stock_type='processed',
                movement_type='inward',
                quantity=rice_quantity,
                reference_type='production',
                reference_id=paddy_stock_id,
                created_by=created_by,
                notes=f"Rice produced from paddy - Yield: {yield_percentage*100}%"
            )
            
            db.session.add(paddy_movement)
            db.session.add(rice_movement)
            db.session.commit()
            
            return processed_stock
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_stock_location(stock_id, stock_type, new_location, created_by=None):
        """Move stock to different location"""
        try:
            if stock_type == 'paddy':
                stock = PaddyStock.query.get(stock_id)
                old_location = stock.warehouse_id
                stock.warehouse_id = new_location
            elif stock_type == 'processed':
                stock = ProcessedStock.query.get(stock_id)
                old_location = stock.warehouse_id
                stock.warehouse_id = new_location
            else:
                raise ValueError("Invalid stock type")
            
            if not stock:
                raise ValueError("Stock not found")
            
            # Create movement record
            movement = StockMovement(
                stock_id=stock_id,
                stock_type=stock_type,
                movement_type='transfer',
                quantity=stock.remaining_quantity if stock_type == 'paddy' else stock.quantity,
                reference_type='location_change',
                created_by=created_by,
                notes=f"Location changed from {old_location} to {new_location}"
            )
            
            db.session.add(movement)
            db.session.commit()
            
            return stock
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_stock_movements(stock_id=None, stock_type=None, limit=50):
        """Get stock movement history"""
        query = StockMovement.query
        
        if stock_id:
            query = query.filter(StockMovement.stock_id == stock_id)
        
        if stock_type:
            query = query.filter(StockMovement.stock_type == stock_type)
        
        movements = query.order_by(StockMovement.created_at.desc()).limit(limit).all()
        
        return movements
    
    @staticmethod
    def _check_stock_levels():
        """Check stock levels and create alerts for low stock"""
        # Define minimum thresholds
        MIN_PADDY_THRESHOLD = 500  # kg
        MIN_RICE_THRESHOLD = 200   # kg
        
        # Check paddy stocks
        low_paddy_stocks = db.session.query(
            PaddyStock.variety,
            func.sum(PaddyStock.remaining_quantity).label('total_quantity')
        ).filter(
            PaddyStock.status.in_(['stored', 'processing']),
            PaddyStock.remaining_quantity > 0
        ).group_by(PaddyStock.variety).having(
            func.sum(PaddyStock.remaining_quantity) < MIN_PADDY_THRESHOLD
        ).all()
        
        # Check processed stocks
        low_rice_stocks = db.session.query(
            ProcessedStock.product_type,
            func.sum(ProcessedStock.quantity).label('total_quantity')
        ).filter(
            ProcessedStock.status == 'available',
            ProcessedStock.quantity > 0
        ).group_by(ProcessedStock.product_type).having(
            func.sum(ProcessedStock.quantity) < MIN_RICE_THRESHOLD
        ).all()
        
        # Create notifications for low stocks
        for stock in low_paddy_stocks:
            NotificationService.create_inventory_low_stock_notification({
                'id': None,
                'name': f"Paddy - {stock.variety}",
                'quantity': float(stock.total_quantity),
                'type': 'paddy'
            })
        
        for stock in low_rice_stocks:
            NotificationService.create_inventory_low_stock_notification({
                'id': None,
                'name': f"Rice - {stock.product_type}",
                'quantity': float(stock.total_quantity),
                'type': 'processed'
            })
    
    @staticmethod
    def get_expiring_stocks(days_ahead=30):
        """Get stocks that are approaching expiry or optimal processing date"""
        expiry_date = datetime.now() + timedelta(days=days_ahead)
        
        # Paddy stocks approaching optimal processing date
        expiring_paddy = PaddyStock.query.filter(
            and_(
                PaddyStock.optimal_processing_date.isnot(None),
                PaddyStock.optimal_processing_date <= expiry_date,
                PaddyStock.status.in_(['stored', 'processing']),
                PaddyStock.remaining_quantity > 0
            )
        ).all()
        
        return expiring_paddy
    
    @staticmethod
    def get_quality_degradation_report():
        """Get quality degradation analysis for stored paddy"""
        # Get stocks with quality degradation predictions
        degrading_stocks = PaddyStock.query.filter(
            and_(
                PaddyStock.quality_degradation_rate.isnot(None),
                PaddyStock.quality_degradation_rate > 0.1,  # More than 10% degradation rate
                PaddyStock.status.in_(['stored', 'processing']),
                PaddyStock.remaining_quantity > 0
            )
        ).order_by(PaddyStock.quality_degradation_rate.desc()).all()
        
        return degrading_stocks
    
    @staticmethod
    def calculate_inventory_value():
        """Calculate total inventory value"""
        # Paddy inventory value
        paddy_value = db.session.query(
            func.sum(PaddyStock.remaining_quantity * PaddyStock.purchase_price)
        ).filter(
            PaddyStock.status.in_(['stored', 'processing']),
            PaddyStock.remaining_quantity > 0
        ).scalar() or 0
        
        # Processed inventory value
        processed_value = db.session.query(
            func.sum(ProcessedStock.quantity * ProcessedStock.selling_price)
        ).filter(
            ProcessedStock.status == 'available',
            ProcessedStock.quantity > 0
        ).scalar() or 0
        
        return {
            'paddy_value': float(paddy_value),
            'processed_value': float(processed_value),
            'total_value': float(paddy_value + processed_value)
        }