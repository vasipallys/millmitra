from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSON

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100))
    phone = db.Column(db.String(15), nullable=False)
    alternate_phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    aadhar_number = db.Column(db.String(12), unique=True)
    pan_number = db.Column(db.String(10))
    bank_account_number = db.Column(db.String(20))
    bank_ifsc = db.Column(db.String(11))
    bank_name = db.Column(db.String(100))
    
    # Address
    village = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6))
    
    # Farm details
    total_land_area = db.Column(db.Numeric(10, 2))  # in acres
    irrigated_area = db.Column(db.Numeric(10, 2))
    farming_experience = db.Column(db.Integer)  # years
    primary_crop = db.Column(db.String(50), default='paddy')
    
    # Status and verification
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    kyc_completed = db.Column(db.Boolean, default=False)
    
    # Ratings and scores
    quality_rating = db.Column(db.Numeric(3, 2), default=0.0)  # 0-5 scale
    reliability_score = db.Column(db.Numeric(3, 2), default=0.0)  # 0-5 scale
    payment_score = db.Column(db.Numeric(3, 2), default=0.0)  # 0-5 scale
    
    # Metadata
    registration_date = db.Column(db.Date, default=datetime.utcnow().date)
    last_transaction_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contracts = db.relationship('FarmerContract', backref='farmer', lazy='dynamic')
    procurements = db.relationship('PaddyProcurement', backref='farmer', lazy='dynamic')
    payments = db.relationship('FarmerPayment', backref='farmer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_code': self.farmer_code,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'village': self.village,
            'district': self.district,
            'state': self.state,
            'total_land_area': float(self.total_land_area) if self.total_land_area else None,
            'status': self.status,
            'verification_status': self.verification_status,
            'quality_rating': float(self.quality_rating),
            'reliability_score': float(self.reliability_score),
            'registration_date': self.registration_date.isoformat() if self.registration_date else None
        }

class FarmerContract(db.Model):
    __tablename__ = 'farmer_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)  # kharif, rabi
    year = db.Column(db.Integer, nullable=False)
    
    # Contract terms
    paddy_variety = db.Column(db.String(50), nullable=False)
    expected_quantity = db.Column(db.Numeric(10, 2), nullable=False)  # in quintals
    base_price = db.Column(db.Numeric(10, 2), nullable=False)  # per quintal
    quality_bonus = db.Column(db.Numeric(10, 2), default=0)  # bonus per quintal for quality
    advance_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Dates
    contract_date = db.Column(db.Date, nullable=False)
    expected_delivery_start = db.Column(db.Date)
    expected_delivery_end = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    actual_quantity_delivered = db.Column(db.Numeric(10, 2), default=0)
    total_amount_paid = db.Column(db.Numeric(15, 2), default=0)
    
    # Terms and conditions
    terms_conditions = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'farmer_id': self.farmer_id,
            'season': self.season,
            'year': self.year,
            'paddy_variety': self.paddy_variety,
            'expected_quantity': float(self.expected_quantity),
            'base_price': float(self.base_price),
            'status': self.status,
            'contract_date': self.contract_date.isoformat(),
            'actual_quantity_delivered': float(self.actual_quantity_delivered)
        }

class PaddyProcurement(db.Model):
    __tablename__ = 'paddy_procurements'
    
    id = db.Column(db.Integer, primary_key=True)
    procurement_number = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('farmer_contracts.id'))
    
    # Procurement details
    procurement_date = db.Column(db.Date, nullable=False)
    paddy_variety = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)  # in quintals
    moisture_content = db.Column(db.Numeric(5, 2))  # percentage
    foreign_matter = db.Column(db.Numeric(5, 2))  # percentage
    broken_grains = db.Column(db.Numeric(5, 2))  # percentage
    
    # Quality assessment
    quality_grade = db.Column(db.String(10))  # A, B, C, D
    quality_score = db.Column(db.Numeric(5, 2))  # 0-100
    quality_bonus_rate = db.Column(db.Numeric(10, 2), default=0)
    quality_penalty_rate = db.Column(db.Numeric(10, 2), default=0)
    
    # Pricing
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    final_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Storage and logistics
    vehicle_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    storage_location = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='received')  # received, quality_tested, stored, processed
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, completed
    
    # Quality test results
    test_results = db.Column(JSON)
    inspector_notes = db.Column(db.Text)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = db.relationship('FarmerContract', backref='procurements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'procurement_number': self.procurement_number,
            'farmer_id': self.farmer_id,
            'procurement_date': self.procurement_date.isoformat(),
            'paddy_variety': self.paddy_variety,
            'quantity': float(self.quantity),
            'quality_grade': self.quality_grade,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'final_price': float(self.final_price),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_status': self.payment_status
        }

class FarmerPayment(db.Model):
    __tablename__ = 'farmer_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    procurement_id = db.Column(db.Integer, db.ForeignKey('paddy_procurements.id'))
    contract_id = db.Column(db.Integer, db.ForeignKey('farmer_contracts.id'))
    
    # Payment details
    payment_type = db.Column(db.String(20), nullable=False)  # advance, procurement, bonus, final
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # bank_transfer, cash, cheque
    payment_date = db.Column(db.Date, nullable=False)
    
    # Bank details
    transaction_reference = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(20))
    bank_ifsc = db.Column(db.String(11))
    
    # Status
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    
    # Additional info
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    procurement = db.relationship('PaddyProcurement', backref='payments')
    contract = db.relationship('FarmerContract', backref='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'farmer_id': self.farmer_id,
            'payment_type': self.payment_type,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat(),
            'status': self.status,
            'description': self.description
        }

class FarmerDocument(db.Model):
    __tablename__ = 'farmer_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # aadhar, pan, bank_passbook, land_record
    document_number = db.Column(db.String(100))
    file_path = db.Column(db.String(500))
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    farmer = db.relationship('Farmer', backref='documents')