"""
Enhanced Predictive Analytics Module for Rice Mill Management System
Implements advanced forecasting and anomaly detection algorithms.
"""

import json
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from typing import Dict, Any, List, Tuple


class PredictiveAnalytics:
    """Enhanced Predictive Analytics for the Rice Mill Management System"""
    
    def __init__(self):
        """Initialize the Predictive Analytics module"""
        self.logger = logging.getLogger(__name__)
        self.production_model = None
        self.quality_model = None
        self.anomaly_detector = None
        self.logger.info("Predictive Analytics module initialized")
    
    def forecast_production(self, historical_data: List[Dict[str, Any]], 
                          periods: int = 30) -> Dict[str, Any]:
        """Forecast future production levels using time series analysis"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            
            # Extract production values
            production_series = df['production']
            
            # Seasonal decomposition
            decomposition = seasonal_decompose(production_series, model='additive', period=7)
            
            # Fit ARIMA model
            model = ARIMA(production_series, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            forecast = fitted_model.forecast(steps=periods)
            forecast_ci = fitted_model.get_forecast(steps=periods).conf_int()
            
            # Prepare results
            forecast_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), 
                                         periods=periods, freq='D')
            
            forecast_result = {
                'success': True,
                'forecast': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'production': float(production),
                        'lower_ci': float(lower),
                        'upper_ci': float(upper)
                    }
                    for date, production, (lower, upper) in 
                    zip(forecast_dates, forecast, forecast_ci.values)
                ],
                'trend': self._analyze_trend(decomposition.trend.dropna()),
                'seasonal_pattern': self._extract_seasonal_pattern(decomposition.seasonal)
            }
            
            return forecast_result
            
        except Exception as e:
            self.logger.error(f"Error in production forecasting: {str(e)}")
            return {
                'success': False,
                'error': f'Production forecasting error: {str(e)}'
            }
    
    def detect_anomalies(self, data: List[Dict[str, Any]], 
                        contamination: float = 0.1) -> Dict[str, Any]:
        """Detect anomalies in production or quality data"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Select numerical columns for anomaly detection
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) == 0:
                return {
                    'success': False,
                    'error': 'No numerical data found for anomaly detection'
                }
            
            # Prepare data for Isolation Forest
            X = df[numerical_cols].values
            
            # Fit Isolation Forest
            self.anomaly_detector = IsolationForest(contamination=contamination, 
                                                  random_state=42)
            anomaly_labels = self.anomaly_detector.fit_predict(X)
            
            # Calculate anomaly scores
            anomaly_scores = self.anomaly_detector.decision_function(X)
            
            # Identify anomalies
            anomalies = []
            for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly detected
                    anomalies.append({
                        'index': i,
                        'score': float(score),
                        'data': df.iloc[i].to_dict()
                    })
            
            return {
                'success': True,
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'total_points': len(data)
            }
            
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {str(e)}")
            return {
                'success': False,
                'error': f'Anomaly detection error: {str(e)}'
            }
    
    def quality_trend_analysis(self, quality_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality trends over time"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(quality_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate quality metrics
            if 'quality_score' in df.columns:
                # Linear trend analysis
                df['time_index'] = range(len(df))
                model = LinearRegression()
                model.fit(df[['time_index']], df['quality_score'])
                
                trend_slope = model.coef_[0]
                trend_direction = 'improving' if trend_slope > 0 else 'deteriorating' if trend_slope < 0 else 'stable'
                
                # Calculate recent average
                recent_avg = df['quality_score'].tail(7).mean()
                overall_avg = df['quality_score'].mean()
                
                return {
                    'success': True,
                    'trend_direction': trend_direction,
                    'trend_slope': float(trend_slope),
                    'recent_average': float(recent_avg),
                    'overall_average': float(overall_avg),
                    'data_points': len(df)
                }
            else:
                return {
                    'success': False,
                    'error': 'quality_score column not found in data'
                }
                
        except Exception as e:
            self.logger.error(f"Error in quality trend analysis: {str(e)}")
            return {
                'success': False,
                'error': f'Quality trend analysis error: {str(e)}'
            }
    
    def _analyze_trend(self, trend_series: pd.Series) -> str:
        """Analyze the trend direction from seasonal decomposition"""
        if len(trend_series) < 2:
            return 'insufficient_data'
        
        # Calculate slope using linear regression
        x = np.arange(len(trend_series)).reshape(-1, 1)
        y = trend_series.values.reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        
        slope = model.coef_[0][0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _extract_seasonal_pattern(self, seasonal_series: pd.Series) -> List[float]:
        """Extract seasonal pattern from seasonal decomposition"""
        # Get unique seasonal values (assuming weekly pattern)
        if len(seasonal_series) >= 7:
            pattern = seasonal_series.tail(7).tolist()
            return [float(x) for x in pattern]
        else:
            return [0.0] * 7


def main():
    """Main function for testing the Predictive Analytics module"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create analytics instance
    analytics = PredictiveAnalytics()
    
    # Example usage
    print("Predictive Analytics module ready for integration")


if __name__ == "__main__":
    main()
