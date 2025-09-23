"""
Enhanced Anomaly Detection Module for Rice Mill Management System
Implements advanced statistical process control and real-time anomaly detection.
"""

import json
import logging
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List, Tuple


class AnomalyDetector:
    """Enhanced Anomaly Detection for the Rice Mill Management System"""
    
    def __init__(self):
        """Initialize the Anomaly Detector module"""
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.isolation_forest = None
        self.control_limits = {}
        self.logger.info("Anomaly Detector module initialized")
    
    def detect_statistical_anomalies(self, data: List[Dict[str, Any]], 
                                   metric: str, 
                                   threshold: float = 3.0) -> Dict[str, Any]:
        """Detect anomalies using statistical process control (SPC)"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            if metric not in df.columns:
                return {
                    'success': False,
                    'error': f'Metric {metric} not found in data'
                }
            
            # Calculate control limits (mean ± threshold * std)
            values = df[metric].dropna()
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Avoid division by zero
            if std_val == 0:
                std_val = 1e-8
            
            upper_limit = mean_val + threshold * std_val
            lower_limit = mean_val - threshold * std_val
            
            # Identify anomalies
            anomalies = []
            for i, row in df.iterrows():
                value = row[metric]
                if not pd.isna(value) and (value > upper_limit or value < lower_limit):
                    anomalies.append({
                        'index': i,
                        'value': float(value),
                        'upper_limit': float(upper_limit),
                        'lower_limit': float(lower_limit),
                        'z_score': float(abs(value - mean_val) / std_val)
                    })
            
            # Store control limits for future reference
            self.control_limits[metric] = {
                'mean': float(mean_val),
                'std': float(std_val),
                'upper_limit': float(upper_limit),
                'lower_limit': float(lower_limit)
            }
            
            return {
                'success': True,
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'total_points': len(df),
                'control_limits': self.control_limits[metric]
            }
            
        except Exception as e:
            self.logger.error(f"Error in statistical anomaly detection: {str(e)}")
            return {
                'success': False,
                'error': f'Statistical anomaly detection error: {str(e)}'
            }
    
    def detect_multivariate_anomalies(self, data: List[Dict[str, Any]], 
                                    contamination: float = 0.1) -> Dict[str, Any]:
        """Detect anomalies using multivariate analysis with Isolation Forest"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Select numerical columns
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) == 0:
                return {
                    'success': False,
                    'error': 'No numerical data found for anomaly detection'
                }
            
            # Prepare data
            X = df[numerical_cols].values
            
            # Standardize features
            X_scaled = self.scaler.fit_transform(X)
            
            # Fit Isolation Forest
            self.isolation_forest = IsolationForest(contamination=contamination, 
                                                  random_state=42, 
                                                  n_estimators=100)
            anomaly_labels = self.isolation_forest.fit_predict(X_scaled)
            
            # Calculate anomaly scores
            anomaly_scores = self.isolation_forest.decision_function(X_scaled)
            
            # Identify anomalies
            anomalies = []
            for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly detected
                    anomalies.append({
                        'index': i,
                        'score': float(score),
                        'data': df.iloc[i][numerical_cols].to_dict()
                    })
            
            return {
                'success': True,
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'total_points': len(data),
                'feature_importance': self._get_feature_importance(numerical_cols)
            }
            
        except Exception as e:
            self.logger.error(f"Error in multivariate anomaly detection: {str(e)}")
            return {
                'success': False,
                'error': f'Multivariate anomaly detection error: {str(e)}'
            }
    
    def detect_trend_anomalies(self, time_series_data: List[Dict[str, Any]], 
                             metric: str, 
                             window_size: int = 7) -> Dict[str, Any]:
        """Detect anomalies in time series trends using moving averages"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(time_series_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            if metric not in df.columns:
                return {
                    'success': False,
                    'error': f'Metric {metric} not found in data'
                }
            
            # Calculate moving average and standard deviation
            df['moving_avg'] = df[metric].rolling(window=window_size, min_periods=1).mean()
            df['moving_std'] = df[metric].rolling(window=window_size, min_periods=1).std()
            
            # Calculate z-scores
            df['z_score'] = abs(df[metric] - df['moving_avg']) / df['moving_std']
            
            # Identify trend anomalies (z-score > 3)
            anomalies = []
            for i, row in df.iterrows():
                if not pd.isna(row['z_score']) and row['z_score'] > 3:
                    anomalies.append({
                        'index': i,
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'value': float(row[metric]),
                        'moving_avg': float(row['moving_avg']),
                        'z_score': float(row['z_score'])
                    })
            
            return {
                'success': True,
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'total_points': len(df)
            }
            
        except Exception as e:
            self.logger.error(f"Error in trend anomaly detection: {str(e)}")
            return {
                'success': False,
                'error': f'Trend anomaly detection error: {str(e)}'
            }
    
    def _get_feature_importance(self, feature_names: List[str]) -> List[Dict[str, float]]:
        """Get feature importance from Isolation Forest"""
        if self.isolation_forest is None:
            return []
        
        # Note: IsolationForest doesn't have feature_importances_ attribute
        # We'll return equal importance for all features as a placeholder
        # In a real implementation, you might want to use permutation importance
        importance_value = 1.0 / len(feature_names) if len(feature_names) > 0 else 0
        
        feature_importance = [
            {'feature': name, 'importance': importance_value}
            for name in feature_names
        ]
        
        return feature_importance


def main():
    """Main function for testing the Anomaly Detection module"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create detector instance
    detector = AnomalyDetector()
    
    # Example usage
    print("Anomaly Detection module ready for integration")


if __name__ == "__main__":
    main()
