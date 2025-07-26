"""
Predictive Maintenance System for Rice Mill Equipment
48-72 hour failure predictions with specific maintenance recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaintenanceUrgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EquipmentStatus(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    ALERT = "alert"
    FAILURE = "failure"

@dataclass
class MaintenancePrediction:
    equipment_id: str
    equipment_name: str
    predicted_failure_time: datetime
    confidence: float
    urgency: MaintenanceUrgency
    failure_type: str
    recommended_actions: List[str]
    estimated_cost: float
    downtime_hours: float
    risk_factors: List[str]

@dataclass
class EquipmentMetrics:
    equipment_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    power_consumption: float
    efficiency: float
    operating_hours: float
    last_maintenance: datetime

class PredictiveMaintenanceEngine:
    """Advanced predictive maintenance engine for rice mill equipment"""
    
    def __init__(self):
        self.equipment_profiles = self._load_equipment_profiles()
        self.failure_patterns = self._load_failure_patterns()
        self.maintenance_history = self._load_maintenance_history()
        self.threshold_models = self._initialize_threshold_models()
        
    def _load_equipment_profiles(self) -> Dict:
        """Load equipment profiles and specifications"""
        return {
            'mill_1': {
                'name': 'Primary Rice Mill #1',
                'type': 'rice_mill',
                'manufacturer': 'ABC Mills',
                'model': 'RM-2000',
                'installation_date': '2020-01-15',
                'expected_life': 10,  # years
                'critical_components': ['motor', 'bearings', 'grinding_chamber', 'belt'],
                'normal_operating_ranges': {
                    'temperature': (40, 80),  # Celsius
                    'vibration': (0, 5),      # mm/s
                    'pressure': (2, 8),       # bar
                    'power_consumption': (15, 25),  # kW
                    'efficiency': (85, 95)    # percentage
                }
            },
            'mill_2': {
                'name': 'Secondary Rice Mill #2',
                'type': 'rice_mill',
                'manufacturer': 'XYZ Equipment',
                'model': 'RM-1500',
                'installation_date': '2019-06-20',
                'expected_life': 12,
                'critical_components': ['motor', 'bearings', 'grinding_chamber', 'belt'],
                'normal_operating_ranges': {
                    'temperature': (35, 75),
                    'vibration': (0, 4),
                    'pressure': (1.5, 7),
                    'power_consumption': (12, 20),
                    'efficiency': (80, 92)
                }
            },
            'dryer_1': {
                'name': 'Paddy Dryer #1',
                'type': 'dryer',
                'manufacturer': 'DryTech',
                'model': 'PD-500',
                'installation_date': '2021-03-10',
                'expected_life': 8,
                'critical_components': ['heating_element', 'fan', 'temperature_sensor', 'conveyor'],
                'normal_operating_ranges': {
                    'temperature': (60, 120),
                    'vibration': (0, 3),
                    'pressure': (0.5, 3),
                    'power_consumption': (8, 15),
                    'efficiency': (75, 90)
                }
            },
            'cleaner_1': {
                'name': 'Grain Cleaner #1',
                'type': 'cleaner',
                'manufacturer': 'CleanGrain',
                'model': 'GC-300',
                'installation_date': '2020-08-05',
                'expected_life': 6,
                'critical_components': ['screens', 'aspirator', 'motor', 'vibrator'],
                'normal_operating_ranges': {
                    'temperature': (25, 50),
                    'vibration': (2, 8),
                    'pressure': (1, 4),
                    'power_consumption': (5, 12),
                    'efficiency': (70, 85)
                }
            }
        }
    
    def _load_failure_patterns(self) -> Dict:
        """Load historical failure patterns and signatures"""
        return {
            'bearing_failure': {
                'early_indicators': {
                    'vibration_increase': 20,  # % above normal
                    'temperature_increase': 15,
                    'efficiency_decrease': 5
                },
                'progression_time': 72,  # hours
                'failure_signature': {
                    'vibration_spike': 50,
                    'temperature_spike': 30,
                    'power_fluctuation': 25
                }
            },
            'motor_failure': {
                'early_indicators': {
                    'power_consumption_increase': 15,
                    'temperature_increase': 20,
                    'efficiency_decrease': 10
                },
                'progression_time': 48,
                'failure_signature': {
                    'power_spike': 40,
                    'temperature_spike': 35,
                    'vibration_increase': 30
                }
            },
            'belt_failure': {
                'early_indicators': {
                    'vibration_increase': 25,
                    'efficiency_decrease': 8,
                    'power_fluctuation': 10
                },
                'progression_time': 24,
                'failure_signature': {
                    'vibration_spike': 60,
                    'efficiency_drop': 20,
                    'power_drop': 15
                }
            },
            'heating_element_failure': {
                'early_indicators': {
                    'temperature_inconsistency': 10,
                    'power_consumption_decrease': 12,
                    'efficiency_decrease': 15
                },
                'progression_time': 96,
                'failure_signature': {
                    'temperature_drop': 40,
                    'power_drop': 30,
                    'efficiency_drop': 25
                }
            }
        }
    
    def _load_maintenance_history(self) -> Dict:
        """Load historical maintenance data"""
        # In production, this would load from database
        return {
            'mill_1': [
                {'date': '2024-01-15', 'type': 'preventive', 'component': 'bearings', 'cost': 5000},
                {'date': '2023-11-20', 'type': 'corrective', 'component': 'belt', 'cost': 2000},
                {'date': '2023-08-10', 'type': 'preventive', 'component': 'motor', 'cost': 8000}
            ],
            'mill_2': [
                {'date': '2024-02-01', 'type': 'preventive', 'component': 'bearings', 'cost': 4500},
                {'date': '2023-12-15', 'type': 'preventive', 'component': 'grinding_chamber', 'cost': 6000}
            ],
            'dryer_1': [
                {'date': '2024-01-30', 'type': 'corrective', 'component': 'heating_element', 'cost': 3000},
                {'date': '2023-10-05', 'type': 'preventive', 'component': 'fan', 'cost': 1500}
            ],
            'cleaner_1': [
                {'date': '2024-02-10', 'type': 'preventive', 'component': 'screens', 'cost': 1000},
                {'date': '2023-09-20', 'type': 'corrective', 'component': 'vibrator', 'cost': 2500}
            ]
        }
    
    def _initialize_threshold_models(self) -> Dict:
        """Initialize threshold models for anomaly detection"""
        return {
            'temperature_model': {
                'warning_threshold': 1.2,  # 20% above normal
                'alert_threshold': 1.4,    # 40% above normal
                'critical_threshold': 1.6   # 60% above normal
            },
            'vibration_model': {
                'warning_threshold': 1.5,
                'alert_threshold': 2.0,
                'critical_threshold': 3.0
            },
            'efficiency_model': {
                'warning_threshold': 0.9,  # 10% below normal
                'alert_threshold': 0.8,    # 20% below normal
                'critical_threshold': 0.7   # 30% below normal
            },
            'power_model': {
                'warning_threshold': 1.15,
                'alert_threshold': 1.3,
                'critical_threshold': 1.5
            }
        }
    
    def analyze_equipment_health(self, equipment_metrics: List[EquipmentMetrics]) -> Dict:
        """Analyze current equipment health and predict maintenance needs"""
        try:
            predictions = []
            equipment_status = {}
            
            # Group metrics by equipment
            equipment_data = {}
            for metric in equipment_metrics:
                if metric.equipment_id not in equipment_data:
                    equipment_data[metric.equipment_id] = []
                equipment_data[metric.equipment_id].append(metric)
            
            # Analyze each equipment
            for equipment_id, metrics in equipment_data.items():
                if equipment_id not in self.equipment_profiles:
                    continue
                
                # Get latest metrics
                latest_metrics = sorted(metrics, key=lambda x: x.timestamp)[-1]
                
                # Analyze trends
                trend_analysis = self._analyze_trends(metrics)
                
                # Detect anomalies
                anomalies = self._detect_anomalies(equipment_id, latest_metrics)
                
                # Predict failures
                failure_predictions = self._predict_failures(
                    equipment_id, latest_metrics, trend_analysis, anomalies
                )
                
                # Determine equipment status
                status = self._determine_equipment_status(anomalies, failure_predictions)
                equipment_status[equipment_id] = status
                
                # Add predictions
                predictions.extend(failure_predictions)
            
            # Sort predictions by urgency and time
            predictions.sort(key=lambda x: (x.urgency.value, x.predicted_failure_time))
            
            # Generate summary
            summary = self._generate_maintenance_summary(predictions, equipment_status)
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'predictions': [self._prediction_to_dict(p) for p in predictions],
                'equipment_status': {k: v.value for k, v in equipment_status.items()},
                'summary': summary,
                'recommendations': self._generate_recommendations(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in equipment health analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_trends(self, metrics: List[EquipmentMetrics]) -> Dict:
        """Analyze trends in equipment metrics"""
        if len(metrics) < 2:
            return {}
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        
        # Calculate trends for each metric
        trends = {}
        
        # Temperature trend
        temperatures = [m.temperature for m in sorted_metrics]
        trends['temperature'] = self._calculate_trend(temperatures)
        
        # Vibration trend
        vibrations = [m.vibration for m in sorted_metrics]
        trends['vibration'] = self._calculate_trend(vibrations)
        
        # Efficiency trend
        efficiencies = [m.efficiency for m in sorted_metrics]
        trends['efficiency'] = self._calculate_trend(efficiencies)
        
        # Power consumption trend
        power_consumptions = [m.power_consumption for m in sorted_metrics]
        trends['power_consumption'] = self._calculate_trend(power_consumptions)
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict:
        """Calculate trend statistics for a series of values"""
        if len(values) < 2:
            return {'direction': 'stable', 'rate': 0, 'confidence': 0}
        
        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine direction
        if abs(slope) < 0.1:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Calculate confidence based on R-squared
        correlation = np.corrcoef(x, y)[0, 1]
        confidence = correlation ** 2 if not np.isnan(correlation) else 0
        
        return {
            'direction': direction,
            'rate': float(slope),
            'confidence': float(confidence)
        }
    
    def _detect_anomalies(self, equipment_id: str, metrics: EquipmentMetrics) -> Dict:
        """Detect anomalies in current equipment metrics"""
        profile = self.equipment_profiles[equipment_id]
        normal_ranges = profile['normal_operating_ranges']
        anomalies = {}
        
        # Check temperature
        temp_range = normal_ranges['temperature']
        if metrics.temperature > temp_range[1]:
            severity = self._calculate_severity('temperature', metrics.temperature, temp_range[1])
            anomalies['temperature'] = {
                'type': 'high_temperature',
                'value': metrics.temperature,
                'normal_max': temp_range[1],
                'severity': severity
            }
        
        # Check vibration
        vib_range = normal_ranges['vibration']
        if metrics.vibration > vib_range[1]:
            severity = self._calculate_severity('vibration', metrics.vibration, vib_range[1])
            anomalies['vibration'] = {
                'type': 'high_vibration',
                'value': metrics.vibration,
                'normal_max': vib_range[1],
                'severity': severity
            }
        
        # Check efficiency
        eff_range = normal_ranges['efficiency']
        if metrics.efficiency < eff_range[0]:
            severity = self._calculate_severity('efficiency', metrics.efficiency, eff_range[0], reverse=True)
            anomalies['efficiency'] = {
                'type': 'low_efficiency',
                'value': metrics.efficiency,
                'normal_min': eff_range[0],
                'severity': severity
            }
        
        # Check power consumption
        power_range = normal_ranges['power_consumption']
        if metrics.power_consumption > power_range[1]:
            severity = self._calculate_severity('power_consumption', metrics.power_consumption, power_range[1])
            anomalies['power_consumption'] = {
                'type': 'high_power_consumption',
                'value': metrics.power_consumption,
                'normal_max': power_range[1],
                'severity': severity
            }
        
        return anomalies
    
    def _calculate_severity(self, metric_type: str, value: float, threshold: float, reverse: bool = False) -> str:
        """Calculate severity of anomaly"""
        thresholds = self.threshold_models.get(f'{metric_type}_model', {})
        
        if reverse:
            # For metrics where lower is worse (like efficiency)
            ratio = threshold / value if value > 0 else float('inf')
        else:
            # For metrics where higher is worse
            ratio = value / threshold if threshold > 0 else float('inf')
        
        if ratio >= thresholds.get('critical_threshold', 1.6):
            return 'critical'
        elif ratio >= thresholds.get('alert_threshold', 1.4):
            return 'alert'
        elif ratio >= thresholds.get('warning_threshold', 1.2):
            return 'warning'
        else:
            return 'normal'
    
    def _predict_failures(self, equipment_id: str, metrics: EquipmentMetrics, 
                         trends: Dict, anomalies: Dict) -> List[MaintenancePrediction]:
        """Predict potential failures based on current state and trends"""
        predictions = []
        profile = self.equipment_profiles[equipment_id]
        
        # Check for bearing failure patterns
        if self._check_bearing_failure_pattern(metrics, trends, anomalies):
            prediction = self._create_bearing_failure_prediction(equipment_id, metrics)
            predictions.append(prediction)
        
        # Check for motor failure patterns
        if self._check_motor_failure_pattern(metrics, trends, anomalies):
            prediction = self._create_motor_failure_prediction(equipment_id, metrics)
            predictions.append(prediction)
        
        # Check for belt failure patterns
        if self._check_belt_failure_pattern(metrics, trends, anomalies):
            prediction = self._create_belt_failure_prediction(equipment_id, metrics)
            predictions.append(prediction)
        
        # Check equipment age-based predictions
        age_prediction = self._check_age_based_maintenance(equipment_id, metrics)
        if age_prediction:
            predictions.append(age_prediction)
        
        return predictions
    
    def _check_bearing_failure_pattern(self, metrics: EquipmentMetrics, 
                                     trends: Dict, anomalies: Dict) -> bool:
        """Check if current state matches bearing failure pattern"""
        pattern = self.failure_patterns['bearing_failure']['early_indicators']
        
        # Check vibration increase
        vibration_anomaly = anomalies.get('vibration', {})
        if vibration_anomaly.get('severity') in ['alert', 'critical']:
            return True
        
        # Check temperature increase with vibration trend
        temp_anomaly = anomalies.get('temperature', {})
        vibration_trend = trends.get('vibration', {})
        
        if (temp_anomaly.get('severity') == 'warning' and 
            vibration_trend.get('direction') == 'increasing'):
            return True
        
        return False
    
    def _check_motor_failure_pattern(self, metrics: EquipmentMetrics, 
                                   trends: Dict, anomalies: Dict) -> bool:
        """Check if current state matches motor failure pattern"""
        power_anomaly = anomalies.get('power_consumption', {})
        temp_anomaly = anomalies.get('temperature', {})
        efficiency_anomaly = anomalies.get('efficiency', {})
        
        # High power consumption with temperature increase
        if (power_anomaly.get('severity') in ['warning', 'alert'] and
            temp_anomaly.get('severity') in ['warning', 'alert']):
            return True
        
        # Efficiency decrease with power increase
        if (efficiency_anomaly.get('severity') == 'warning' and
            power_anomaly.get('severity') == 'warning'):
            return True
        
        return False
    
    def _check_belt_failure_pattern(self, metrics: EquipmentMetrics, 
                                  trends: Dict, anomalies: Dict) -> bool:
        """Check if current state matches belt failure pattern"""
        vibration_trend = trends.get('vibration', {})
        efficiency_anomaly = anomalies.get('efficiency', {})
        
        # Increasing vibration with efficiency decrease
        if (vibration_trend.get('direction') == 'increasing' and
            vibration_trend.get('confidence') > 0.7 and
            efficiency_anomaly.get('severity') == 'warning'):
            return True
        
        return False
    
    def _create_bearing_failure_prediction(self, equipment_id: str, 
                                         metrics: EquipmentMetrics) -> MaintenancePrediction:
        """Create bearing failure prediction"""
        profile = self.equipment_profiles[equipment_id]
        failure_time = datetime.now() + timedelta(hours=72)
        
        return MaintenancePrediction(
            equipment_id=equipment_id,
            equipment_name=profile['name'],
            predicted_failure_time=failure_time,
            confidence=0.85,
            urgency=MaintenanceUrgency.HIGH,
            failure_type='bearing_failure',
            recommended_actions=[
                'Schedule immediate bearing inspection',
                'Prepare replacement bearings',
                'Plan 4-hour maintenance window',
                'Check lubrication system'
            ],
            estimated_cost=5000.0,
            downtime_hours=4.0,
            risk_factors=['High vibration', 'Temperature increase', 'Age of bearings']
        )
    
    def _create_motor_failure_prediction(self, equipment_id: str, 
                                       metrics: EquipmentMetrics) -> MaintenancePrediction:
        """Create motor failure prediction"""
        profile = self.equipment_profiles[equipment_id]
        failure_time = datetime.now() + timedelta(hours=48)
        
        return MaintenancePrediction(
            equipment_id=equipment_id,
            equipment_name=profile['name'],
            predicted_failure_time=failure_time,
            confidence=0.78,
            urgency=MaintenanceUrgency.CRITICAL,
            failure_type='motor_failure',
            recommended_actions=[
                'Schedule immediate motor inspection',
                'Check electrical connections',
                'Prepare backup motor if available',
                'Plan 6-hour maintenance window'
            ],
            estimated_cost=12000.0,
            downtime_hours=6.0,
            risk_factors=['High power consumption', 'Temperature spike', 'Efficiency drop']
        )
    
    def _create_belt_failure_prediction(self, equipment_id: str, 
                                      metrics: EquipmentMetrics) -> MaintenancePrediction:
        """Create belt failure prediction"""
        profile = self.equipment_profiles[equipment_id]
        failure_time = datetime.now() + timedelta(hours=24)
        
        return MaintenancePrediction(
            equipment_id=equipment_id,
            equipment_name=profile['name'],
            predicted_failure_time=failure_time,
            confidence=0.92,
            urgency=MaintenanceUrgency.HIGH,
            failure_type='belt_failure',
            recommended_actions=[
                'Inspect belt tension and alignment',
                'Prepare replacement belt',
                'Plan 2-hour maintenance window',
                'Check pulley condition'
            ],
            estimated_cost=2000.0,
            downtime_hours=2.0,
            risk_factors=['Vibration increase', 'Belt wear', 'Misalignment']
        )
    
    def _check_age_based_maintenance(self, equipment_id: str, 
                                   metrics: EquipmentMetrics) -> Optional[MaintenancePrediction]:
        """Check if equipment needs age-based maintenance"""
        profile = self.equipment_profiles[equipment_id]
        install_date = datetime.strptime(profile['installation_date'], '%Y-%m-%d')
        age_years = (datetime.now() - install_date).days / 365.25
        
        # Check if approaching major maintenance interval
        if age_years > 3 and metrics.operating_hours > 8000:
            failure_time = datetime.now() + timedelta(hours=168)  # 1 week
            
            return MaintenancePrediction(
                equipment_id=equipment_id,
                equipment_name=profile['name'],
                predicted_failure_time=failure_time,
                confidence=0.65,
                urgency=MaintenanceUrgency.MEDIUM,
                failure_type='scheduled_maintenance',
                recommended_actions=[
                    'Schedule comprehensive maintenance',
                    'Replace wear parts',
                    'Update lubrication',
                    'Calibrate sensors'
                ],
                estimated_cost=8000.0,
                downtime_hours=8.0,
                risk_factors=['Equipment age', 'High operating hours', 'Preventive maintenance due']
            )
        
        return None
    
    def _determine_equipment_status(self, anomalies: Dict, 
                                  predictions: List[MaintenancePrediction]) -> EquipmentStatus:
        """Determine overall equipment status"""
        # Check for critical predictions
        critical_predictions = [p for p in predictions if p.urgency == MaintenanceUrgency.CRITICAL]
        if critical_predictions:
            return EquipmentStatus.FAILURE
        
        # Check for high urgency predictions
        high_predictions = [p for p in predictions if p.urgency == MaintenanceUrgency.HIGH]
        if high_predictions:
            return EquipmentStatus.ALERT
        
        # Check for critical anomalies
        critical_anomalies = [a for a in anomalies.values() if a.get('severity') == 'critical']
        if critical_anomalies:
            return EquipmentStatus.ALERT
        
        # Check for warning anomalies
        warning_anomalies = [a for a in anomalies.values() if a.get('severity') in ['warning', 'alert']]
        if warning_anomalies:
            return EquipmentStatus.WARNING
        
        return EquipmentStatus.NORMAL
    
    def _generate_maintenance_summary(self, predictions: List[MaintenancePrediction], 
                                    equipment_status: Dict) -> Dict:
        """Generate maintenance summary"""
        total_predictions = len(predictions)
        critical_count = len([p for p in predictions if p.urgency == MaintenanceUrgency.CRITICAL])
        high_count = len([p for p in predictions if p.urgency == MaintenanceUrgency.HIGH])
        
        total_cost = sum(p.estimated_cost for p in predictions)
        total_downtime = sum(p.downtime_hours for p in predictions)
        
        # Equipment status summary
        status_counts = {}
        for status in equipment_status.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_predictions': total_predictions,
            'critical_predictions': critical_count,
            'high_priority_predictions': high_count,
            'estimated_total_cost': total_cost,
            'estimated_total_downtime': total_downtime,
            'equipment_status_summary': status_counts,
            'next_maintenance_due': predictions[0].predicted_failure_time.isoformat() if predictions else None
        }
    
    def _generate_recommendations(self, predictions: List[MaintenancePrediction]) -> List[str]:
        """Generate overall maintenance recommendations"""
        if not predictions:
            return ["All equipment operating normally. Continue regular monitoring."]
        
        recommendations = []
        
        # Critical recommendations
        critical_predictions = [p for p in predictions if p.urgency == MaintenanceUrgency.CRITICAL]
        if critical_predictions:
            recommendations.append(
                f"URGENT: {len(critical_predictions)} critical maintenance issue(s) detected. "
                "Immediate action required to prevent equipment failure."
            )
        
        # High priority recommendations
        high_predictions = [p for p in predictions if p.urgency == MaintenanceUrgency.HIGH]
        if high_predictions:
            recommendations.append(
                f"HIGH PRIORITY: {len(high_predictions)} equipment(s) require maintenance within 72 hours."
            )
        
        # Cost optimization
        total_cost = sum(p.estimated_cost for p in predictions)
        if total_cost > 20000:
            recommendations.append(
                f"Consider scheduling coordinated maintenance to optimize costs (Total: ₹{total_cost:,.0f})"
            )
        
        # Downtime optimization
        total_downtime = sum(p.downtime_hours for p in predictions)
        if total_downtime > 12:
            recommendations.append(
                f"Plan maintenance schedule to minimize production impact ({total_downtime:.1f} hours total)"
            )
        
        return recommendations
    
    def _prediction_to_dict(self, prediction: MaintenancePrediction) -> Dict:
        """Convert prediction object to dictionary"""
        return {
            'equipment_id': prediction.equipment_id,
            'equipment_name': prediction.equipment_name,
            'predicted_failure_time': prediction.predicted_failure_time.isoformat(),
            'confidence': prediction.confidence,
            'urgency': prediction.urgency.value,
            'failure_type': prediction.failure_type,
            'recommended_actions': prediction.recommended_actions,
            'estimated_cost': prediction.estimated_cost,
            'downtime_hours': prediction.downtime_hours,
            'risk_factors': prediction.risk_factors
        }

# Global instance
predictive_maintenance_engine = PredictiveMaintenanceEngine()
