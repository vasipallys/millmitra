from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_
from extensions import db
from models.farmer import Farmer, FarmerContract, PaddyProcurement
from models.user import User
from models.finance import Payment
from models.inventory import PaddyStock

class FarmerService:
    
    def register_farmer(self, user: User, farmer_data: dict, ai_verification: dict = None):
        """Register a new farmer"""
        
        # Generate farmer code
        farmer_code = self._generate_farmer_code(farmer_data['district'])
        
        farmer = Farmer(
            farmer_code=farmer_code,
            name=farmer_data['name'],
            father_name=farmer_data.get('father_name'),
            phone=farmer_data['phone'],
            alternate_phone=farmer_data.get('alternate_phone'),
            email=farmer_data.get('email'),
            aadhar_number=farmer_data.get('aadhar_number'),
            pan_number=farmer_data.get('pan_number'),
            bank_account_number=farmer_data.get('bank_account_number'),
            bank_ifsc=farmer_data.get('bank_ifsc'),
            bank_name=farmer_data.get('bank_name'),
            village=farmer_data['village'],
            district=farmer_data['district'],
            state=farmer_data['state'],
            pincode=farmer_data.get('pincode'),
            total_land_area=farmer_data.get('total_land_area'),
            irrigated_area=farmer_data.get('irrigated_area'),
            farming_experience=farmer_data.get('farming_experience'),
            notes=farmer_data.get('notes'),
            created_by=user.id
        )
        
        # Apply AI verification results
        if ai_verification:
            farmer.verification_status = ai_verification.get('status', 'pending')
            if ai_verification.get('auto_verify', False):
                farmer.kyc_completed = True
        
        db.session.add(farmer)
        db.session.commit()
        
        return farmer
    
    def create_contract(self, user: User, contract_data: dict, ai_optimization: dict = None):
        """Create a farmer contract"""
        
        contract_number = self._generate_contract_number()
        
        # Apply AI price optimization
        base_price = contract_data['base_price']
        if ai_optimization and ai_optimization.get('optimized_price'):
            base_price = ai_optimization['optimized_price']
        
        contract = FarmerContract(
            contract_number=contract_number,
            farmer_id=contract_data['farmer_id'],
            season=contract_data['season'],
            year=contract_data['year'],
            paddy_variety=contract_data['paddy_variety'],
            expected_quantity=contract_data['expected_quantity'],
            base_price=base_price,
            quality_bonus=contract_data.get('quality_bonus', 0),
            advance_amount=contract_data.get('advance_amount', 0),
            contract_date=datetime.strptime(contract_data['contract_date'], '%Y-%m-%d').date(),
            expected_delivery_start=datetime.strptime(contract_data['expected_delivery_start'], '%Y-%m-%d').date() if contract_data.get('expected_delivery_start') else None,
            expected_delivery_end=datetime.strptime(contract_data['expected_delivery_end'], '%Y-%m-%d').date() if contract_data.get('expected_delivery_end') else None,
            terms_conditions=contract_data.get('terms_conditions'),
            special_instructions=contract_data.get('special_instructions'),
            created_by=user.id
        )
        
        db.session.add(contract)
        
        # Create advance payment if specified
        if contract.advance_amount > 0:
            advance_payment = Payment(
                payment_id=self._generate_payment_number(),
                farmer_id=contract.farmer_id,
                payment_type='paid',
                payment_category='farmer_payment',
                amount=contract.advance_amount,
                payment_method=contract_data.get('advance_payment_method', 'bank_transfer'),
                payment_date=contract.contract_date,
                description=f"Advance payment for contract {contract_number}",
                created_by=user.id,
                status='cleared'
            )
            db.session.add(advance_payment)
        
        db.session.commit()
        return contract
    
    def record_procurement(self, user: User, procurement_data: dict, quality_assessment: dict = None):
        """Record paddy procurement"""
        
        procurement_number = self._generate_procurement_number()
        
        # Calculate final price based on quality
        base_price = procurement_data['base_price']
        quality_bonus = 0
        quality_penalty = 0
        
        if quality_assessment:
            quality_bonus = quality_assessment.get('bonus_rate', 0)
            quality_penalty = quality_assessment.get('penalty_rate', 0)
        
        final_price = base_price + quality_bonus - quality_penalty
        total_amount = final_price * procurement_data['quantity']
        
        procurement = PaddyProcurement(
            procurement_number=procurement_number,
            farmer_id=procurement_data['farmer_id'],
            contract_id=procurement_data.get('contract_id'),
            procurement_date=datetime.strptime(procurement_data['procurement_date'], '%Y-%m-%d').date(),
            paddy_variety=procurement_data['paddy_variety'],
            quantity=procurement_data['quantity'],
            moisture_content=procurement_data.get('moisture_content'),
            foreign_matter=procurement_data.get('foreign_matter'),
            broken_grains=procurement_data.get('broken_grains'),
            quality_grade=quality_assessment.get('grade') if quality_assessment else None,
            quality_score=quality_assessment.get('score') if quality_assessment else None,
            quality_bonus_rate=quality_bonus,
            quality_penalty_rate=quality_penalty,
            base_price=base_price,
            final_price=final_price,
            total_amount=total_amount,
            vehicle_number=procurement_data.get('vehicle_number'),
            driver_name=procurement_data.get('driver_name'),
            storage_location=procurement_data.get('storage_location'),
            test_results=quality_assessment.get('test_results') if quality_assessment else None,
            inspector_notes=procurement_data.get('inspector_notes'),
            created_by=user.id
        )
        
        db.session.add(procurement)
        
        # Update contract if linked
        if procurement.contract_id:
            contract = FarmerContract.query.get(procurement.contract_id)
            contract.actual_quantity_delivered += procurement.quantity
        
        # Update farmer's last transaction date and ratings
        farmer = Farmer.query.get(procurement.farmer_id)
        farmer.last_transaction_date = procurement.procurement_date
        
        if quality_assessment and quality_assessment.get('score'):
            # Update farmer's quality rating (weighted average)
            current_rating = farmer.quality_rating or 0
            new_score = quality_assessment['score'] / 20  # Convert 0-100 to 0-5 scale
            farmer.quality_rating = (current_rating * 0.8) + (new_score * 0.2)
        
        db.session.commit()
        return procurement
    
    def process_payment(self, user: User, payment_data: dict, ai_validation: dict = None):
        """Process farmer payment"""
        
        # AI validation check
        if ai_validation and not ai_validation.get('valid', True):
            raise ValueError(f"Payment validation failed: {ai_validation.get('reason')}")
        
        payment_number = self._generate_payment_number()
        
        payment = Payment(
            payment_id=payment_number,
            farmer_id=payment_data['farmer_id'],
            payment_type='paid',
            payment_category='farmer_payment',
            amount=payment_data['amount'],
            payment_method=payment_data['payment_method'],
            payment_date=datetime.strptime(payment_data['payment_date'], '%Y-%m-%d'),
            reference_number=payment_data.get('transaction_reference'),
            description=payment_data.get('description'),
            notes=payment_data.get('notes'),
            created_by=user.id
        )
        
        db.session.add(payment)
        
        # Update procurement payment status if linked
        procurement_id = payment_data.get('procurement_id')
        if procurement_id:
            procurement = PaddyProcurement.query.get(procurement_id)
            total_paid = db.session.query(func.sum(Payment.amount)).filter(
                Payment.payment_category == 'farmer_payment',
                Payment.description.like(f'%procurement {procurement.id}%'),
                Payment.status == 'cleared'
            ).scalar() or 0
            
            total_paid += payment.amount
            
            if total_paid >= procurement.total_amount:
                procurement.payment_status = 'completed'
            else:
                procurement.payment_status = 'partial'
        
        # Update contract payment tracking
        if payment.contract_id:
            contract = FarmerContract.query.get(payment.contract_id)
            contract.total_amount_paid += payment.amount
        
        # Update farmer reliability score
        farmer = Farmer.query.get(payment.farmer_id)
        if payment.payment_type == 'procurement':
            # Positive impact on reliability for timely payments
            farmer.reliability_score = min(5.0, (farmer.reliability_score or 0) + 0.1)
        
        db.session.commit()
        return payment
    
    def get_farmer_dashboard_data(self, farmer_id: int):
        """Get comprehensive farmer dashboard data"""
        
        farmer = Farmer.query.get_or_404(farmer_id)
        
        # Active contracts
        active_contracts = FarmerContract.query.filter(
            FarmerContract.farmer_id == farmer_id,
            FarmerContract.status == 'active'
        ).all()
        
        # Recent procurements
        recent_procurements = PaddyProcurement.query.filter(
            PaddyProcurement.farmer_id == farmer_id
        ).order_by(PaddyProcurement.procurement_date.desc()).limit(10).all()
        
        # Payment summary
        total_payments = db.session.query(func.sum(Payment.amount)).filter(
            Payment.farmer_id == farmer_id,
            Payment.payment_category == 'farmer_payment',
            Payment.status == 'cleared'
        ).scalar() or 0
        
        pending_payments = db.session.query(func.sum(PaddyProcurement.total_amount)).filter(
            PaddyProcurement.farmer_id == farmer_id,
            PaddyProcurement.payment_status.in_(['pending', 'partial'])
        ).scalar() or 0
        
        # Season summary
        current_year = datetime.now().year
        season_summary = db.session.query(
            func.sum(PaddyProcurement.quantity).label('total_quantity'),
            func.avg(PaddyProcurement.quality_score).label('avg_quality'),
            func.sum(PaddyProcurement.total_amount).label('total_value')
        ).filter(
            PaddyProcurement.farmer_id == farmer_id,
            func.extract('year', PaddyProcurement.procurement_date) == current_year
        ).first()
        
        return {
            'farmer': farmer.to_dict(),
            'active_contracts': [contract.to_dict() for contract in active_contracts],
            'recent_procurements': [proc.to_dict() for proc in recent_procurements],
            'payment_summary': {
                'total_payments': float(total_payments),
                'pending_payments': float(pending_payments)
            },
            'season_summary': {
                'total_quantity': float(season_summary.total_quantity or 0),
                'average_quality': float(season_summary.avg_quality or 0),
                'total_value': float(season_summary.total_value or 0)
            }
        }
    
    def get_farmers_list(self, filters: dict = None):
        """Get filtered list of farmers"""
        
        query = Farmer.query
        
        if filters:
            if filters.get('district'):
                query = query.filter(Farmer.district == filters['district'])
            if filters.get('status'):
                query = query.filter(Farmer.status == filters['status'])
            if filters.get('verification_status'):
                query = query.filter(Farmer.verification_status == filters['verification_status'])
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    Farmer.name.ilike(search_term),
                    Farmer.farmer_code.ilike(search_term),
                    Farmer.phone.ilike(search_term)
                ))
        
        farmers = query.order_by(Farmer.created_at.desc()).all()
        return farmers
    
    def _generate_farmer_code(self, district: str):
        """Generate unique farmer code"""
        district_code = district[:3].upper()
        year = datetime.now().year % 100
        
        last_farmer = Farmer.query.filter(
            Farmer.farmer_code.like(f"F{district_code}{year}%")
        ).order_by(Farmer.id.desc()).first()
        
        if last_farmer:
            last_num = int(last_farmer.farmer_code[-4:])
            return f"F{district_code}{year}{last_num + 1:04d}"
        else:
            return f"F{district_code}{year}0001"
    
    def _generate_contract_number(self):
        """Generate unique contract number"""
        today = datetime.now()
        prefix = f"CON-{today.year}{today.month:02d}"
        
        last_contract = FarmerContract.query.filter(
            FarmerContract.contract_number.like(f"{prefix}%")
        ).order_by(FarmerContract.id.desc()).first()
        
        if last_contract:
            last_num = int(last_contract.contract_number.split('-')[-1])
            return f"{prefix}-{last_num + 1:04d}"
        else:
            return f"{prefix}-0001"
    
    def _generate_procurement_number(self):
        """Generate unique procurement number"""
        today = datetime.now()
        prefix = f"PROC-{today.year}{today.month:02d}{today.day:02d}"
        
        last_proc = PaddyProcurement.query.filter(
            PaddyProcurement.procurement_number.like(f"{prefix}%")
        ).order_by(PaddyProcurement.id.desc()).first()
        
        if last_proc:
            last_num = int(last_proc.procurement_number.split('-')[-1])
            return f"{prefix}-{last_num + 1:03d}"
        else:
            return f"{prefix}-001"
    
    def _generate_payment_number(self):
        """Generate unique payment number"""
        today = datetime.now()
        prefix = f"FPAY-{today.year}{today.month:02d}"
        
        last_payment = Payment.query.filter(
            Payment.payment_category == 'farmer_payment',
            Payment.payment_id.like(f"{prefix}%")
        ).order_by(Payment.id.desc()).first()
        
        if last_payment:
            last_num = int(last_payment.payment_id.split('-')[-1])
            return f"{prefix}-{last_num + 1:04d}"
        else:
            return f"{prefix}-0001"