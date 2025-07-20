from flask import Blueprint, jsonify
from ai_services.analytics import PredictiveAnalytics

dashboard_bp = Blueprint('dashboard', __name__)

class SmartDashboard:
    def __init__(self):
        self.analytics = PredictiveAnalytics()
        
    @dashboard_bp.route('/api/dashboard/widgets')
    async def get_smart_widgets():
        user_role = get_current_user_role()
        time_context = get_time_context()
        
        # AI-powered widget prioritization
        widgets = await self.analytics.get_priority_widgets(
            role=user_role,
            time=time_context
        )
        
        return jsonify(widgets)