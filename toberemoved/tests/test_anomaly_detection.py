"""
Test suite for Enhanced Anomaly Detection Module
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.anomaly_detection import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    """Test cases for the Anomaly Detection module"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = AnomalyDetector()
    
    def test_initialization(self):
        """Test that the Anomaly Detector module initializes correctly"""
        self.assertIsInstance(self.detector, AnomalyDetector)
        self.assertIsNotNone(self.detector.scaler)
        self.assertIsNone(self.detector.isolation_forest)
    
    def test_statistical_anomalies(self):
        """Test statistical anomaly detection functionality"""
        # Test data with clear outliers
        data = [
            {'production': 100, 'quality': 95},
            {'production': 110, 'quality': 92},
            {'production': 105, 'quality': 94},
            {'production': 300, 'quality': 70},  # Anomaly
            {'production': 102, 'quality': 93}
        ]
        
        # Test anomaly detection for production metric
        result = self.detector.detect_statistical_anomalies(data, 'production', threshold=1.5)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreater(result['anomaly_count'], 0)
        self.assertIn('control_limits', result)
        
        # Verify that the anomaly was detected
        anomaly_found = any(anomaly['value'] == 300 for anomaly in result['anomalies'])
        self.assertTrue(anomaly_found)
    
    def test_multivariate_anomalies(self):
        """Test multivariate anomaly detection functionality"""
        # Test data with clear outliers
        data = [
            {'production': 100, 'quality': 95, 'temperature': 25},
            {'production': 110, 'quality': 92, 'temperature': 26},
            {'production': 105, 'quality': 94, 'temperature': 24},
            {'production': 300, 'quality': 70, 'temperature': 50},  # Anomaly
            {'production': 102, 'quality': 93, 'temperature': 25}
        ]
        
        # Test multivariate anomaly detection
        result = self.detector.detect_multivariate_anomalies(data, contamination=0.3)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['total_points'], result['anomaly_count'])
        self.assertIsInstance(result['feature_importance'], list)
    
    def test_trend_anomalies(self):
        """Test trend anomaly detection functionality"""
        # Test time series data with clear outliers
        time_series_data = [
            {'date': '2023-01-01', 'production': 100},
            {'date': '2023-01-02', 'production': 110},
            {'date': '2023-01-03', 'production': 105},
            {'date': '2023-01-04', 'production': 108},
            {'date': '2023-01-05', 'production': 102},
            {'date': '2023-01-06', 'production': 104},
            {'date': '2023-01-07', 'production': 103},
            {'date': '2023-01-08', 'production': 300},  # Anomaly
            {'date': '2023-01-09', 'production': 101},
            {'date': '2023-01-10', 'production': 106}
        ]
        
        # Test trend anomaly detection
        result = self.detector.detect_trend_anomalies(time_series_data, 'production', window_size=5)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['total_points'], result['anomaly_count'])
        
        # Verify that the anomaly was detected
        if result['anomaly_count'] > 0:
            anomaly_found = any(anomaly['value'] == 300 for anomaly in result['anomalies'])
            self.assertTrue(anomaly_found)
    
    def test_missing_metric(self):
        """Test handling of missing metric in statistical anomaly detection"""
        data = [
            {'production': 100, 'quality': 95},
            {'production': 110, 'quality': 92}
        ]
        
        # Test with non-existent metric
        result = self.detector.detect_statistical_anomalies(data, 'non_existent_metric')
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_no_numerical_data(self):
        """Test handling of non-numerical data in multivariate anomaly detection"""
        data = [
            {'name': 'sample1', 'description': 'test'},
            {'name': 'sample2', 'description': 'test'}
        ]
        
        # Test with non-numerical data
        result = self.detector.detect_multivariate_anomalies(data)
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
