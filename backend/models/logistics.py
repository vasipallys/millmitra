from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # truck, van, pickup
    make_model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    
    # Capacity and specifications
    load_capacity = db.Column(db.Float)  # in tons
    fuel_type = db.Column(db.String(20))  # diesel, petrol, electric
    fuel_efficiency = db.Column(db.Float)  # km per liter
    
    # Ownership
    ownership_type = db.Column(db.String(20), default='owned')  # owned, leased, contracted
    owner_details = db.Column(JSON)
    
    # Status and maintenance
    status = db.Column(db.String(20), default='available')  # available, in_transit, maintenance, retired
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    maintenance_notes = db.Column(db.Text)
    
    # Insurance and documents
    insurance_expiry = db.Column(db.DateTime)
    registration_expiry = db.Column(db.DateTime)
    permit_details = db.Column(JSON)
    
    # GPS and tracking
    gps_device_id = db.Column(db.String(50))
    current_location = db.Column(JSON)  # lat, lng
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shipments = relationship("Shipment", back_populates="vehicle")
    maintenance_records = relationship("VehicleMaintenance", back_populates="vehicle")

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # License details
    license_type = db.Column(db.String(20))  # LMV, HMV, etc.
    license_expiry = db.Column(db.DateTime)
    
    # Employment
    employment_type = db.Column(db.String(20), default='permanent')  # permanent, contract, freelance
    hire_date = db.Column(db.DateTime)
    salary = db.Column(db.Float)
    
    # Performance and ratings
    rating = db.Column(db.Float, default=5.0)
    total_trips = db.Column(db.Integer, default=0)
    total_distance = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.String(20), default='available')  # available, on_trip, off_duty, suspended
    current_location = db.Column(JSON)
    
    # Documents
    documents = db.Column(JSON)  # List of document URLs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shipments = relationship("Shipment", back_populates="driver")

class Shipment(db.Model):
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_number = db.Column(db.String(50), unique=True, nullable=False)
    shipment_type = db.Column(db.String(20), nullable=False)  # delivery, pickup, transfer
    
    # Origin and destination
    origin_address = db.Column(db.Text, nullable=False)
    origin_coordinates = db.Column(JSON)
    destination_address = db.Column(db.Text, nullable=False)
    destination_coordinates = db.Column(JSON)
    
    # Cargo details
    cargo_description = db.Column(db.Text)
    total_weight = db.Column(db.Float)
    total_volume = db.Column(db.Float)
    package_count = db.Column(db.Integer)
    cargo_value = db.Column(db.Float)
    
    # Scheduling
    scheduled_pickup = db.Column(db.DateTime)
    scheduled_delivery = db.Column(db.DateTime)
    actual_pickup = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    
    # Assignment
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    
    # Route and tracking
    planned_route = db.Column(JSON)
    actual_route = db.Column(JSON)
    distance_planned = db.Column(db.Float)
    distance_actual = db.Column(db.Float)
    
    # Status and progress
    status = db.Column(db.String(20), default='planned')  # planned, assigned, in_transit, delivered, cancelled
    progress_percentage = db.Column(db.Float, default=0)
    current_location = db.Column(JSON)
    
    # Costs and billing
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    fuel_cost = db.Column(db.Float)
    driver_payment = db.Column(db.Float)
    
    # Customer information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer_contact = db.Column(JSON)
    
    # Special instructions
    special_instructions = db.Column(db.Text)
    handling_requirements = db.Column(JSON)
    
    # Documentation
    documents = db.Column(JSON)  # Delivery receipts, photos, etc.
    
    # AI insights
    route_optimization = db.Column(JSON)
    delivery_prediction = db.Column(JSON)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="shipments")
    driver = relationship("Driver", back_populates="shipments")
    customer = relationship("Customer")
    created_by_user = relationship("User")
    tracking_updates = relationship("ShipmentTracking", back_populates="shipment")
    items = relationship("ShipmentItem", back_populates="shipment")

class ShipmentItem(db.Model):
    __tablename__ = 'shipment_items'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    # Item details
    item_description = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(50))  # paddy, rice, byproduct
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    weight = db.Column(db.Float)
    dimensions = db.Column(JSON)  # length, width, height
    
    # Packaging
    packaging_type = db.Column(db.String(50))  # bag, box, bulk
    package_count = db.Column(db.Integer)
    
    # Value and insurance
    unit_value = db.Column(db.Float)
    total_value = db.Column(db.Float)
    is_insured = db.Column(db.Boolean, default=False)
    
    # Special handling
    is_fragile = db.Column(db.Boolean, default=False)
    temperature_controlled = db.Column(db.Boolean, default=False)
    special_instructions = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, loaded, in_transit, delivered
    
    # Relationships
    shipment = relationship("Shipment", back_populates="items")

class ShipmentTracking(db.Model):
    __tablename__ = 'shipment_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    # Location and time
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(JSON)  # lat, lng, address
    
    # Status update
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    # Additional data
    speed = db.Column(db.Float)  # km/h
    fuel_level = db.Column(db.Float)  # percentage
    temperature = db.Column(db.Float)  # for temperature-controlled cargo
    
    # Source of update
    update_source = db.Column(db.String(20), default='gps')  # gps, manual, driver, customer
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    shipment = relationship("Shipment", back_populates="tracking_updates")
    updated_by_user = relationship("User")

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    route_code = db.Column(db.String(20), unique=True)
    
    # Route details
    start_location = db.Column(db.Text, nullable=False)
    end_location = db.Column(db.Text, nullable=False)
    waypoints = db.Column(JSON)  # List of intermediate stops
    
    # Distance and time
    total_distance = db.Column(db.Float)  # km
    estimated_time = db.Column(db.Integer)  # minutes
    
    # Route optimization
    optimized_path = db.Column(JSON)
    traffic_patterns = db.Column(JSON)
    
    # Usage statistics
    usage_count = db.Column(db.Integer, default=0)
    average_time = db.Column(db.Float)
    success_rate = db.Column(db.Float, default=100.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VehicleMaintenance(db.Model):
    __tablename__ = 'vehicle_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    
    # Maintenance details
    maintenance_type = db.Column(db.String(50), nullable=False)  # routine, repair, inspection
    description = db.Column(db.Text, nullable=False)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime)
    actual_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # hours
    
    # Service provider
    service_provider = db.Column(db.String(100))
    mechanic_name = db.Column(db.String(100))
    
    # Costs
    labor_cost = db.Column(db.Float)
    parts_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    # Parts and services
    parts_replaced = db.Column(JSON)
    services_performed = db.Column(JSON)
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # Next maintenance
    next_maintenance_km = db.Column(db.Float)
    next_maintenance_date = db.Column(db.DateTime)
    
    # Documentation
    invoice_number = db.Column(db.String(50))
    documents = db.Column(JSON)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    created_by_user = relationship("User")