import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.customer import Customer, CustomerInteraction
from models.sales import SalesOrder
import statistics
import re
from textblob import TextBlob

class AICustomerService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def validate_customer_data(self, customer_data: Dict):
        """AI validation of customer data"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Required fields validation
        required_fields = ['name', 'contact_person', 'phone', 'email']
        for field in required_fields:
            if not customer_data.get(field):
                validation['errors'].append(f'{field.replace("_", " ").title()} is required')
        
        # Email validation
        email = customer_data.get('email', '')
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            validation['errors'].append('Invalid email format')
        
        # Phone validation
        phone = customer_data.get('phone', '')
        if phone and not re.match(r'^[+]?[\d\s\-\(\)]{10,15}$', phone):
            validation['warnings'].append('Phone number format may be invalid')
        
        # Business validation
        business_type = customer_data.get('business_type', '')
        if not business_type:
            validation['warnings'].append('Business type not specified')
        
        # Credit limit validation
        credit_limit = customer_data.get('credit_limit', 0)
        if credit_limit > 10000000:  # 1 crore
            validation['warnings'].append('High credit limit - requires approval')
        
        validation['valid'] = len(validation['errors']) == 0
        return validation
    
    def predict_customer_segment(self, customer_data: Dict):
        """AI prediction of customer segment"""
        try:
            response = requests.post(f"{self.ai_service_url}/customer/predict-segment", json=customer_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_segment_prediction(customer_data)
    
    def assess_credit_worthiness(self, customer_data: Dict):
        """AI assessment of customer credit worthiness"""
        assessment = {
            'credit_score': 0,
            'risk_level': 'medium',
            'recommended_credit_limit': 0,
            'factors': [],
            'recommendations': []
        }
        
        # Base credit score
        base_score = 650
        
        # Business type factor
        business_type = customer_data.get('business_type', '').lower()
        if business_type in ['retailer', 'distributor', 'wholesaler']:
            base_score += 50
        elif business_type in ['restaurant', 'hotel']:
            base_score += 30
        
        # Annual revenue factor
        annual_revenue = customer_data.get('annual_revenue', 0)
        if annual_revenue > 50000000:  # 5 crore
            base_score += 100
        elif annual_revenue > 10000000:  # 1 crore
            base_score += 50
        elif annual_revenue > 1000000:  # 10 lakh
            base_score += 25
        
        # Years in business factor
        years_in_business = customer_data.get('years_in_business', 0)
        if years_in_business > 10:
            base_score += 75
        elif years_in_business > 5:
            base_score += 50
        elif years_in_business > 2:
            base_score += 25
        
        assessment['credit_score'] = min(850, max(300, base_score))
        
        # Risk level determination
        if assessment['credit_score'] >= 750:
            assessment['risk_level'] = 'low'
            assessment['recommended_credit_limit'] = annual_revenue * 0.1
        elif assessment['credit_score'] >= 650:
            assessment['risk_level'] = 'medium'
            assessment['recommended_credit_limit'] = annual_revenue * 0.05
        else:
            assessment['risk_level'] = 'high'
            assessment['recommended_credit_limit'] = annual_revenue * 0.02
        
        # Factors
        assessment['factors'] = [
            f"Business type: {business_type}",
            f"Annual revenue: ₹{annual_revenue:,}",
            f"Years in business: {years_in_business}"
        ]
        
        # Recommendations
        if assessment['risk_level'] == 'high':
            assessment['recommendations'] = [
                'Require advance payment',
                'Start with small orders',
                'Regular credit monitoring'
            ]
        
        return assessment
    
    def detect_duplicate_customer(self, customer_data: Dict):
        """AI detection of duplicate customers"""
        duplicate_check = {
            'is_duplicate': False,
            'confidence': 0.0,
            'similar_customers': [],
            'matching_criteria': []
        }
        
        # Simulate duplicate detection
        name = customer_data.get('name', '').lower()
        phone = customer_data.get('phone', '')
        email = customer_data.get('email', '').lower()
        
        # Simple simulation - in real implementation, this would query the database
        if 'test' in name or 'demo' in name:
            duplicate_check['is_duplicate'] = True
            duplicate_check['confidence'] = 0.85
            duplicate_check['similar_customers'] = [
                {
                    'id': 123,
                    'name': 'Test Customer Ltd',
                    'similarity_score': 0.85,
                    'matching_fields': ['name', 'phone']
                }
            ]
            duplicate_check['matching_criteria'] = ['Similar name pattern']
        
        return duplicate_check
    
    def enrich_customer_data(self, customer_data: Dict):
        """AI enrichment of customer data"""
        enriched_data = customer_data.copy()
        
        # Add AI-derived fields
        enriched_data['ai_enriched'] = True
        enriched_data['enrichment_timestamp'] = datetime.utcnow().isoformat()
        
        # Predict missing fields
        if not enriched_data.get('business_type'):
            name = enriched_data.get('name', '').lower()
            if any(word in name for word in ['hotel', 'restaurant', 'cafe']):
                enriched_data['predicted_business_type'] = 'restaurant'
            elif any(word in name for word in ['retail', 'store', 'shop']):
                enriched_data['predicted_business_type'] = 'retailer'
            else:
                enriched_data['predicted_business_type'] = 'distributor'
        
        # Add location insights
        city = enriched_data.get('city', '').lower()
        if city in ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata']:
            enriched_data['market_tier'] = 'tier_1'
        elif city in ['pune', 'hyderabad', 'ahmedabad', 'jaipur', 'lucknow']:
            enriched_data['market_tier'] = 'tier_2'
        else:
            enriched_data['market_tier'] = 'tier_3'
        
        return enriched_data
    
    def analyze_customer_profile(self, customer_data: Dict):
        """AI analysis of customer profile"""
        analysis = {
            'profile_completeness': 0.0,
            'engagement_potential': 'medium',
            'growth_potential': 'medium',
            'risk_factors': [],
            'opportunities': [],
            'recommendations': []
        }
        
        # Profile completeness
        required_fields = ['name', 'contact_person', 'phone', 'email', 'address', 'business_type']
        completed_fields = sum(1 for field in required_fields if customer_data.get(field))
        analysis['profile_completeness'] = completed_fields / len(required_fields)
        
        # Engagement potential
        if customer_data.get('annual_revenue', 0) > 10000000:
            analysis['engagement_potential'] = 'high'
        elif customer_data.get('annual_revenue', 0) < 1000000:
            analysis['engagement_potential'] = 'low'
        
        # Growth potential
        years_in_business = customer_data.get('years_in_business', 0)
        if years_in_business < 3:
            analysis['growth_potential'] = 'high'
            analysis['opportunities'].append('Young business with growth potential')
        
        # Risk factors
        if customer_data.get('credit_score', 650) < 600:
            analysis['risk_factors'].append('Low credit score')
        
        # Recommendations
        if analysis['profile_completeness'] < 0.8:
            analysis['recommendations'].append('Complete customer profile for better service')
        
        return analysis
    
    def analyze_interaction_history(self, customer_id: int):
        """AI analysis of customer interaction history"""
        analysis = {
            'interaction_frequency': 'medium',
            'sentiment_trend': 'neutral',
            'issue_resolution_rate': 0.85,
            'preferred_channels': [],
            'recent_interactions': [],
            'insights': []
        }
        
        # Simulate interaction analysis
        analysis['recent_interactions'] = [
            {
                'date': (datetime.now() - timedelta(days=5)).isoformat(),
                'type': 'phone_call',
                'subject': 'Order inquiry',
                'sentiment': 'positive',
                'status': 'resolved'
            },
            {
                'date': (datetime.now() - timedelta(days=12)).isoformat(),
                'type': 'email',
                'subject': 'Payment terms discussion',
                'sentiment': 'neutral',
                'status': 'resolved'
            }
        ]
        
        analysis['preferred_channels'] = ['phone', 'email']
        analysis['insights'] = [
            'Customer prefers phone communication',
            'Generally positive interaction sentiment',
            'Quick to resolve issues'
        ]
        
        return analysis
    
    def get_next_best_action(self, context: Dict):
        """AI recommendation for next best action"""
        customer = context.get('customer', {})
        interactions = context.get('recent_interactions', [])
        
        # Analyze recent interactions
        if interactions:
            # Check for unresolved issues
            open_issues = [i for i in interactions if i.get('status') == 'open']
            if open_issues:
                latest_issue = open_issues[0]
                return {
                    'action': 'resolve_issue',
                    'priority': 'high',
                    'title': 'Resolve Customer Issue',
                    'description': f"Open issue: {latest_issue.get('subject', 'Unknown')}",
                    'timeline': 'immediate',
                    'owner': 'customer_service',
                    'expected_outcome': 'improved_satisfaction'
                }
        
        # Check for upsell opportunities
        annual_revenue = customer.get('annual_revenue', 0)
        if annual_revenue > 5000000:  # 50 lakh
            return {
                'action': 'upsell_opportunity',
                'priority': 'medium',
                'title': 'Explore Premium Products',
                'description': 'Customer profile suggests potential for premium rice varieties',
                'timeline': 'within_week',
                'owner': 'sales_team',
                'expected_outcome': 'increased_revenue'
            }
        
        # Default action
        return {
            'action': 'relationship_building',
            'priority': 'low',
            'title': 'Schedule Relationship Call',
            'description': 'Regular check-in to maintain relationship',
            'timeline': 'within_month',
            'owner': 'account_manager',
            'expected_outcome': 'maintained_relationship'
        }
    
    def predict_customer_satisfaction(self, customer_data: Dict):
        """AI prediction of customer satisfaction"""
        prediction = {
            'satisfaction_score': 0.0,
            'confidence': 0.0,
            'factors': {},
            'improvement_areas': [],
            'recommendations': []
        }
        
        # Base satisfaction score
        base_score = 7.5  # out of 10
        
        # Factors affecting satisfaction
        factors = {}
        
        # Order fulfillment factor
        fulfillment_rate = customer_data.get('order_fulfillment_rate', 0.95)
        factors['order_fulfillment'] = fulfillment_rate
        base_score += (fulfillment_rate - 0.9) * 10
        
        # Response time factor
        avg_response_time = customer_data.get('avg_response_time_hours', 4)
        factors['response_time'] = avg_response_time
        if avg_response_time <= 2:
            base_score += 0.5
        elif avg_response_time > 8:
            base_score -= 0.5
        
        # Product quality factor
        quality_score = customer_data.get('product_quality_score', 8.0)
        factors['product_quality'] = quality_score
        base_score += (quality_score - 7.5) * 0.4
        
        prediction['satisfaction_score'] = max(1.0, min(10.0, base_score))
        prediction['confidence'] = 0.75
        prediction['factors'] = factors
        
        # Improvement areas
        if fulfillment_rate < 0.95:
            prediction['improvement_areas'].append('Order fulfillment reliability')
        
        if avg_response_time > 6:
            prediction['improvement_areas'].append('Response time to inquiries')
        
        # Recommendations
        if prediction['satisfaction_score'] < 7.0:
            prediction['recommendations'] = [
                'Immediate customer outreach required',
                'Review service delivery process',
                'Consider compensation for poor experience'
            ]
        
        return prediction
    
    def assess_churn_risk(self, customer_data: Dict):
        """AI assessment of customer churn risk"""
        risk_assessment = {
            'churn_probability': 0.0,
            'risk_level': 'low',
            'risk_factors': [],
            'retention_strategies': [],
            'timeline': 'low_risk'
        }
        
        # Calculate churn probability
        risk_score = 0.0
        
        # Order frequency factor
        days_since_last_order = customer_data.get('days_since_last_order', 30)
        if days_since_last_order > 90:
            risk_score += 0.3
            risk_assessment['risk_factors'].append('Long gap since last order')
        elif days_since_last_order > 60:
            risk_score += 0.15
        
        # Satisfaction factor
        satisfaction_score = customer_data.get('satisfaction_score', 7.5)
        if satisfaction_score < 6.0:
            risk_score += 0.4
            risk_assessment['risk_factors'].append('Low satisfaction score')
        elif satisfaction_score < 7.0:
            risk_score += 0.2
        
        # Payment behavior factor
        payment_delays = customer_data.get('payment_delays_count', 0)
        if payment_delays > 3:
            risk_score += 0.2
            risk_assessment['risk_factors'].append('Frequent payment delays')
        
        # Complaint factor
        unresolved_complaints = customer_data.get('unresolved_complaints', 0)
        if unresolved_complaints > 0:
            risk_score += 0.3
            risk_assessment['risk_factors'].append('Unresolved complaints')
        
        risk_assessment['churn_probability'] = min(0.95, risk_score)
        
        # Risk level determination
        if risk_assessment['churn_probability'] >= 0.7:
            risk_assessment['risk_level'] = 'high'
            risk_assessment['timeline'] = 'immediate_action_required'
            risk_assessment['retention_strategies'] = [
                'Immediate personal outreach',
                'Special pricing offer',
                'Service recovery plan',
                'Executive escalation'
            ]
        elif risk_assessment['churn_probability'] >= 0.4:
            risk_assessment['risk_level'] = 'medium'
            risk_assessment['timeline'] = 'action_within_week'
            risk_assessment['retention_strategies'] = [
                'Proactive customer check-in',
                'Service improvement plan',
                'Loyalty program enrollment'
            ]
        else:
            risk_assessment['retention_strategies'] = [
                'Regular relationship maintenance',
                'Upsell opportunities exploration'
            ]
        
        return risk_assessment
    
    def analyze_text_sentiment(self, text: str):
        """AI analysis of text sentiment"""
        if not text:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'score': 0.0}
        
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': abs(polarity),
                'score': polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'score': 0.0}
    
    def calculate_customer_lifetime_value(self, segment_id: Optional[int] = None):
        """AI calculation of customer lifetime value"""
        clv_analysis = {
            'average_clv': 0,
            'clv_distribution': {},
            'top_value_customers': [],
            'growth_potential': {},
            'recommendations': []
        }
        
        # Simulate CLV calculation
        base_clv = 2500000  # 25 lakh average
        
        clv_analysis['average_clv'] = base_clv
        
        # CLV distribution
        clv_analysis['clv_distribution'] = {
            'high_value': {'count': 50, 'avg_clv': base_clv * 3, 'percentage': 15},
            'medium_value': {'count': 150, 'avg_clv': base_clv, 'percentage': 45},
            'low_value': {'count': 133, 'avg_clv': base_clv * 0.4, 'percentage': 40}
        }
        
        # Top value customers (simulated)
        clv_analysis['top_value_customers'] = [
            {'customer_id': 101, 'name': 'Premium Rice Distributors', 'clv': base_clv * 5},
            {'customer_id': 102, 'name': 'Golden Grain Retailers', 'clv': base_clv * 4.2},
            {'customer_id': 103, 'name': 'Royal Foods Ltd', 'clv': base_clv * 3.8}
        ]
        
        # Growth potential
        clv_analysis['growth_potential'] = {
            'total_potential': base_clv * 1.3,
            'strategies': ['Premium product introduction', 'Service enhancement', 'Loyalty programs']
        }
        
        return clv_analysis
    
    def _fallback_segment_prediction(self, customer_data: Dict):
        """Fallback segment prediction when AI service is unavailable"""
        annual_revenue = customer_data.get('annual_revenue', 0)
        business_type = customer_data.get('business_type', '').lower()
        
        if annual_revenue > 50000000:  # 5 crore
            return {'segment': 'enterprise', 'confidence': 0.8}
        elif annual_revenue > 10000000:  # 1 crore
            return {'segment': 'large_business', 'confidence': 0.75}
        elif business_type in ['retailer', 'distributor']:
            return {'segment': 'commercial', 'confidence': 0.7}
        else:
            return {'segment': 'small_business', 'confidence': 0.65}
    
    def recommend_products(self, customer_data: Dict):
        """AI product recommendations for customer"""
        recommendations = []
        
        # Analyze customer profile
        business_type = customer_data.get('business_type', '').lower()
        annual_revenue = customer_data.get('annual_revenue', 0)
        location_tier = customer_data.get('market_tier', 'tier_3')
        
        # Premium products for high-revenue customers
        if annual_revenue > 10000000:
            recommendations.append({
                'product': 'Premium Basmati Rice',
                'reason': 'High-revenue customer suitable for premium products',
                'confidence': 0.85,
                'potential_revenue': 500000
            })
        
        # Location-based recommendations
        if location_tier == 'tier_1':
            recommendations.append({
                'product': 'Organic Rice Varieties',
                'reason': 'Tier-1 city customers prefer organic products',
                'confidence': 0.75,
                'potential_revenue': 300000
            })
        
        # Business type recommendations
        if business_type in ['restaurant', 'hotel']:
            recommendations.append({
                'product': 'Bulk Packaging Rice',
                'reason': 'Restaurant/hotel business requires bulk quantities',
                'confidence': 0.9,
                'potential_revenue': 750000
            })
        
        return recommendations
    
    def optimize_customer_journey(self, journey_analysis: Dict):
        """AI optimization of customer journey"""
        optimization = {
            'journey_improvements': [],
            'touchpoint_optimization': {},
            'automation_opportunities': [],
            'personalization_strategies': []
        }
        
        # Journey improvements
        optimization['journey_improvements'] = [
            'Streamline onboarding process',
            'Implement proactive communication',
            'Add self-service options',
            'Enhance mobile experience'
        ]
        
        # Touchpoint optimization
        optimization['touchpoint_optimization'] = {
            'initial_contact': 'Implement AI chatbot for instant response',
            'onboarding': 'Create digital onboarding workflow',
            'ongoing_service': 'Proactive issue detection and resolution',
            'renewal': 'Automated renewal reminders with incentives'
        }
        
        # Automation opportunities
        optimization['automation_opportunities'] = [
            'Automated order confirmations',
            'Proactive delivery notifications',
            'Automated satisfaction surveys',
            'Smart reorder suggestions'
        ]
        
        return optimization

