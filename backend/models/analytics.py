from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from extensions import db

class Dashboard(db.Model):
    __tablename__ = 'dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_name = db.Column(db.String(100), nullable=False)
    dashboard_type = db.Column(db.String(50), nullable=False)  # executive, operational, financial, etc.
    description = db.Column(db.Text)
    
    # Configuration
    layout_config = db.Column(JSON)  # Widget positions and sizes
    refresh_interval = db.Column(db.Integer, default=300)  # seconds
    is_public = db.Column(db.Boolean, default=False)
    
    # Access control
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    department = db.Column(db.String(50))
    access_roles = db.Column(JSON)  # List of roles that can access
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard")
    created_by_user = relationship("User")

class DashboardWidget(db.Model):
    __tablename__ = 'dashboard_widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    widget_name = db.Column(db.String(100), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # chart, table, kpi, gauge, etc.
    
    # Data source
    data_source = db.Column(db.String(100))  # SQL query, API endpoint, etc.
    query_config = db.Column(JSON)
    filters = db.Column(JSON)
    
    # Display configuration
    chart_config = db.Column(JSON)  # Chart.js or similar config
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=4)
    height = db.Column(db.Integer, default=3)
    
    # Refresh settings
    auto_refresh = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=300)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # financial, operational, compliance, etc.
    description = db.Column(db.Text)
    
    # Report configuration
    data_sources = db.Column(JSON)  # List of tables/views to include
    filters = db.Column(JSON)
    grouping = db.Column(JSON)
    sorting = db.Column(JSON)
    
    # Output format
    output_format = db.Column(db.String(20), default='pdf')  # pdf, excel, csv
    template_config = db.Column(JSON)
    
    # Scheduling
    is_scheduled = db.Column(db.Boolean, default=False)
    schedule_frequency = db.Column(db.String(20))  # daily, weekly, monthly
    schedule_config = db.Column(JSON)
    recipients = db.Column(JSON)  # Email list for scheduled reports
    
    # Access control
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)
    access_roles = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("ReportExecution", back_populates="report")
    created_by_user = relationship("User")

class ReportExecution(db.Model):
    __tablename__ = 'report_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    execution_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Execution details
    status = db.Column(db.String(20), default='running')  # running, completed, failed
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    execution_time = db.Column(db.Float)  # seconds
    
    # Results
    output_file_path = db.Column(db.String(255))
    record_count = db.Column(db.Integer)
    file_size = db.Column(db.Integer)  # bytes
    
    # Error handling
    error_message = db.Column(db.Text)
    
    # Execution context
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    execution_type = db.Column(db.String(20), default='manual')  # manual, scheduled
    parameters = db.Column(JSON)
    
    # Relationships
    report = relationship("Report", back_populates="executions")
    executed_by_user = relationship("User")

class KPI(db.Model):
    __tablename__ = 'kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_name = db.Column(db.String(100), nullable=False)
    kpi_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # financial, operational, quality, etc.
    
    # Calculation
    calculation_method = db.Column(db.String(50))  # sql, formula, api
    calculation_config = db.Column(JSON)
    unit_of_measure = db.Column(db.String(20))
    
    # Targets and thresholds
    target_value = db.Column(db.Float)
    warning_threshold = db.Column(db.Float)
    critical_threshold = db.Column(db.Float)
    
    # Display settings
    display_format = db.Column(db.String(20), default='number')  # number, percentage, currency
    decimal_places = db.Column(db.Integer, default=2)
    
    # Update frequency
    update_frequency = db.Column(db.String(20), default='daily')  # realtime, hourly, daily, weekly
    last_calculated = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    values = relationship("KPIValue", back_populates="kpi")
    created_by_user = relationship("User")

class KPIValue(db.Model):
    __tablename__ = 'kpi_values'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpis.id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    
    # Context
    period_type = db.Column(db.String(20))  # daily, weekly, monthly, quarterly, yearly
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    
    # Metadata
    data_source = db.Column(db.String(100))
    calculation_details = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    kpi = relationship("KPI", back_populates="values")

class DataAlert(db.Model):
    __tablename__ = 'data_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_name = db.Column(db.String(100), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # threshold, anomaly, trend
    description = db.Column(db.Text)
    
    # Trigger conditions
    data_source = db.Column(db.String(100))
    condition_config = db.Column(JSON)
    threshold_value = db.Column(db.Float)
    comparison_operator = db.Column(db.String(10))  # >, <, =, >=, <=, !=
    
    # Notification settings
    notification_channels = db.Column(JSON)  # email, sms, slack, etc.
    recipients = db.Column(JSON)
    message_template = db.Column(db.Text)
    
    # Frequency control
    check_frequency = db.Column(db.String(20), default='hourly')
    cooldown_period = db.Column(db.Integer, default=3600)  # seconds
    last_triggered = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    triggers = relationship("AlertTrigger", back_populates="alert")
    created_by_user = relationship("User")

class AlertTrigger(db.Model):
    __tablename__ = 'alert_triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('data_alerts.id'), nullable=False)
    trigger_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Trigger details
    trigger_value = db.Column(db.Float)
    threshold_exceeded = db.Column(db.Float)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Response
    notification_sent = db.Column(db.Boolean, default=False)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    # Context data
    context_data = db.Column(JSON)
    
    # Relationships
    alert = relationship("DataAlert", back_populates="triggers")
    acknowledged_by_user = relationship("User")