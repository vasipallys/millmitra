#!/usr/bin/env python3
"""
Production Monitoring Setup
===========================
"""

import os
import json
from pathlib import Path
from datetime import datetime

def create_health_check_endpoint():
    """Create enhanced health check configuration"""
    
    health_config = {
        "health_checks": {
            "database": {
                "enabled": True,
                "timeout": 5,
                "query": "SELECT 1"
            },
            "redis": {
                "enabled": True,
                "timeout": 3
            },
            "disk_space": {
                "enabled": True,
                "threshold_percent": 85
            },
            "memory": {
                "enabled": True,
                "threshold_percent": 90
            }
        },
        "monitoring": {
            "response_time_threshold": 2000,
            "error_rate_threshold": 0.05,
            "alert_email": "admin@ricemill.com"
        }
    }
    
    config_file = Path("config/monitoring.json")
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(health_config, f, indent=2)
    
    print(f"[SUCCESS] Monitoring configuration created: {config_file}")
    return config_file

def setup_log_rotation():
    """Set up log rotation configuration"""
    
    logrotate_config = """# Rice Mill Application Log Rotation
/path/to/rice_mill/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload rice-mill-backend
    endscript
}
"""
    
    print("[INFO] Log rotation configuration:")
    print(logrotate_config)
    print("Save this to /etc/logrotate.d/rice-mill")
    
    return logrotate_config

if __name__ == "__main__":
    print("[INFO] Setting up Production Monitoring")
    print("=" * 50)
    
    create_health_check_endpoint()
    setup_log_rotation()
    
    print("\n[INFO] Additional Monitoring Setup:")
    print("1. Configure Sentry for error tracking")
    print("2. Set up Prometheus/Grafana for metrics")
    print("3. Configure email alerts")
    print("4. Set up uptime monitoring")
