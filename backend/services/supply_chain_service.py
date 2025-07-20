from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_, or_
from models.supply_chain import Supplier, PurchaseOrder, PurchaseOrderItem, SupplierContract, ProcurementRequest
from models.user import User
from database import db

class SupplyChainService:
    def __init__(self):
        pass
    
    def create_supplier(self, user: User, supplier_data: Dict):
        """Create new supplier"""
        supplier = Supplier(
            supplier_code=self._generate_supplier_code(),
            company_name=supplier_data['company_name'],
            contact_person=supplier_data.get('contact_person'),
            email=supplier_data.get('email'),
            phone=supplier_data.get('phone'),
            address=supplier_data.get('address'),
            city=supplier_data.get('city'),
            state=supplier_data.get('state'),
            country=supplier_data.get('country'),
            postal_code=supplier_data.get('postal_code'),
            tax_id=supplier_data.get('tax_id'),
            payment_terms=supplier_data.get('payment_terms', 'net_30'),
            credit_limit=supplier_data.get('credit_limit', 0.0),
            supplier_type=supplier_data.get('supplier_type', 'raw_material')
        )
        
        db.session.add(supplier)
        db.session.commit()
        return supplier
    
    def create_purchase_order(self, user: User, po_data: Dict, ai_insights: Dict = None):
        """Create new purchase order"""
        po = PurchaseOrder(
            po_number=self._generate_po_number(),
            supplier_id=po_data['supplier_id'],
            order_date=datetime.fromisoformat(po_data['order_date']),
            expected_delivery_date=datetime.fromisoformat(po_data['expected_delivery_date']),
            subtotal=po_data['subtotal'],
            tax_amount=po_data.get('tax_amount', 0.0),
            shipping_cost=po_data.get('shipping_cost', 0.0),
            total_amount=po_data['total_amount'],
            priority=po_data.get('priority', 'normal'),
            notes=po_data.get('notes'),
            reference_number=po_data.get('reference_number'),
            ai_recommendations=ai_insights.get('recommendations') if ai_insights else None,
            risk_assessment=ai_insights.get('risk_assessment') if ai_insights else None,
            created_by=user.id
        )
        
        db.session.add(po)
        db.session.flush()
        
        # Add PO items
        for item_data in po_data.get('items', []):
            item = PurchaseOrderItem(
                po_id=po.id,
                item_name=item_data['item_name'],
                item_code=item_data.get('item_code'),
                description=item_data.get('description'),
                ordered_quantity=item_data['ordered_quantity'],
                unit_of_measure=item_data.get('unit_of_measure'),
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                quality_specs=item_data.get('quality_specs')
            )
            db.session.add(item)
        
        db.session.commit()
        return po
    
    def receive_purchase_order(self, po_id: int, user: User, receipt_data: Dict):
        """Process purchase order receipt"""
        po = PurchaseOrder.query.get_or_404(po_id)
        
        # Update delivery information
        po.actual_delivery_date = datetime.fromisoformat(receipt_data['delivery_date'])
        po.delivery_status = receipt_data.get('delivery_status', 'complete')
        
        # Update received quantities
        for item_receipt in receipt_data.get('items', []):
            item = PurchaseOrderItem.query.get(item_receipt['item_id'])
            if item:
                item.received_quantity = item_receipt['received_quantity']
                item.received_quality = item_receipt.get('quality_assessment')
                item.status = 'received' if item_receipt['received_quantity'] > 0 else 'pending'
        
        # Check if PO is fully received
        all_items_received = all(
            item.received_quantity >= item.ordered_quantity 
            for item in po.po_items
        )
        
        if all_items_received:
            po.status = 'delivered'
            po.delivery_status = 'complete'
        else:
            po.delivery_status = 'partial'
        
        # Update supplier performance
        self._update_supplier_performance(po)
        
        db.session.commit()
        return po
    
    def create_procurement_request(self, user: User, request_data: Dict):
        """Create procurement request"""
        request = ProcurementRequest(
            request_number=self._generate_request_number(),
            requested_by=user.id,
            department=request_data.get('department'),
            item_category=request_data.get('item_category'),
            urgency=request_data.get('urgency', 'normal'),
            required_date=datetime.fromisoformat(request_data['required_date']),
            justification=request_data.get('justification'),
            estimated_cost=request_data.get('estimated_cost')
        )
        
        db.session.add(request)
        db.session.flush()
        
        # Add request items
        for item_data in request_data.get('items', []):
            item = ProcurementRequestItem(
                request_id=request.id,
                item_name=item_data['item_name'],
                description=item_data.get('description'),
                quantity=item_data['quantity'],
                unit_of_measure=item_data.get('unit_of_measure'),
                estimated_unit_price=item_data.get('estimated_unit_price'),
                specifications=item_data.get('specifications')
            )
            db.session.add(item)
        
        db.session.commit()
        return request
    
    def evaluate_supplier_performance(self, supplier_id: int, period_days: int = 90):
        """Evaluate supplier performance over period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get POs for the period
        pos = PurchaseOrder.query.filter(
            and_(
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.order_date.between(start_date, end_date),
                PurchaseOrder.status == 'delivered'
            )
        ).all()
        
        if not pos:
            return None
        
        # Calculate metrics
        total_orders = len(pos)
        on_time_deliveries = sum(1 for po in pos if po.actual_delivery_date <= po.expected_delivery_date)
        
        # Quality score (from received items)
        quality_scores = []
        for po in pos:
            for item in po.po_items:
                if item.received_quality and 'quality_score' in item.received_quality:
                    quality_scores.append(item.received_quality['quality_score'])
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        delivery_performance = (on_time_deliveries / total_orders) * 100
        
        # Update supplier ratings
        supplier = Supplier.query.get(supplier_id)
        supplier.quality_rating = avg_quality / 20  # Convert to 5-point scale
        supplier.delivery_rating = delivery_performance / 20  # Convert to 5-point scale
        supplier.overall_score = (supplier.quality_rating + supplier.delivery_rating) / 2
        
        db.session.commit()
        
        return {
            'total_orders': total_orders,
            'on_time_delivery_rate': delivery_performance,
            'average_quality_score': avg_quality,
            'overall_rating': supplier.overall_score
        }
    
    def get_supplier_recommendations(self, item_category: str, requirements: Dict):
        """Get supplier recommendations for procurement"""
        # Get suppliers for the category
        suppliers = Supplier.query.filter(
            and_(
                Supplier.supplier_type == item_category,
                Supplier.status == 'active'
            )
        ).order_by(Supplier.overall_score.desc()).all()
        
        recommendations = []
        for supplier in suppliers[:5]:  # Top 5 suppliers
            # Calculate suitability score
            suitability_score = self._calculate_supplier_suitability(supplier, requirements)
            
            recommendations.append({
                'supplier_id': supplier.id,
                'company_name': supplier.company_name,
                'overall_score': supplier.overall_score,
                'suitability_score': suitability_score,
                'quality_rating': supplier.quality_rating,
                'delivery_rating': supplier.delivery_rating,
                'is_preferred': supplier.is_preferred
            })
        
        return sorted(recommendations, key=lambda x: x['suitability_score'], reverse=True)
    
    def _generate_supplier_code(self):
        """Generate unique supplier code"""
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier:
            last_num = int(last_supplier.supplier_code[3:])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"SUP{new_num:05d}"
    
    def _generate_po_number(self):
        """Generate unique PO number"""
        today = datetime.now()
        prefix = f"PO{today.strftime('%Y%m')}"
        
        last_po = PurchaseOrder.query.filter(
            PurchaseOrder.po_number.like(f"{prefix}%")
        ).order_by(PurchaseOrder.id.desc()).first()
        
        if last_po:
            last_num = int(last_po.po_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def _generate_request_number(self):
        """Generate unique request number"""
        today = datetime.now()
        prefix = f"PR{today.strftime('%Y%m')}"
        
        last_request = ProcurementRequest.query.filter(
            ProcurementRequest.request_number.like(f"{prefix}%")
        ).order_by(ProcurementRequest.id.desc()).first()
        
        if last_request:
            last_num = int(last_request.request_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def _update_supplier_performance(self, po: PurchaseOrder):
        """Update supplier performance metrics"""
        # This would be called after each delivery
        # Implementation would calculate real-time performance metrics
        pass
    
    def _calculate_supplier_suitability(self, supplier: Supplier, requirements: Dict):
        """Calculate supplier suitability for specific requirements"""
        score = 0
        
        # Base score from overall rating
        score += supplier.overall_score * 20
        
        # Preferred supplier bonus
        if supplier.is_preferred:
            score += 10
        
        # Payment terms compatibility
        if requirements.get('payment_terms') == supplier.payment_terms:
            score += 5
        
        # Credit limit check
        required_amount = requirements.get('estimated_value', 0)
        if supplier.credit_limit >= required_amount:
            score += 10
        
        return min(100, score)