import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class MaintenanceAI:
    def __init__(self):
        self.failure_patterns = {
            'vibration_increase': {'threshold': 1.5, 'severity': 'high'},
            'temperature_rise': {'threshold': 10, 'severity': 'medium'},
            'efficiency_drop': {'threshold': 0.15, 'severity': 'high'},
            'unusual_noise': {'threshold': 0.8, 'severity': 'medium'}
        }
    
    def predict_equipment_failure(self, equipment_data: Dict, readings_history: List[Dict]) -> Dict:
        """Predict equipment failure using AI analysis"""
        try:
            # Calculate health score
            health_score = self._calculate_health_score(equipment_data, readings_history)
            
            # Predict failure probability
            failure_probability = self._calculate_failure_probability(equipment_data, readings_history)
            
            # Estimate time to failure
            time_to_failure = self._estimate_time_to_failure(readings_history, failure_probability)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(equipment_data, readings_history)
            
            # Generate recommendations
            recommendations = self._generate_maintenance_recommendations(
                health_score, failure_probability, risk_factors
            )
            
            return {
                'health_score': health_score,
                'failure_probability': failure_probability,
                'estimated_days_to_failure': time_to_failure,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'maintenance_priority': self._determine_priority(failure_probability, health_score),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                'health_score': 70,
                'failure_probability': 0.3,
                'estimated_days_to_failure': 30,
                'risk_factors': ['Analysis error'],
                'recommendations': ['Manual inspection required'],
                'maintenance_priority': 'medium',
                'error': str(e)
            }
    
    def _calculate_health_score(self, equipment_data: Dict, readings_history: List[Dict]) -> float:
        """Calculate equipment health score (0-100)"""
        base_score = 100
        
        # Age factor
        age_years = equipment_data.get('age_years', 0)
        age_penalty = min(30, age_years * 2)  # Max 30 points for age
        base_score -= age_penalty
        
        # Operating hours factor
        total_hours = equipment_data.get('total_operating_hours', 0)
        expected_life_hours = equipment_data.get('expected_life_hours', 50000)
        usage_ratio = total_hours / expected_life_hours if expected_life_hours > 0 else 0
        usage_penalty = min(25, usage_ratio * 25)  # Max 25 points for usage
        base_score -= usage_penalty
        
        # Recent readings analysis
        if readings_history:
            readings_penalty = self._analyze_readings_health(readings_history)
            base_score -= readings_penalty
        
        # Maintenance history factor
        last_service_days = equipment_data.get('days_since_last_service', 0)
        service_interval = equipment_data.get('service_interval_days', 90)
        if last_service_days > service_interval:
            overdue_penalty = min(15, (last_service_days - service_interval) / 10)
            base_score -= overdue_penalty
        
        return max(0, min(100, base_score))
    
    def _analyze_readings_health(self, readings_history: List[Dict]) -> float:
        """Analyze equipment readings for health indicators"""
        penalty = 0
        
        if len(readings_history) < 5:
            return 5  # Insufficient data penalty
        
        # Group readings by type
        readings_by_type = {}
        for reading in readings_history[-20:]:  # Last 20 readings
            reading_type = reading.get('reading_type')
            if reading_type not in readings_by_type:
                readings_by_type[reading_type] = []
            readings_by_type[reading_type].append(reading)
        
        # Analyze each reading type
        for reading_type, readings in readings_by_type.items():
            if len(readings) >= 3:
                values = [r.get('reading_value', 0) for r in readings]
                
                # Check for trends
                if reading_type == 'temperature':
                    avg_temp = np.mean(values)
                    if avg_temp > 80:  # High temperature
                        penalty += 10
                    elif avg_temp > 70:
                        penalty += 5
                
                elif reading_type == 'vibration':
                    avg_vibration = np.mean(values)
                    if avg_vibration > 5:  # High vibration
                        penalty += 15
                    elif avg_vibration > 3:
                        penalty += 8
                
                elif reading_type == 'efficiency':
                    avg_efficiency = np.mean(values)
                    if avg_efficiency < 70:  # Low efficiency
                        penalty += 12
                    elif avg_efficiency < 80:
                        penalty += 6
                
                # Check for increasing trends (deterioration)
                if len(values) >= 5:
                    trend = self._calculate_trend(values)
                    if reading_type in ['temperature', 'vibration'] and trend > 0.1:
                        penalty += 8
                    elif reading_type == 'efficiency' and trend < -0.1:
                        penalty += 8
        
        return min(30, penalty)  # Max 30 points penalty from readings
    
    def _calculate_failure_probability(self, equipment_data: Dict, readings_history: List[Dict]) -> float:
        """Calculate probability of failure in next 30 days"""
        base_probability = 0.1  # 10% base probability
        
        # Age factor
        age_years = equipment_data.get('age_years', 0)
        age_factor = min(0.3, age_years * 0.02)  # Max 30% from age
        
        # Usage factor
        total_hours = equipment_data.get('total_operating_hours', 0)
        expected_life_hours = equipment_data.get('expected_life_hours', 50000)
        usage_ratio = total_hours / expected_life_hours if expected_life_hours > 0 else 0
        usage_factor = min(0.25, usage_ratio * 0.25)  # Max 25% from usage
        
        # Maintenance overdue factor
        last_service_days = equipment_data.get('days_since_last_service', 0)
        service_interval = equipment_data.get('service_interval_days', 90)
        if last_service_days > service_interval:
            overdue_factor = min(0.2, (last_service_days - service_interval) / 365)
        else:
            overdue_factor = 0
        
        # Readings factor
        readings_factor = self._calculate_readings_risk(readings_history)
        
        total_probability = base_probability + age_factor + usage_factor + overdue_factor + readings_factor
        return min(0.95, total_probability)  # Cap at 95%
    
    def _calculate_readings_risk(self, readings_history: List[Dict]) -> float:
        """Calculate risk factor from equipment readings"""
        if not readings_history:
            return 0.1  # Unknown risk
        
        risk_factor = 0
        
        # Analyze recent readings for anomalies
        recent_readings = readings_history[-10:]  # Last 10 readings
        
        for reading in recent_readings:
            anomaly_score = reading.get('anomaly_score', 0)
            if anomaly_score > 0.8:
                risk_factor += 0.05
            elif anomaly_score > 0.6:
                risk_factor += 0.02
        
        return min(0.3, risk_factor)  # Max 30% from readings
    
    def _estimate_time_to_failure(self, readings_history: List[Dict], failure_probability: float) -> int:
        """Estimate days until potential failure"""
        if failure_probability < 0.2:
            return 180  # Low risk - 6 months
        elif failure_probability < 0.4:
            return 90   # Medium risk - 3 months
        elif failure_probability < 0.6:
            return 45   # High risk - 1.5 months
        elif failure_probability < 0.8:
            return 15   # Very high risk - 2 weeks
        else:
            return 7    # Critical risk - 1 week
    
    def _identify_risk_factors(self, equipment_data: Dict, readings_history: List[Dict]) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        # Age-related risks
        age_years = equipment_data.get('age_years', 0)
        if age_years > 10:
            risk_factors.append(f"Equipment age: {age_years} years")
        
        # Usage-related risks
        total_hours = equipment_data.get('total_operating_hours', 0)
        expected_life_hours = equipment_data.get('expected_life_hours', 50000)
        if total_hours > expected_life_hours * 0.8:
            risk_factors.append("High operating hours")
        
        # Maintenance-related risks
        last_service_days = equipment_data.get('days_since_last_service', 0)
        service_interval = equipment_data.get('service_interval_days', 90)
        if last_service_days > service_interval:
            risk_factors.append(f"Maintenance overdue by {last_service_days - service_interval} days")
        
        # Readings-related risks
        if readings_history:
            recent_readings = readings_history[-5:]
            
            # Check for high temperature
            temp_readings = [r for r in recent_readings if r.get('reading_type') == 'temperature']
            if temp_readings:
                avg_temp = np.mean([r.get('reading_value', 0) for r in temp_readings])
                if avg_temp > 80:
                    risk_factors.append(f"High operating temperature: {avg_temp:.1f}°C")
            
            # Check for high vibration
            vib_readings = [r for r in recent_readings if r.get('reading_type') == 'vibration']
            if vib_readings:
                avg_vib = np.mean([r.get('reading_value', 0) for r in vib_readings])
                if avg_vib > 5:
                    risk_factors.append(f"High vibration levels: {avg_vib:.1f}")
            
            # Check for low efficiency
            eff_readings = [r for r in recent_readings if r.get('reading_type') == 'efficiency']
            if eff_readings:
                avg_eff = np.mean([r.get('reading_value', 0) for r in eff_readings])
                if avg_eff < 75:
                    risk_factors.append(f"Low efficiency: {avg_eff:.1f}%")
        
        return risk_factors
    
    def _generate_maintenance_recommendations(self, health_score: float, failure_probability: float, risk_factors: List[str]) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []
        
        # Health score based recommendations
        if health_score < 50:
            recommendations.append("Schedule immediate comprehensive inspection")
            recommendations.append("Consider equipment replacement planning")
        elif health_score < 70:
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Schedule detailed maintenance review")
        elif health_score < 85:
            recommendations.append("Continue regular maintenance schedule")
            recommendations.append("Monitor key performance indicators")
        
        # Failure probability based recommendations
        if failure_probability > 0.7:
            recommendations.append("Prepare backup equipment")
            recommendations.append("Schedule emergency maintenance window")
        elif failure_probability > 0.5:
            recommendations.append("Accelerate planned maintenance")
            recommendations.append("Increase spare parts inventory")
        
        # Risk factor specific recommendations
        for risk_factor in risk_factors:
            if "temperature" in risk_factor.lower():
                recommendations.append("Check cooling system and ventilation")
                recommendations.append("Inspect for blockages or wear")
            elif "vibration" in risk_factor.lower():
                recommendations.append("Check alignment and balance")
                recommendations.append("Inspect bearings and mounting")
            elif "efficiency" in risk_factor.lower():
                recommendations.append("Clean and calibrate equipment")
                recommendations.append("Check for wear in critical components")
            elif "overdue" in risk_factor.lower():
                recommendations.append("Schedule overdue maintenance immediately")
            elif "age" in risk_factor.lower():
                recommendations.append("Develop replacement timeline")
                recommendations.append("Increase inspection frequency")
        
        return list(set(recommendations))[:8]  # Remove duplicates and limit to 8
    
    def _determine_priority(self, failure_probability: float, health_score: float) -> str:
        """Determine maintenance priority"""
        if failure_probability > 0.7 or health_score < 40:
            return 'critical'
        elif failure_probability > 0.5 or health_score < 60:
            return 'high'
        elif failure_probability > 0.3 or health_score < 80:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in values (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        z = np.polyfit(x, values, 1)
        return z[0]  # Slope of the trend line
    
    def optimize_maintenance_schedule(self, equipment_list: List[Dict], constraints: Dict) -> Dict:
        """Optimize maintenance schedule using AI"""
        try:
            optimized_schedule = []
            total_cost = 0
            total_downtime = 0
            
            # Sort equipment by priority
            equipment_with_priority = []
            for equipment in equipment_list:
                failure_prob = equipment.get('failure_probability', 0.3)
                health_score = equipment.get('health_score', 70)
                priority_score = failure_prob * 100 + (100 - health_score)
                equipment_with_priority.append((equipment, priority_score))
            
            equipment_with_priority.sort(key=lambda x: x[1], reverse=True)
            
            # Schedule maintenance based on priority and constraints
            available_dates = self._generate_available_dates(constraints)
            technician_capacity = constraints.get('technician_capacity', {})
            
            for equipment, priority_score in equipment_with_priority:
                optimal_date = self._find_optimal_maintenance_date(
                    equipment, available_dates, technician_capacity
                )
                
                if optimal_date:
                    maintenance_item = {
                        'equipment_id': equipment['id'],
                        'equipment_name': equipment['equipment_name'],
                        'scheduled_date': optimal_date.isoformat(),
                        'priority_score': priority_score,
                        'estimated_duration': equipment.get('estimated_maintenance_duration', 240),
                        'estimated_cost': equipment.get('estimated_maintenance_cost', 1000),
                        'required_skills': equipment.get('required_skills', []),
                        'required_parts': equipment.get('required_parts', [])
                    }
                    
                    optimized_schedule.append(maintenance_item)
                    total_cost += maintenance_item['estimated_cost']
                    total_downtime += maintenance_item['estimated_duration']
            
            return {
                'optimized_schedule': optimized_schedule,
                'total_estimated_cost': total_cost,
                'total_estimated_downtime': total_downtime,
                'optimization_score': self._calculate_optimization_score(optimized_schedule),
                'recommendations': self._generate_schedule_recommendations(optimized_schedule, constraints)
            }
        
        except Exception as e:
            return {
                'optimized_schedule': [],
                'error': str(e),
                'recommendations': ['Manual scheduling required']
            }
    
    def _generate_available_dates(self, constraints: Dict) -> List[datetime]:
        """Generate list of available maintenance dates"""
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=constraints.get('planning_horizon_days', 90))
        
        available_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends if specified
            if constraints.get('skip_weekends', True) and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Skip blackout dates
            blackout_dates = constraints.get('blackout_dates', [])
            if current_date.date().isoformat() not in blackout_dates:
                available_dates.append(current_date)
            
            current_date += timedelta(days=1)
        
        return available_dates
    
    def _find_optimal_maintenance_date(self, equipment: Dict, available_dates: List[datetime], technician_capacity: Dict) -> datetime:
        """Find optimal maintenance date for equipment"""
        failure_probability = equipment.get('failure_probability', 0.3)
        
        # Calculate urgency - higher failure probability means sooner maintenance
        if failure_probability > 0.7:
            max_delay_days = 7
        elif failure_probability > 0.5:
            max_delay_days = 21
        elif failure_probability > 0.3:
            max_delay_days = 45
        else:
            max_delay_days = 90
        
        # Find earliest suitable date within urgency window
        urgency_deadline = datetime.now() + timedelta(days=max_delay_days)
        
        for date in available_dates:
            if date <= urgency_deadline:
                # Check technician availability
                required_skills = equipment.get('required_skills', [])
                if self._check_technician_availability(date, required_skills, technician_capacity):
                    return date
        
        # If no date found within urgency window, return earliest available
        return available_dates[0] if available_dates else None
    
    def _check_technician_availability(self, date: datetime, required_skills: List[str], technician_capacity: Dict) -> bool:
        """Check if technicians with required skills are available"""
        # Simplified availability check
        date_str = date.date().isoformat()
        daily_capacity = technician_capacity.get(date_str, {})
        
        for skill in required_skills:
            if daily_capacity.get(skill, 0) < 1:
                return False
        
        return True
    
    def _calculate_optimization_score(self, schedule: List[Dict]) -> float:
        """Calculate optimization score for the schedule"""
        if not schedule:
            return 0
        
        # Score based on priority ordering and timing
        score = 100
        
        # Check if high priority items are scheduled early
        for i, item in enumerate(schedule):
            priority_score = item.get('priority_score', 0)
            if priority_score > 150 and i > 5:  # High priority item scheduled late
                score -= 10
        
        return max(0, min(100, score))
    
    def _generate_schedule_recommendations(self, schedule: List[Dict], constraints: Dict) -> List[str]:
        """Generate recommendations for the optimized schedule"""
        recommendations = []
        
        if not schedule:
            recommendations.append("No equipment scheduled for maintenance")
            return recommendations
        
        # Check for clustering
        dates = [item['scheduled_date'] for item in schedule]
        if len(set(dates)) < len(dates) * 0.7:
            recommendations.append("Consider spreading maintenance across more dates")
        
        # Check for high-cost periods
        total_cost = sum(item.get('estimated_cost', 0) for item in schedule)
        if total_cost > constraints.get('budget_limit', float('inf')):
            recommendations.append("Schedule exceeds budget - consider phasing maintenance")
        
        # Check for critical items
        critical_items = [item for item in schedule if item.get('priority_score', 0) > 150]
        if critical_items:
            recommendations.append(f"{len(critical_items)} critical maintenance items require immediate attention")
        
        return recommendations
    
    def analyze_spare_parts_demand(self, maintenance_schedule: List[Dict], historical_usage: List[Dict]) -> Dict:
        """Analyze and predict spare parts demand"""
        try:
            parts_demand = {}
            
            # Analyze scheduled maintenance requirements
            for maintenance_item in maintenance_schedule:
                required_parts = maintenance_item.get('required_parts', [])
                for part in required_parts:
                    part_id = part.get('part_id')
                    quantity = part.get('quantity', 1)
                    
                    if part_id not in parts_demand:
                        parts_demand[part_id] = {
                            'scheduled_demand': 0,
                            'predicted_demand': 0,
                            'total_demand': 0
                        }
                    
                    parts_demand[part_id]['scheduled_demand'] += quantity
            
            # Analyze historical usage patterns
            if historical_usage:
                for part_id in parts_demand:
                    historical_data = [usage for usage in historical_usage if usage.get('part_id') == part_id]
                    if historical_data:
                        monthly_usage = [usage.get('quantity', 0) for usage in historical_data[-12:]]
                        avg_monthly_usage = np.mean(monthly_usage) if monthly_usage else 0
                        parts_demand[part_id]['predicted_demand'] = avg_monthly_usage * 3  # 3 months ahead
            
            # Calculate total demand
            for part_id in parts_demand:
                parts_demand[part_id]['total_demand'] = (
                    parts_demand[part_id]['scheduled_demand'] + 
                    parts_demand[part_id]['predicted_demand']
                )
            
            return {
                'parts_demand_forecast': parts_demand,
                'high_demand_parts': [
                    part_id for part_id, demand in parts_demand.items() 
                    if demand['total_demand'] > 5
                ],
                'recommendations': self._generate_parts_recommendations(parts_demand)
            }
        
        except Exception as e:
            return {
                'parts_demand_forecast': {},
                'error': str(e),
                'recommendations': ['Manual parts planning required']
            }
    
    def _generate_parts_recommendations(self, parts_demand: Dict) -> List[str]:
        """Generate spare parts recommendations"""
        recommendations = []
        
        high_demand_parts = [
            part_id for part_id, demand in parts_demand.items() 
            if demand['total_demand'] > 5
        ]
        
        if high_demand_parts:
            recommendations.append(f"Increase stock for {len(high_demand_parts)} high-demand parts")
        
        critical_parts = [
            part_id for part_id, demand in parts_demand.items() 
            if demand['scheduled_demand'] > 0
        ]
        
        if critical_parts:
            recommendations.append(f"Ensure availability of {len(critical_parts)} parts for scheduled maintenance")
        
        return recommendations