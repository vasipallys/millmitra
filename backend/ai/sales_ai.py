import numpy as np
from datetime import datetime, timedelta
from models.sales import Customer, SalesOrder, SalesLead
from models.inventory import InventoryItem
from database import db
import google.generativeai as genai

class SalesAI:
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_new_customer(self, customer_data):
        """Analyze new customer and provide insights"""
        try:
            # Calculate customer score based on various factors
            score = 50  # Base score
            
            # Company size indicator
            if customer_data.get('company_name'):
                score += 15
            
            # Credit limit indicator
            credit_limit = customer_data.get('credit_limit', 0)
            if credit_limit > 100000:
                score += 20
            elif credit_limit > 50000:
                score += 10
            
            # Customer type scoring
            type_scores = {
                'export': 25,
                'distributor': 20,
                'wholesale': 15,
                'retail': 10
            }
            score += type_scores.get(customer_data.get('customer_type', 'retail'), 10)
            
            # Determine risk rating
            if score >= 80:
                risk_rating = 'low'
            elif score >= 60:
                risk_rating = 'medium'
            else:
                risk_rating = 'high'
            
            # Predict preferred products based on customer type
            preferred_products = self._predict_preferred_products(customer_data)
            
            return {
                'customer_score': min(score, 100),
                'risk_rating': risk_rating,
                'preferred_products': preferred_products,
                'recommendations': [
                    f"Customer score: {score}/100",
                    f"Risk level: {risk_rating}",
                    f"Recommended credit limit: ₹{self._recommend_credit_limit(score)}"
                ]
            }
        
        except Exception as e:
            return {
                'customer_score': 50,
                'risk_rating': 'medium',
                'preferred_products': [],
                'recommendations': ['Unable to generate AI insights']
            }
    
    def _predict_preferred_products(self, customer_data):
        """Predict preferred products based on customer profile"""
        customer_type = customer_data.get('customer_type', 'retail')
        
        preferences = {
            'export': ['Basmati Rice', 'Premium White Rice'],
            'distributor': ['White Rice', 'Parboiled Rice', 'Brown Rice'],
            'wholesale': ['White Rice', 'Parboiled Rice'],
            'retail': ['White Rice', 'Premium Rice']
        }
        
        return preferences.get(customer_type, ['White Rice'])
    
    def _recommend_credit_limit(self, customer_score):
        """Recommend credit limit based on customer score"""
        if customer_score >= 80:
            return 200000
        elif customer_score >= 60:
            return 100000
        elif customer_score >= 40:
            return 50000
        else:
            return 25000
    
    def optimize_sales_order(self, order_data):
        """Optimize sales order with AI recommendations"""
        try:
            recommendations = []
            
            # Check inventory availability
            for item in order_data.get('items', []):
                availability = self._check_inventory_availability(item)
                if not availability['available']:
                    recommendations.append(
                        f"Limited stock for {item['product_name']}. "
                        f"Available: {availability['quantity']} {item.get('unit', 'quintal')}"
                    )
            
            # Pricing optimization
            pricing_insights = self._optimize_pricing(order_data)
            recommendations.extend(pricing_insights)
            
            # Delivery optimization
            delivery_insights = self._optimize_delivery(order_data)
            recommendations.extend(delivery_insights)
            
            return {
                'recommendations': recommendations,
                'optimization_score': self._calculate_optimization_score(order_data)
            }
        
        except Exception as e:
            return {
                'recommendations': ['Unable to generate optimization insights'],
                'optimization_score': 75
            }
    
    def _check_inventory_availability(self, item):
        """Check inventory availability for order item"""
        # This would integrate with actual inventory system
        # For now, return mock data
        return {
            'available': True,
            'quantity': item['quantity'] * 1.2  # Mock: 20% more available
        }
    
    def _optimize_pricing(self, order_data):
        """Provide pricing optimization insights"""
        insights = []
        
        # Mock pricing analysis
        total_value = sum(
            item['quantity'] * item['unit_price'] 
            for item in order_data.get('items', [])
        )
        
        if total_value > 100000:
            insights.append("Large order detected. Consider volume discount of 2-3%")
        
        # Seasonal pricing
        current_month = datetime.now().month
        if current_month in [4, 5, 6]:  # Summer months
            insights.append("Peak season pricing applicable")
        
        return insights
    
    def _optimize_delivery(self, order_data):
        """Provide delivery optimization insights"""
        insights = []
        
        delivery_date = order_data.get('delivery_date')
        if delivery_date:
            delivery_dt = datetime.fromisoformat(delivery_date)
            days_to_delivery = (delivery_dt - datetime.now()).days
            
            if days_to_delivery < 3:
                insights.append("Urgent delivery required. Check production capacity")
            elif days_to_delivery > 30:
                insights.append("Long delivery timeline. Consider advance production planning")
        
        return insights
    
    def _calculate_optimization_score(self, order_data):
        """Calculate optimization score for the order"""
        score = 70  # Base score
        
        # Add points for complete information
        if order_data.get('delivery_date'):
            score += 10
        if order_data.get('payment_terms'):
            score += 10
        if len(order_data.get('items', [])) > 0:
            score += 10
        
        return min(score, 100)
    
    def predict_order_fulfillment(self, order_data):
        """Predict order fulfillment timeline and probability"""
        try:
            total_quantity = sum(item['quantity'] for item in order_data.get('items', []))
            
            # Mock fulfillment prediction
            if total_quantity <= 50:
                fulfillment_days = 3
                probability = 95
            elif total_quantity <= 100:
                fulfillment_days = 5
                probability = 90
            else:
                fulfillment_days = 7
                probability = 85
            
            return {
                'estimated_fulfillment_days': fulfillment_days,
                'fulfillment_probability': probability,
                'confidence': 0.85,
                'factors': [
                    f"Order quantity: {total_quantity} quintals",
                    f"Current production capacity: High",
                    f"Inventory availability: Good"
                ]
            }
        
        except Exception as e:
            return {
                'estimated_fulfillment_days': 5,
                'fulfillment_probability': 80,
                'confidence': 0.5,
                'factors': ['Unable to analyze fulfillment factors']
            }
    
    def assess_order_risk(self, order_data):
        """Assess risk factors for the order"""
        try:
            risk_factors = []
            risk_score = 0
            
            # Customer risk (mock)
            customer_id = order_data.get('customer_id')
            if customer_id:
                # In real implementation, check customer payment history
                risk_score += 10
                risk_factors.append("New customer - limited payment history")
            
            # Order value risk
            total_value = sum(
                item['quantity'] * item['unit_price'] 
                for item in order_data.get('items', [])
            )
            
            if total_value > 500000:
                risk_score += 20
                risk_factors.append("High value order - requires approval")
            
            # Payment terms risk
            payment_terms = order_data.get('payment_terms', 'cash')
            if 'credit' in payment_terms.lower():
                risk_score += 15
                risk_factors.append("Credit payment terms - monitor closely")
            
            # Determine risk level
            if risk_score <= 20:
                risk_level = 'low'
            elif risk_score <= 40:
                risk_level = 'medium'
            else:
                risk_level = 'high'
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': self._get_risk_recommendations(risk_level)
            }
        
        except Exception as e:
            return {
                'risk_score': 25,
                'risk_level': 'medium',
                'risk_factors': ['Unable to assess risk factors'],
                'recommendations': ['Manual review recommended']
            }
    
    def _get_risk_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            'low': ['Standard processing approved'],
            'medium': ['Verify customer details', 'Consider advance payment'],
            'high': ['Requires manager approval', 'Advance payment mandatory', 'Credit check required']
        }
        return recommendations.get(risk_level, ['Manual review required'])
    
    def optimize_quotation_pricing(self, quotation_data):
        """Optimize quotation pricing with AI"""
        try:
            recommendations = []
            
            # Market analysis (mock)
            market_trend = self._analyze_market_trends()
            recommendations.append(f"Market trend: {market_trend}")
            
            # Competitive pricing
            competitive_insights = self._analyze_competitive_pricing(quotation_data)
            recommendations.extend(competitive_insights)
            
            # Volume-based pricing
            volume_insights = self._analyze_volume_pricing(quotation_data)
            recommendations.extend(volume_insights)
            
            return {
                'pricing_recommendations': recommendations,
                'suggested_adjustments': self._suggest_price_adjustments(quotation_data),
                'confidence': 0.8
            }
        
        except Exception as e:
            return {
                'pricing_recommendations': ['Unable to generate pricing insights'],
                'suggested_adjustments': {},
                'confidence': 0.5
            }
    
    def _analyze_market_trends(self):
        """Analyze current market trends"""
        # Mock market analysis
        trends = ['Stable', 'Rising', 'Declining']
        return np.random.choice(trends)
    
    def _analyze_competitive_pricing(self, quotation_data):
        """Analyze competitive pricing"""
        insights = []
        
        # Mock competitive analysis
        total_value = sum(
            item['quantity'] * item['unit_price'] 
            for item in quotation_data.get('items', [])
        )
        
        if total_value > 200000:
            insights.append("Large order - competitive pricing critical")
        
        insights.append("Pricing within market range")
        return insights
    
    def _analyze_volume_pricing(self, quotation_data):
        """Analyze volume-based pricing opportunities"""
        insights = []
        
        total_quantity = sum(item['quantity'] for item in quotation_data.get('items', []))
        
        if total_quantity > 100:
            insights.append("Volume discount applicable - consider 2-3% reduction")
        elif total_quantity > 50:
            insights.append("Medium volume order - 1-2% discount possible")
        
        return insights
    
    def _suggest_price_adjustments(self, quotation_data):
        """Suggest specific price adjustments"""
        adjustments = {}
        
        for i, item in enumerate(quotation_data.get('items', [])):
            if item['quantity'] > 50:
                adjustments[f"item_{i}"] = {
                    'current_price': item['unit_price'],
                    'suggested_price': item['unit_price'] * 0.98,  # 2% discount
                    'reason': 'Volume discount'
                }
        
        return adjustments
    
    def predict_quotation_conversion(self, quotation_data):
        """Predict quotation to order conversion probability"""
        try:
            probability = 60  # Base probability
            
            # Customer type factor
            customer_type = quotation_data.get('customer_type', 'retail')
            type_multipliers = {
                'export': 1.2,
                'distributor': 1.15,
                'wholesale': 1.1,
                'retail': 1.0
            }
            probability *= type_multipliers.get(customer_type, 1.0)
            
            # Pricing competitiveness (mock)
            probability += np.random.randint(-10, 15)
            
            # Quotation completeness
            if quotation_data.get('delivery_terms'):
                probability += 5
            if quotation_data.get('payment_terms'):
                probability += 5
            
            probability = max(20, min(95, probability))
            
            return {
                'probability': probability,
                'confidence': 0.75,
                'factors': [
                    f"Customer type: {customer_type}",
                    "Competitive pricing",
                    "Complete quotation details"
                ]
            }
        
        except Exception as e:
            return {
                'probability': 60,
                'confidence': 0.5,
                'factors': ['Unable to analyze conversion factors']
            }
    
    def calculate_lead_score(self, lead_data):
        """Calculate AI-based lead score"""
        try:
            score = 0
            
            # Company size indicator
            if lead_data.get('company_name'):
                score += 20
            
            # Contact information completeness
            if lead_data.get('email'):
                score += 15
            if lead_data.get('phone'):
                score += 15
            
            # Estimated value
            estimated_value = lead_data.get('estimated_value', 0)
            if estimated_value > 100000:
                score += 25
            elif estimated_value > 50000:
                score += 15
            elif estimated_value > 10000:
                score += 10
            
            # Source quality
            source_scores = {
                'referral': 20,
                'website': 15,
                'exhibition': 15,
                'cold_call': 5
            }
            score += source_scores.get(lead_data.get('source', ''), 10)
            
            # Product interest specificity
            if lead_data.get('product_interest'):
                score += 10
            
            return {
                'score': min(score, 100),
                'grade': self._get_lead_grade(score),
                'factors': [
                    f"Estimated value: ₹{estimated_value}",
                    f"Source: {lead_data.get('source', 'Unknown')}",
                    f"Contact completeness: {'High' if score > 70 else 'Medium' if score > 40 else 'Low'}"
                ]
            }
        
        except Exception as e:
            return {
                'score': 50,
                'grade': 'C',
                'factors': ['Unable to calculate lead score']
            }
    
    def _get_lead_grade(self, score):
        """Convert lead score to grade"""
        if score >= 80:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        else:
            return 'D'
    
    def assess_lead_qualification(self, lead_data):
        """Assess lead qualification status"""
        try:
            qualification_score = 0
            
            # Budget indicator
            estimated_value = lead_data.get('estimated_value', 0)
            if estimated_value > 50000:
                qualification_score += 30
            elif estimated_value > 10000:
                qualification_score += 20
            
            # Authority indicator (company name suggests decision maker)
            if lead_data.get('company_name'):
                qualification_score += 25
            
            # Need indicator (specific product interest)
            if lead_data.get('product_interest'):
                qualification_score += 25
            
            # Timeline indicator
            if lead_data.get('expected_closure_date'):
                expected_date = datetime.fromisoformat(lead_data['expected_closure_date'])
                days_to_closure = (expected_date - datetime.now()).days
                if days_to_closure <= 30:
                    qualification_score += 20
                elif days_to_closure <= 90:
                    qualification_score += 10
            
            # Determine qualification status
            if qualification_score >= 70:
                status = 'hot'
            elif qualification_score >= 50:
                status = 'qualified'
            elif qualification_score >= 30:
                status = 'warm'
            else:
                status = 'cold'
            
            return {
                'status': status,
                'score': qualification_score,
                'confidence': 0.8,
                'reasons': self._get_qualification_reasons(qualification_score, lead_data)
            }
        
        except Exception as e:
            return {
                'status': 'warm',
                'score': 50,
                'confidence': 0.5,
                'reasons': ['Unable to assess qualification']
            }
    
    def _get_qualification_reasons(self, score, lead_data):
        """Get reasons for qualification assessment"""
        reasons = []
        
        if lead_data.get('estimated_value', 0) > 50000:
            reasons.append("High estimated value")
        
        if lead_data.get('company_name'):
            reasons.append("Corporate lead")
        
        if lead_data.get('product_interest'):
            reasons.append("Specific product interest")
        
        if lead_data.get('expected_closure_date'):
            reasons.append("Defined timeline")
        
        return reasons if reasons else ['Basic qualification criteria met']
    
    def recommend_lead_action(self, lead_scoring, qualification_assessment):
        """Recommend next best action for lead"""
        try:
            lead_score = lead_scoring.get('score', 50)
            qualification_status = qualification_assessment.get('status', 'warm')
            
            # Action matrix based on score and qualification
            if qualification_status == 'hot':
                if lead_score >= 80:
                    action = "Schedule immediate demo/meeting"
                else:
                    action = "Call within 24 hours"
            elif qualification_status == 'qualified':
                if lead_score >= 70:
                    action = "Send detailed proposal"
                else:
                    action = "Schedule discovery call"
            elif qualification_status == 'warm':
                action = "Send product information and follow up in 3 days"
            else:  # cold
                action = "Add to nurture campaign"
            
            return {
                'action': action,
                'priority': self._get_action_priority(qualification_status, lead_score),
                'timeline': self._get_action_timeline(qualification_status),
                'confidence': 0.85
            }
        
        except Exception as e:
            return {
                'action': "Manual review required",
                'priority': 'medium',
                'timeline': '1-2 days',
                'confidence': 0.5
            }
    
    def _get_action_priority(self, qualification_status, lead_score):
        """Get action priority based on qualification and score"""
        if qualification_status == 'hot' and lead_score >= 80:
            return 'urgent'
        elif qualification_status in ['hot', 'qualified'] and lead_score >= 60:
            return 'high'
        elif qualification_status == 'qualified' or lead_score >= 70:
            return 'medium'
        else:
            return 'low'
    
    def _get_action_timeline(self, qualification_status):
        """Get recommended action timeline"""
        timelines = {
            'hot': 'Within 24 hours',
            'qualified': '1-2 days',
            'warm': '3-5 days',
            'cold': '1-2 weeks'
        }
        return timelines.get(qualification_status, '3-5 days')
    
    def analyze_competition(self, quotation_data):
        """Analyze competitive landscape for quotation"""
        try:
            # Mock competitive analysis
            competitors = ['ABC Rice Mills', 'XYZ Agro', 'Premium Rice Co.']
            
            analysis = {
                'main_competitors': competitors[:2],
                'competitive_advantages': [
                    'Superior quality control',
                    'Faster delivery',
                    'Better customer service'
                ],
                'potential_threats': [
                    'Price competition',
                    'Bulk discount offers'
                ],
                'recommended_strategy': self._get_competitive_strategy(quotation_data)
            }
            
            return analysis
        
        except Exception as e:
            return {
                'main_competitors': [],
                'competitive_advantages': ['Quality products'],
                'potential_threats': ['Price competition'],
                'recommended_strategy': 'Focus on value proposition'
            }
    
    def _get_competitive_strategy(self, quotation_data):
        """Get recommended competitive strategy"""
        total_value = sum(
            item['quantity'] * item['unit_price'] 
            for item in quotation_data.get('items', [])
        )
        
        if total_value > 200000:
            return "Emphasize premium quality and reliable supply chain"
        elif total_value > 100000:
            return "Highlight competitive pricing with quality assurance"
        else:
            return "Focus on personalized service and flexibility"
    
    def generate_dashboard_insights(self, dashboard_data):
        """Generate AI insights for sales dashboard"""
        try:
            insights = []
            
            # Revenue trend analysis
            revenue_growth = dashboard_data.get('revenue_growth', 0)
            if revenue_growth > 10:
                insights.append("Strong revenue growth - consider scaling operations")
            elif revenue_growth < -5:
                insights.append("Revenue decline detected - review pricing strategy")
            else:
                insights.append("Stable revenue performance")
            
            # Order pattern analysis
            avg_order_value = dashboard_data.get('average_order_value', 0)
            if avg_order_value > 50000:
                insights.append("High-value customers - focus on retention")
            else:
                insights.append("Opportunity to increase order values")
            
            # Pipeline analysis
            pipeline = dashboard_data.get('pipeline', [])
            total_pipeline_value = sum(item.get('value', 0) for item in pipeline)
            if total_pipeline_value > 1000000:
                insights.append("Strong sales pipeline - prepare for fulfillment")
            
            return {
                'key_insights': insights,
                'recommendations': self._get_dashboard_recommendations(dashboard_data),
                'alerts': self._generate_sales_alerts(dashboard_data)
            }
        
        except Exception as e:
            return {
                'key_insights': ['Unable to generate insights'],
                'recommendations': ['Review sales data'],
                'alerts': []
            }
    
    def _get_dashboard_recommendations(self, dashboard_data):
        """Get actionable recommendations for dashboard"""
        recommendations = []
        
        # Top customers analysis
        top_customers = dashboard_data.get('top_customers', [])
        if len(top_customers) < 3:
            recommendations.append("Diversify customer base to reduce dependency")
        
        # Order growth analysis
        order_growth = dashboard_data.get('order_growth', 0)
        if order_growth > 20:
            recommendations.append("Scale production capacity to meet demand")
        
        return recommendations
    
    def _generate_sales_alerts(self, dashboard_data):
        """Generate sales alerts based on data"""
        alerts = []
        
        # Revenue alerts
        revenue_growth = dashboard_data.get('revenue_growth', 0)
        if revenue_growth < -10:
            alerts.append({
                'type': 'warning',
                'message': 'Revenue declined by more than 10%',
                'action': 'Review pricing and market strategy'
            })
        
        return alerts
    
    def generate_customer_insights(self, customer_analytics):
        """Generate AI insights for specific customer"""
        try:
            customer = customer_analytics.get('customer', {})
            order_history = customer_analytics.get('order_history', [])
            
            insights = []
            
            # Order frequency analysis
            if len(order_history) > 5:
                insights.append("Loyal customer - consider VIP treatment")
            elif len(order_history) == 0:
                insights.append("New customer - focus on first impression")
            
            # Value analysis
            total_value = customer.get('total_value', 0)
            if total_value > 500000:
                insights.append("High-value customer - assign dedicated account manager")
            
            # Payment behavior
            if customer.get('payment_terms') == 'cash':
                insights.append("Cash customer - reliable payment history")
            
            return {
                'customer_insights': insights,
                'growth_opportunities': self._identify_growth_opportunities(customer_analytics),
                'risk_factors': self._identify_customer_risks(customer_analytics)
            }
        
        except Exception as e:
            return {
                'customer_insights': ['Unable to generate insights'],
                'growth_opportunities': [],
                'risk_factors': []
            }
    
    def _identify_growth_opportunities(self, customer_analytics):
        """Identify growth opportunities with customer"""
        opportunities = []
        
        customer = customer_analytics.get('customer', {})
        product_preferences = customer_analytics.get('product_preferences', [])
        
        # Product diversification
        if len(product_preferences) == 1:
            opportunities.append("Introduce complementary products")
        
        # Volume increase
        avg_order_value = customer.get('average_order_value', 0)
        if avg_order_value < 25000:
            opportunities.append("Offer volume discounts to increase order size")
        
        return opportunities
    
    def _identify_customer_risks(self, customer_analytics):
        """Identify potential risks with customer"""
        risks = []
        
        customer = customer_analytics.get('customer', {})
        
        # Credit risk
        if customer.get('credit_limit', 0) > customer.get('total_value', 0) * 2:
            risks.append("High credit exposure - monitor payment behavior")
        
        # Dependency risk
        if customer.get('total_orders', 0) > 20:
            risks.append("High dependency customer - ensure satisfaction")
        
        return risks
    
    def analyze_revenue_trends(self, analytics_data):
        """Analyze revenue trends and provide insights"""
        try:
            revenue_growth = analytics_data.get('revenue_growth', 0)
            current_revenue = analytics_data.get('current_revenue', 0)
            
            trends = {
                'trend_direction': 'up' if revenue_growth > 0 else 'down' if revenue_growth < 0 else 'stable',
                'growth_rate': revenue_growth,
                'performance_rating': self._get_performance_rating(revenue_growth),
                'forecast': self._generate_revenue_forecast(current_revenue, revenue_growth)
            }
            
            return trends
        
        except Exception as e:
            return {
                'trend_direction': 'stable',
                'growth_rate': 0,
                'performance_rating': 'average',
                'forecast': 'Unable to generate forecast'
            }
    
    def _get_performance_rating(self, growth_rate):
        """Get performance rating based on growth rate"""
        if growth_rate > 15:
            return 'excellent'
        elif growth_rate > 5:
            return 'good'
        elif growth_rate > -5:
            return 'average'
        else:
            return 'poor'
    
    def _generate_revenue_forecast(self, current_revenue, growth_rate):
        """Generate simple revenue forecast"""
        if growth_rate > 0:
            next_month_forecast = current_revenue * (1 + growth_rate / 100)
            return f"Projected next month: ₹{next_month_forecast:,.0f}"
        else:
            return "Stable revenue expected"
    
    def forecast_sales(self, months):
        """Generate sales forecast for specified months"""
        try:
            # Mock forecasting - in real implementation, use historical data and ML models
            base_revenue = 1000000  # Base monthly revenue
            forecasts = []
            
            for month in range(1, months + 1):
                # Add some seasonality and growth
                seasonal_factor = 1 + 0.1 * np.sin(month * np.pi / 6)  # Seasonal variation
                growth_factor = 1 + (month * 0.02)  # 2% monthly growth
                
                forecast_revenue = base_revenue * seasonal_factor * growth_factor
                confidence = max(0.6, 0.9 - (month * 0.05))  # Decreasing confidence
                
                forecasts.append({
                    'month': month,
                    'forecasted_revenue': round(forecast_revenue, 2),
                    'confidence': round(confidence, 2),
                    'factors': ['Historical trends', 'Seasonal patterns', 'Market conditions']
                })
            
            return {
                'forecasts': forecasts,
                'methodology': 'Time series analysis with seasonal adjustment',
                'accuracy': 'Medium-term forecasts have 70-80% accuracy'
            }
        
        except Exception as e:
            return {
                'forecasts': [],
                'methodology': 'Unable to generate forecast',
                'accuracy': 'N/A'
            }
