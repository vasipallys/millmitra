"""
Test suite for Enhanced Predictive Analytics Module
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.predictive_analytics import PredictiveAnalytics


class TestPredictiveAnalytics(unittest.TestCase):
    """Test cases for the Predictive Analytics module"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analytics = PredictiveAnalytics()
    
    def test_initialization(self):
        """Test that the Predictive Analytics module initializes correctly"""
        self.assertIsInstance(self.analytics, PredictiveAnalytics)
        self.assertIsNone(self.analytics.production_model)
        self.assertIsNone(self.analytics.quality_model)
        self.assertIsNone(self.analytics.anomaly_detector)
    
    def test_forecast_production(self):
        """Test production forecasting functionality"""
        # Mock the ARIMA model
        with patch('ai.predictive_analytics.ARIMA') as mock_arima, \
             patch('ai.predictive_analytics.seasonal_decompose') as mock_decompose:
            
            # Mock seasonal decomposition
            mock_trend = MagicMock()
            mock_trend.dropna.return_value = pd.Series([1, 2, 3])
            mock_decompose.return_value.trend = mock_trend
            
            # Mock ARIMA model
            mock_fitted_model = MagicMock()
            mock_fitted_model.forecast.return_value = np.array([110, 115, 120])
            mock_conf_int = MagicMock()
            mock_conf_int.values = np.array([[100, 120], [105, 125], [110, 130]])
            mock_fitted_model.get_forecast.return_value.conf_int.return_value = mock_conf_int
            mock_arima.return_value.fit.return_value = mock_fitted_model
            
            # Test data
            historical_data = [
                {'date': '2023-01-01', 'production': 100},
                {'date': '2023-01-02', 'production': 110},
                {'date': '2023-01-03', 'production': 120}
            ]
            
            # Test forecast
            result = self.analytics.forecast_production(historical_data, periods=3)
            
            # Verify result
            self.assertTrue(result['success'])
            self.assertEqual(len(result['forecast']), 3)
            self.assertIn('trend', result)
            self.assertIn('seasonal_pattern', result)
    
    def test_detect_anomalies(self):
        """Test anomaly detection functionality"""
        # Test data
        data = [
            {'production': 100, 'quality': 95},
            {'production': 110, 'quality': 92},
            {'production': 105, 'quality': 94},
            {'production': 300, 'quality': 70},  # Anomaly
            {'production': 102, 'quality': 93}
        ]
        
        # Test anomaly detection
        result = self.analytics.detect_anomalies(data, contamination=0.2)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIsInstance(result['anomalies'], list)
        self.assertGreaterEqual(result['total_points'], result['anomaly_count'])
    
    def test_quality_trend_analysis(self):
        """Test quality trend analysis functionality"""
        # Test data
        quality_data = [
            {'date': '2023-01-01', 'quality_score': 90},
            {'date': '2023-01-02', 'quality_score': 92},
            {'date': '2023-01-03', 'quality_score': 94},
            {'date': '2023-01-04', 'quality_score': 96},
            {'date': '2023-01-05', 'quality_score': 98}
        ]
        
        # Test trend analysis
        result = self.analytics.quality_trend_analysis(quality_data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('trend_direction', result)
        self.assertIn('trend_slope', result)
        self.assertIn('recent_average', result)
        self.assertIn('overall_average', result)
    
    def test_analyze_trend(self):
        """Test internal trend analysis method"""
        # Test increasing trend
        trend_series = pd.Series([1, 2, 3, 4, 5])
        result = self.analytics._analyze_trend(trend_series)
        self.assertEqual(result, 'increasing')
        
        # Test decreasing trend
        trend_series = pd.Series([5, 4, 3, 2, 1])
        result = self.analytics._analyze_trend(trend_series)
        self.assertEqual(result, 'decreasing')
        
        # Test stable trend
        trend_series = pd.Series([3, 3, 3, 3, 3])
        result = self.analytics._analyze_trend(trend_series)
        self.assertEqual(result, 'stable')
    
    def test_extract_seasonal_pattern(self):
        """Test internal seasonal pattern extraction method"""
        # Test with sufficient data
        seasonal_series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = self.analytics._extract_seasonal_pattern(seasonal_series)
        self.assertEqual(len(result), 7)
        self.assertIsInstance(result, list)
        
        # Test with insufficient data
        seasonal_series = pd.Series([1, 2, 3])
        result = self.analytics._extract_seasonal_pattern(seasonal_series)
        self.assertEqual(len(result), 7)
        self.assertEqual(result, [0.0] * 7)


if __name__ == '__main__':
    unittest.main()
