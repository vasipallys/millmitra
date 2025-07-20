from fastapi import APIRouter, HTTPException
from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
import json
from textblob import TextBlob
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

router = APIRouter()

class CustomerAI:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.scaler = StandardScaler()
    
    async def validate_customer_data(self, customer_data: Dict) -> Dict:
        """AI-powered customer data validation"""
        errors = []
        warnings = []
        recommendations = []
        confidence_score = 0.0
        
        # Name validation
        name = customer_data.get('name', '').strip()
        if not name:
            errors.append("Customer name is required")
        elif len(name) < 2:
            errors.append("Customer name too short")
        elif not re.match(r'^[a-zA-Z\s\.]+$', name):
            warnings.append("Name contains unusual characters")
        else:
            confidence_score += 0.2
        
        # Phone validation
        phone = customer_data.get('phone', '').strip()
        if not phone:
            errors.append("Phone number is required")
        elif not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
            errors.append("Invalid phone number format")
        else:
            confidence_score += 0.3
        
        # Email validation
        email = customer_data.get('email', '').strip()
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format")
            else:
                confidence_score += 0.2
        else:
            recommendations.append("Adding email improves communication options")
        
        # Business type validation
        business_type = customer_data.get('business_type', '')
        valid_types = ['retailer', 'wholesaler', 'distributor', 'restaurant', 'hotel']
        if business_type and business_type not in valid_types:
            warnings.append(f"Unusual business type: {business_type}")
        else:
            confidence_score += 0.1
        
        # Credit limit validation
        credit_limit = customer_data.get('credit_limit', 0)
        if credit_limit < 0:
            errors.append("Credit limit cannot be negative")
        elif credit_limit > 1000000:
            warnings.append("Very high credit limit - requires approval")
        else:
            confidence_score += 0.1
        
        # Address completeness
        address_fields = ['address', 'city', 'state', 'pincode']
        missing_address = [field for field in address_fields if not customer_data.get(field)]
        if missing_address:
            recommendations.append(f"Complete address helps with delivery: missing {', '.join(missing_address)}")
        else:
            confidence_score += 0.1
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'recommendations': recommendations,
            'confidence_score': min(confidence_score, 1.0),
            'data_quality': 'high' if confidence_score > 0.8 else 'medium' if confidence_score > 0.5 else 'low'
        }
    
    async def predict_customer_segment(self, customer_data: Dict) -> str:
        """Predict customer segment using AI"""
        # Feature extraction
        features = []
        
        # Business type scoring
        business_type = customer_data.get('business_type', 'retailer')
        business_scores = {
            'distributor': 0.9,
            'wholesaler': 0.7,
            'restaurant': 0.6,
            'hotel': 0.6,
            'retailer': 0.3
        }
        features.append(business_scores.get(business_type, 0.3))
        
        # Credit limit scoring
        credit_limit = customer_data.get('credit_limit', 0)
        credit_score = min(credit_limit / 100000, 1.0)  # Normalize to 0-1
        features.append(credit_score)
        
        # Location scoring (simplified)
        city = customer_data.get('city', '').lower()
        metro_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune']
        location_score = 0.8 if city in metro_cities else 0.4
        features.append(location_score)
        
        # Business name analysis
        business_name = customer_data.get('business_name', '').lower()
        premium_keywords = ['premium', 'deluxe', 'royal', 'grand', 'super', 'mega']
        name_score = 0.7 if any(keyword in business_name for keyword in premium_keywords) else 0.3
        features.append(name_score)
        
        # Calculate overall score
        overall_score = np.mean(features)
        
        # Segment prediction
        if overall_score > 0.7:
            return 'premium'
        elif overall_score > 0.4:
            return 'regular'
        else:
            return 'budget'
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of customer interaction"""
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'themes': [], 'confidence': 0.0}
        
        # Use TextBlob for sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine label
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Extract themes/keywords
        words = text.lower().split()
        # Filter for meaningful words
        themes = [word for word in words if len(word) > 3 and word.isalpha()]
        
        # Common rice mill themes
        domain_themes = []
        theme_keywords = {
            'quality': ['quality', 'grade', 'broken', 'moisture', 'purity'],
            'delivery': ['delivery', 'shipping', 'transport', 'delay', 'time'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'discount', 'rate'],
            'service': ['service', 'support', 'help', 'response', 'staff'],
            'product': ['rice', 'variety', 'basmati', 'jasmine', 'packaging']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                domain_themes.append(theme)
        
        return {
            'score': polarity,
            'label': label,
            'themes': domain_themes[:5],  # Top 5 themes
            'confidence': abs(polarity),
            'subjectivity': subjectivity,
            'word_count': len(words),
            'urgency_indicators': self._detect_urgency(text)
        }
    
    async def get_customer_insights(self, customers: List[Dict]) -> Dict:
        """Generate AI insights for customer list"""
        if not customers:
            return {'insights': [], 'patterns': [], 'recommendations': []}
        
        insights = []
        patterns = []
        recommendations = []
        
        # Segment analysis
        segments = {}
        total_value = 0
        high_value_count = 0
        
        for customer in customers:
            segment = customer.get('segment', 'unknown')
            segments[segment] = segments.get(segment, 0) + 1
            
            ltv = customer.get('lifetime_value', 0)
            total_value += ltv
            if ltv > 50000:
                high_value_count += 1
        
        avg_value = total_value / len(customers) if customers else 0
        
        # Generate insights
        insights.append(f"Analyzed {len(customers)} customers with average LTV of ₹{avg_value:.2f}")
        
        if segments:
            dominant_segment = max(segments, key=segments.get)
            insights.append(f"Dominant segment: {dominant_segment} ({segments[dominant_segment]} customers)")
        
        if high_value_count > 0:
            insights.append(f"{high_value_count} high-value customers (>₹50,000 LTV) identified")
        
        # Pattern detection
        if len(customers) > 10:
            patterns.append({
                'type': 'segmentation',
                'description': f'Customer base distributed across {len(segments)} segments',
                'confidence': 0.8
            })
        
        # Recommendations
        if high_value_count / len(customers) < 0.2:
            recommendations.append("Focus on customer value enhancement programs")
        
        if 'budget' in segments and segments['budget'] > len(customers) * 0.5:
            recommendations.append("Consider introducing entry-level products for budget segment")
        
        return {
            'insights': insights,
            'patterns': patterns,
            'recommendations': recommendations,
            'segment_distribution': segments,
            'value_metrics': {
                'average_ltv': avg_value,
                'high_value_percentage': (high_value_count / len(customers)) * 100
            }
        }
    
    async def get_customer_recommendations(self, customer_data: Dict) -> List[Dict]:
        """Get AI recommendations for specific customer"""
        recommendations = []
        
        segment = customer_data.get('segment', '')
        lifetime_value = customer_data.get('lifetime_value', 0)
        last_order_date = customer_data.get('last_order_date')
        total_orders = customer_data.get('total_orders', 0)
        avg_order_value = customer_data.get('avg_order_value', 0)
        
        # Inactivity check
        if last_order_date:
            try:
                last_order = datetime.fromisoformat(last_order_date.replace('Z', '+00:00'))
                days_since_order = (datetime.now() - last_order).days
                
                if days_since_order > 60:
                    recommendations.append({
                        'type': 'retention',
                        'priority': 'high',
                        'title': 'Customer Re-engagement',
                        'description': f'No orders in {days_since_order} days',
                        'action': 'Send personalized offer or make contact call',
                        'expected_impact': 'medium'
                    })
                elif days_since_order > 30:
                    recommendations.append({
                        'type': 'retention',
                        'priority': 'medium',
                        'title': 'Proactive Outreach',
                        'description': f'Customer inactive for {days_since_order} days',
                        'action': 'Check-in call to understand needs',
                        'expected_impact': 'low'
                    })
            except:
                pass
        
        # Value-based recommendations
        if lifetime_value > 100000:
            recommendations.append({
                'type': 'vip_treatment',
                'priority': 'medium',
                'title': 'VIP Customer Care',
                'description': 'High-value customer deserves special attention',
                'action': 'Assign dedicated account manager',
                'expected_impact': 'high'
            })
        
        if avg_order_value > 20000:
            recommendations.append({
                'type': 'upsell',
                'priority': 'medium',
                'title': 'Premium Product Opportunity',
                'description': 'Customer shows capacity for high-value purchases',
                'action': 'Introduce premium rice varieties',
                'expected_impact': 'medium'
            })
        
        # Frequency-based recommendations
        if total_orders > 20:
            recommendations.append({
                'type': 'loyalty',
                'priority': 'low',
                'title': 'Loyalty Program',
                'description': 'Frequent customer eligible for loyalty benefits',
                'action': 'Enroll in loyalty program with volume discounts',
                'expected_impact': 'medium'
            })
        
        # Segment-specific recommendations
        if segment == 'premium':
            recommendations.append({
                'type': 'cross_sell',
                'priority': 'medium',
                'title': 'Premium Services',
                'description': 'Premium customer may need additional services',
                'action': 'Offer custom packaging or delivery services',
                'expected_impact': 'medium'
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def get_next_best_action(self, context: Dict) -> Dict:
        """Get next best action for customer"""
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
            
            # Check sentiment of recent interactions
            negative_interactions = [i for i in interactions if i.get('sentiment_label') == 'negative']
            if negative_interactions:
                return {
                    'action': 'satisfaction_recovery',
                    'priority': 'high',
                    'title': 'Address Customer Concerns',
                    'description': 'Recent negative feedback detected',
                    'timeline': 'within_24_hours',
                    'owner': 'account_manager',
                    'expected_outcome': 'relationship_recovery'
                }
        
        # Check order history
        last_order_date = customer.get('last_order_date')
        if last_order_date:
            try:
                last_order = datetime.fromisoformat(last_order_date.replace('Z', '+00:00'))
                days_since_order = (datetime.now() - last_order).days
                
                if days_since_order > 45:
                    return {
                        'action': 'reactivation_campaign',
                        'priority': 'medium',
                        'title': 'Customer Reactivation',
                        'description': f'No orders in {days_since_order} days',
                        'timeline': 'this_week',
                        'owner': 'sales_team',
                        'expected_outcome': 'order_placement'
                    }
            except:
                pass
        
        # Default action for active customers
        return {
            'action': 'relationship_building',
            'priority': 'low',
            'title': 'Strengthen Relationship',
            'description': 'Regular check-in to identify opportunities',
            'timeline': 'this_month',
            'owner': 'account_manager',
            'expected_outcome': 'increased_loyalty'
        }
    
    async def intelligent_search(self, query: str) -> Dict:
        """AI-powered intelligent customer search"""
        # Enhanced search logic
        search_results = []
        search_type = 'exact_match'
        
        # Try different search strategies
        query_lower = query.lower().strip()
        
        # Phone number search
        if re.match(r'[\d\s\-\(\)]{8,}', query):
            search_type = 'phone_search'
            # This would query the database for phone matches
            
        # Email search
        elif '@' in query:
            search_type = 'email_search'
            
        # Business name search
        elif len(query) > 3:
            search_type = 'fuzzy_search'
            # Implement fuzzy matching logic
        
        return {
            'success': True,
            'customers': search_results,
            'search_type': search_type,
            'query_analysis': {
                'original_query': query,
                'processed_query': query_lower,
                'search_strategy': search_type,
                'confidence': 0.8
            },
            'suggestions': self._generate_search_suggestions(query)
        }
    
    def _detect_urgency(self, text: str) -> List[str]:
        """Detect urgency indicators in text"""
        urgency_keywords = [
            'urgent', 'asap', 'immediately', 'emergency', 'critical',
            'important', 'priority', 'rush', 'quick', 'fast'
        ]
        
        indicators = []
        text_lower = text.lower()
        
        for keyword in urgency_keywords:
            if keyword in text_lower:
                indicators.append(keyword)
        
        # Check for exclamation marks
        if '!' in text:
            indicators.append('exclamation_marks')
        
        # Check for capital letters (shouting)
        if len([c for c in text if c.isupper()]) > len(text) * 0.3:
            indicators.append('excessive_caps')
        
        return indicators
    
    def _generate_search_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        
        if query.isdigit():
            suggestions.append(f"Search by customer code: CUS{query.zfill(6)}")
            suggestions.append(f"Search by phone: {query}")
        
        if len(query) > 2:
            suggestions.append(f"Search business names containing: {query}")
            suggestions.append(f"Search contact persons: {query}")
        
        return suggestions

customer_ai = CustomerAI()

@router.post("/validate")
async def validate_customer_data(data: Dict):
    result = await customer_ai.validate_customer_data(data)
    return result

@router.post("/predict-segment")
async def predict_segment(data: Dict):
    segment = await customer_ai.predict_customer_segment(data)
    return {'predicted_segment': segment}

@router.post("/sentiment")
async def analyze_sentiment(data: Dict):
    text = data.get('text', '')
    result = await customer_ai.analyze_sentiment(text)
    return result

@router.post("/insights")
async def get_insights(data: Dict):
    customers = data.get('customers', [])
    result = await customer_ai.get_customer_insights(customers)
    return result

@router.post("/recommendations")
async def get_recommendations(data: Dict):
    recommendations = await customer_ai.get_customer_recommendations(data)
    return {'recommendations': recommendations}

@router.post("/next-best-action")
async def get_next_best_action(data: Dict):
    result = await customer_ai.get_next_best_action(data)
    return result

@router.post("/intelligent-search")
async def intelligent_search(data: Dict):
    query = data.get('query', '')
    result = await customer_ai.intelligent_search(query)
    return result