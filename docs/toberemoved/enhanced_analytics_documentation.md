# Enhanced Analytics Documentation

## Overview
This document provides comprehensive documentation for the enhanced predictive analytics and anomaly detection modules implemented in the Rice Mill Management System. These modules provide advanced forecasting capabilities and real-time anomaly detection to improve operational efficiency and quality control.

## Predictive Analytics Module

### Module Location
`backend/ai/predictive_analytics.py`

### Key Features
1. **Production Forecasting**: Uses time series analysis with ARIMA models and seasonal decomposition to forecast future production levels.
2. **Anomaly Detection**: Implements Isolation Forest algorithm to detect anomalies in production or quality data.
3. **Quality Trend Analysis**: Analyzes quality trends over time using linear regression to determine improvement or deterioration patterns.

### API Reference

#### `PredictiveAnalytics()`
Initializes the Predictive Analytics module.

#### `forecast_production(historical_data, periods=30)`
Forecasts future production levels using time series analysis.

**Parameters:**
- `historical_data` (List[Dict[str, Any]]): Historical production data with date and production values.
- `periods` (int): Number of future periods to forecast (default: 30).

**Returns:**
- `Dict[str, Any]`: Forecast results including predicted values, confidence intervals, trend analysis, and seasonal patterns.

#### `detect_anomalies(data, contamination=0.1)`
Detects anomalies in production or quality data using Isolation Forest.

**Parameters:**
- `data` (List[Dict[str, Any]]): Data to analyze for anomalies.
- `contamination` (float): Expected proportion of anomalies in the data (default: 0.1).

**Returns:**
- `Dict[str, Any]`: Anomaly detection results including detected anomalies and their scores.

#### `quality_trend_analysis(quality_data)`
Analyzes quality trends over time.

**Parameters:**
- `quality_data` (List[Dict[str, Any]]): Historical quality data with dates and quality scores.

**Returns:**
- `Dict[str, Any]`: Trend analysis results including direction, slope, and averages.

### Dependencies
- pandas
- numpy
- scikit-learn
- statsmodels

## Anomaly Detection Module

### Module Location
`backend/ai/anomaly_detection.py`

### Key Features
1. **Statistical Process Control**: Detects anomalies using statistical process control (SPC) with control limits.
2. **Multivariate Analysis**: Uses Isolation Forest for multivariate anomaly detection.
3. **Trend Anomaly Detection**: Identifies anomalies in time series trends using moving averages.

### API Reference

#### `AnomalyDetector()`
Initializes the Anomaly Detector module.

#### `detect_statistical_anomalies(data, metric, threshold=3.0)`
Detects anomalies using statistical process control (SPC).

**Parameters:**
- `data` (List[Dict[str, Any]]): Data to analyze for anomalies.
- `metric` (str): The metric column to analyze for anomalies.
- `threshold` (float): Z-score threshold for anomaly detection (default: 3.0).

**Returns:**
- `Dict[str, Any]`: Anomaly detection results including detected anomalies and control limits.

#### `detect_multivariate_anomalies(data, contamination=0.1)`
Detects anomalies using multivariate analysis with Isolation Forest.

**Parameters:**
- `data` (List[Dict[str, Any]]): Data to analyze for anomalies.
- `contamination` (float): Expected proportion of anomalies in the data (default: 0.1).

**Returns:**
- `Dict[str, Any]`: Anomaly detection results including detected anomalies and feature importance.

#### `detect_trend_anomalies(time_series_data, metric, window_size=7)`
Detects anomalies in time series trends using moving averages.

**Parameters:**
- `time_series_data` (List[Dict[str, Any]]): Time series data with dates and metric values.
- `metric` (str): The metric column to analyze for trend anomalies.
- `window_size` (int): Window size for moving average calculation (default: 7).

**Returns:**
- `Dict[str, Any]`: Trend anomaly detection results including detected anomalies and z-scores.

### Dependencies
- pandas
- numpy
- scipy
- scikit-learn

## Integration with Multi-Agent Architecture

The predictive analytics and anomaly detection modules are designed to integrate seamlessly with the multi-agent AI architecture of the Rice Mill Management System. The Analytics Agent serves as the interface between these modules and the AI Coordinator.

### Integration Points
1. **AI Coordinator**: Routes analytics tasks to the Analytics Agent.
2. **Analytics Agent**: Processes analytics tasks using the predictive analytics and anomaly detection modules.
3. **Redis**: Used for communication between the AI Coordinator and Analytics Agent.

### Example Usage

#### Production Forecasting
```python
from ai.predictive_analytics import PredictiveAnalytics

# Initialize the module
analytics = PredictiveAnalytics()

# Historical production data
historical_data = [
    {'date': '2023-01-01', 'production': 100},
    {'date': '2023-01-02', 'production': 110},
    {'date': '2023-01-03', 'production': 120},
    # ... more data
]

# Forecast production for the next 30 days
forecast_result = analytics.forecast_production(historical_data, periods=30)
```

#### Anomaly Detection
```python
from ai.anomaly_detection import AnomalyDetector

# Initialize the module
detector = AnomalyDetector()

# Production data with potential anomalies
production_data = [
    {'date': '2023-01-01', 'production': 100, 'quality': 95},
    {'date': '2023-01-02', 'production': 110, 'quality': 92},
    {'date': '2023-01-03', 'production': 300, 'quality': 70},  # Anomaly
    # ... more data
]

# Detect anomalies
anomaly_result = detector.detect_multivariate_anomalies(production_data, contamination=0.1)
```

## Testing

Comprehensive test suites are provided for both modules:

1. **Predictive Analytics Tests**: `tests/test_predictive_analytics.py`
2. **Anomaly Detection Tests**: `tests/test_anomaly_detection.py`

All tests are passing and validate the functionality of the modules.

## Performance Considerations

1. **Data Preprocessing**: Both modules handle data preprocessing internally, but providing clean, well-structured data will improve performance.
2. **Computational Complexity**: Anomaly detection with Isolation Forest has O(n log n) complexity, which scales well for typical rice mill datasets.
3. **Memory Usage**: The modules are designed to be memory efficient, processing data in batches when possible.

## Troubleshooting

### Common Issues

1. **NumPy Compatibility**: Ensure NumPy version 1.24.3 is installed to avoid compatibility issues with pandas and other dependencies.
2. **Missing Data**: Both modules handle missing data gracefully, but results may be less accurate with significant missing data.
3. **Feature Importance**: The Isolation Forest in the anomaly detection module doesn't provide feature importances directly, so equal importance is assumed for all features.

### Error Handling

Both modules include comprehensive error handling with detailed error messages to help diagnose issues. All exceptions are logged using the Python logging module.

## Future Enhancements

1. **Advanced Forecasting Models**: Integration of more sophisticated forecasting models like LSTM neural networks.
2. **Real-time Anomaly Detection**: Implementation of streaming anomaly detection for real-time monitoring.
3. **Feature Importance Calculation**: Enhanced feature importance calculation for the Isolation Forest algorithm.
4. **External Factor Integration**: Incorporation of external factors like weather data and market prices into forecasting models.
