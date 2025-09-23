from datetime import datetime, timedelta
from typing import Dict, List
from models.logistics import Vehicle, Driver, Shipment, ShipmentItem, ShipmentTracking, Route
from models.user import User
from extensions import db
import uuid

class LogisticsService:
    def __init__(self):
        pass
    
    def create_shipment(self, user: User, shipment_data: Dict):
        """Create new shipment"""
        shipment_number = f"SH{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        shipment = Shipment(
            shipment_number=shipment_number,
            shipment_type=shipment_data['shipment_type'],
            origin_address=shipment_data['origin_address'],
            origin_coordinates=shipment_data.get('origin_coordinates'),
            destination_address=shipment_data['destination_address'],
            destination_coordinates=shipment_data.get('destination_coordinates'),
            cargo_description=shipment_data.get('cargo_description'),
            total_weight=shipment_data.get('total_weight'),
            total_volume=shipment_data.get('total_volume'),
            package_count=shipment_data.get('package_count'),
            cargo_value=shipment_data.get('cargo_value'),
            scheduled_pickup=datetime.fromisoformat(shipment_data['scheduled_pickup']),
            scheduled_delivery=datetime.fromisoformat(shipment_data['scheduled_delivery']),
            customer_id=shipment_data.get('customer_id'),
            customer_contact=shipment_data.get('customer_contact'),
            special_instructions=shipment_data.get('special_instructions'),
            handling_requirements=shipment_data.get('handling_requirements', {}),
            created_by=user.id
        )
        
        db.session.add(shipment)
        db.session.flush()
        
        # Add shipment items
        for item_data in shipment_data.get('items', []):
            item = ShipmentItem(
                shipment_id=shipment.id,
                item_description=item_data['item_description'],
                item_type=item_data.get('item_type'),
                quantity=item_data['quantity'],
                unit=item_data.get('unit', 'kg'),
                weight=item_data.get('weight'),
                dimensions=item_data.get('dimensions'),
                packaging_type=item_data.get('packaging_type'),
                package_count=item_data.get('package_count'),
                unit_value=item_data.get('unit_value'),
                total_value=item_data.get('total_value'),
                is_fragile=item_data.get('is_fragile', False),
                temperature_controlled=item_data.get('temperature_controlled', False),
                special_instructions=item_data.get('special_instructions')
            )
            db.session.add(item)
        
        # Calculate estimated cost
        shipment.estimated_cost = self._calculate_shipping_cost(shipment)
        
        db.session.commit()
        return shipment
    
    def assign_vehicle_and_driver(self, shipment_id: int, vehicle_id: int, driver_id: int, user: User):
        """Assign vehicle and driver to shipment"""
        shipment = Shipment.query.get_or_404(shipment_id)
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        driver = Driver.query.get_or_404(driver_id)
        
        # Check availability
        if vehicle.status != 'available':
            raise ValueError("Vehicle is not available")
        
        if driver.status != 'available':
            raise ValueError("Driver is not available")
        
        # Check capacity
        if shipment.total_weight and vehicle.load_capacity:
            if shipment.total_weight > vehicle.load_capacity:
                raise ValueError("Shipment weight exceeds vehicle capacity")
        
        # Assign
        shipment.vehicle_id = vehicle_id
        shipment.driver_id = driver_id
        shipment.status = 'assigned'
        
        # Update vehicle and driver status
        vehicle.status = 'assigned'
        driver.status = 'assigned'
        
        # Create tracking entry
        self._create_tracking_update(
            shipment, 
            'assigned', 
            f"Assigned to vehicle {vehicle.vehicle_number} and driver {driver.driver_name}",
            user
        )
        
        db.session.commit()
        return shipment
    
    def start_shipment(self, shipment_id: int, user: User):
        """Start shipment journey"""
        shipment = Shipment.query.get_or_404(shipment_id)
        
        if shipment.status != 'assigned':
            raise ValueError("Shipment must be assigned before starting")
        
        shipment.status = 'in_transit'
        shipment.actual_pickup = datetime.utcnow()
        
        # Update vehicle status
        if shipment.vehicle:
            shipment.vehicle.status = 'in_transit'
        
        # Update driver status
        if shipment.driver:
            shipment.driver.status = 'on_trip'
        
        # Create tracking entry
        self._create_tracking_update(
            shipment,
            'pickup_completed',
            'Shipment picked up and journey started',
            user
        )
        
        db.session.commit()
        return shipment
    
    def complete_delivery(self, shipment_id: int, delivery_data: Dict, user: User):
        """Complete shipment delivery"""
        shipment = Shipment.query.get_or_404(shipment_id)
        
        if shipment.status != 'in_transit':
            raise ValueError("Shipment must be in transit to complete delivery")
        
        shipment.status = 'delivered'
        shipment.actual_delivery = datetime.utcnow()
        shipment.progress_percentage = 100
        
        # Update delivery details
        if delivery_data.get('actual_distance'):
            shipment.distance_actual = delivery_data['actual_distance']
        
        if delivery_data.get('fuel_cost'):
            shipment.fuel_cost = delivery_data['fuel_cost']
        
        # Store delivery documents
        if delivery_data.get('documents'):
            shipment.documents = delivery_data['documents']
        
        # Update vehicle and driver status
        if shipment.vehicle:
            shipment.vehicle.status = 'available'
        
        if shipment.driver:
            shipment.driver.status = 'available'
            shipment.driver.total_trips += 1
            if shipment.distance_actual:
                shipment.driver.total_distance += shipment.distance_actual
        
        # Create final tracking entry
        self._create_tracking_update(
            shipment,
            'delivered',
            'Shipment delivered successfully',
            user
        )
        
        # Calculate actual cost
        shipment.actual_cost = self._calculate_actual_cost(shipment)
        
        db.session.commit()
        return shipment
    
    def track_shipment(self, shipment_number: str):
        """Get shipment tracking information"""
        shipment = Shipment.query.filter_by(shipment_number=shipment_number).first_or_404()
        
        tracking_updates = ShipmentTracking.query.filter_by(
            shipment_id=shipment.id
        ).order_by(ShipmentTracking.timestamp.desc()).all()
        
        return {
            'shipment': {
                'id': shipment.id,
                'shipment_number': shipment.shipment_number,
                'status': shipment.status,
                'progress_percentage': shipment.progress_percentage,
                'origin': shipment.origin_address,
                'destination': shipment.destination_address,
                'scheduled_pickup': shipment.scheduled_pickup.isoformat() if shipment.scheduled_pickup else None,
                'scheduled_delivery': shipment.scheduled_delivery.isoformat() if shipment.scheduled_delivery else None,
                'actual_pickup': shipment.actual_pickup.isoformat() if shipment.actual_pickup else None,
                'actual_delivery': shipment.actual_delivery.isoformat() if shipment.actual_delivery else None,
                'current_location': shipment.current_location
            },
            'vehicle': {
                'vehicle_number': shipment.vehicle.vehicle_number,
                'vehicle_type': shipment.vehicle.vehicle_type
            } if shipment.vehicle else None,
            'driver': {
                'name': shipment.driver.driver_name,
                'phone': shipment.driver.phone
            } if shipment.driver else None,
            'tracking_updates': [
                {
                    'timestamp': update.timestamp.isoformat(),
                    'status': update.status,
                    'description': update.description,
                    'location': update.location
                }
                for update in tracking_updates
            ]
        }
    
    def optimize_route(self, shipment_id: int):
        """Optimize route for shipment"""
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # This would integrate with mapping services like Google Maps API
        # For now, return a basic optimization
        optimized_route = {
            'waypoints': [
                shipment.origin_coordinates,
                shipment.destination_coordinates
            ],
            'total_distance': self._calculate_distance(
                shipment.origin_coordinates,
                shipment.destination_coordinates
            ),
            'estimated_time': 120,  # minutes
            'fuel_estimate': 15.5,  # liters
            'toll_estimate': 200    # rupees
        }
        
        shipment.route_optimization = optimized_route
        shipment.distance_planned = optimized_route['total_distance']
        
        db.session.commit()
        return optimized_route
    
    def get_fleet_status(self):
        """Get current fleet status"""
        vehicles = Vehicle.query.all()
        drivers = Driver.query.all()
        
        vehicle_status = {}
        for status in ['available', 'in_transit', 'maintenance']:
            vehicle_status[status] = len([v for v in vehicles if v.status == status])
        
        driver_status = {}
        for status in ['available', 'on_trip', 'off_duty']:
            driver_status[status] = len([d for d in drivers if d.status == status])
        
        active_shipments = Shipment.query.filter(
            Shipment.status.in_(['assigned', 'in_transit'])
        ).count()
        
        return {
            'vehicles': {
                'total': len(vehicles),
                'status_breakdown': vehicle_status
            },
            'drivers': {
                'total': len(drivers),
                'status_breakdown': driver_status
            },
            'shipments': {
                'active': active_shipments
            }
        }
    
    def schedule_maintenance(self, vehicle_id: int, maintenance_data: Dict, user: User):
        """Schedule vehicle maintenance"""
        from models.logistics import VehicleMaintenance
        
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        maintenance = VehicleMaintenance(
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_data['maintenance_type'],
            description=maintenance_data['description'],
            scheduled_date=datetime.fromisoformat(maintenance_data['scheduled_date']),
            service_provider=maintenance_data.get('service_provider'),
            estimated_cost=maintenance_data.get('estimated_cost'),
            created_by=user.id
        )
        
        db.session.add(maintenance)
        
        # Update vehicle next maintenance
        vehicle.next_maintenance = maintenance.scheduled_date
        
        db.session.commit()
        return maintenance
    
    # Helper methods
    def _create_tracking_update(self, shipment: Shipment, status: str, description: str, user: User):
        """Create tracking update"""
        tracking = ShipmentTracking(
            shipment_id=shipment.id,
            status=status,
            description=description,
            location=shipment.current_location,
            updated_by=user.id
        )
        db.session.add(tracking)
    
    def _calculate_shipping_cost(self, shipment: Shipment):
        """Calculate estimated shipping cost"""
        base_rate = 10  # per km
        weight_rate = 2   # per kg
        
        distance = shipment.distance_planned or 100  # default distance
        weight = shipment.total_weight or 0
        
        distance_cost = distance * base_rate
        weight_cost = weight * weight_rate
        
        return distance_cost + weight_cost
    
    def _calculate_actual_cost(self, shipment: Shipment):
        """Calculate actual shipping cost"""
        fuel_cost = shipment.fuel_cost or 0
        driver_payment = shipment.driver_payment or 500  # default payment
        
        return fuel_cost + driver_payment
    
    def _calculate_distance(self, origin: Dict, destination: Dict):
        """Calculate distance between two points"""
        # Simple distance calculation (would use proper mapping service)
        if not origin or not destination:
            return 100  # default
        
        # Haversine formula would go here
        return 150  # placeholder