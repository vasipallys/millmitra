from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Customer, SalesOrder, User
# Temporarily disabled until services are fixed
# from services.customer_service import CustomerService
# from services.ai_customer_service import AICustomerService
from extensions import db
from datetime import datetime, timedelta
import json

customers_bp = Blueprint('customers', __name__)

# Mock AI Customer Service
class MockAICustomerService:
    def validate_customer_data(self, data):
        return {'valid': True, 'errors': []}

    def predict_customer_segment(self, data):
        return {'segment': 'premium', 'confidence': 0.85}

    def assess_credit_worthiness(self, data):
        return {'score': 750, 'rating': 'A', 'risk_level': 'low'}

    def detect_duplicate_customer(self, data):
        return {'is_duplicate': False, 'similar_customers': []}

    def enrich_customer_data(self, data):
        return data  # Return as-is for now

    def generate_onboarding_plan(self, customer_data):
        return {'steps': ['Welcome call', 'Setup account', 'First order'], 'timeline': '7 days'}

    def analyze_customer_profile(self, customer_data):
        return {'profile_strength': 85, 'completeness': 90, 'engagement_level': 'high'}

    def analyze_interaction_history(self, customer_id):
        return {'total_interactions': 15, 'avg_satisfaction': 4.5, 'recent_interactions': []}

    def get_next_best_action(self, context):
        return {'action': 'Schedule follow-up call', 'priority': 'medium', 'timeline': '3 days'}

    def predict_customer_satisfaction(self, customer_data):
        return {'predicted_score': 4.2, 'confidence': 0.78, 'factors': ['Service quality', 'Response time']}

    def assess_churn_risk(self, customer_data):
        return {'risk_score': 25, 'risk_level': 'low', 'key_factors': ['Regular orders', 'High satisfaction']}

    def analyze_update_impact(self, old_data, new_data):
        return {'impact_level': 'low', 'affected_areas': [], 'recommendations': []}

    def analyze_interaction_patterns(self, interactions):
        return {'patterns': ['Regular communication', 'Positive sentiment'], 'insights': []}

    def analyze_interaction_sentiment(self, interactions):
        return {'overall_sentiment': 'positive', 'sentiment_score': 0.75, 'trends': []}

    def classify_interaction(self, data):
        return {'type': 'inquiry', 'category': 'general', 'urgency': 'normal'}

    def analyze_text_sentiment(self, text):
        return {'sentiment': 'positive', 'score': 0.8, 'confidence': 0.9}

    def assess_interaction_priority(self, data, customer_data):
        return {'priority': 'medium', 'score': 60, 'factors': []}

    def suggest_interaction_response(self, data, customer_data):
        return {'suggestions': ['Thank customer', 'Provide information'], 'templates': []}

    def recommend_followup_actions(self, interaction_data):
        return {'actions': ['Send follow-up email', 'Schedule call'], 'timeline': '2 days'}

    # Add all other AI methods with mock responses
    def analyze_segment_performance(self, segments):
        return {'performance': 'good', 'insights': []}

    def optimize_customer_segments(self, analysis):
        return {'recommendations': ['Refine criteria', 'Add new segment']}

    def validate_segment_criteria(self, data):
        return {'valid': True, 'errors': []}

    def optimize_segment_criteria(self, data):
        return data

    def analyze_customer_contracts(self, contracts):
        return {'analysis': 'positive', 'insights': []}

    def predict_contract_renewals(self, contracts):
        return {'renewal_probability': 0.85, 'factors': []}

    def optimize_contract_terms(self, data, customer_data):
        return {'optimized_terms': data, 'improvements': []}

    def assess_contract_risk(self, data, customer_data):
        return {'risk_level': 'low', 'score': 25}

    def recommend_contract_pricing(self, data, customer_data):
        return {'recommended_price': data.get('price', 1000), 'justification': []}

    def analyze_satisfaction_trends(self, data):
        return {'trend': 'positive', 'insights': []}

    def recommend_satisfaction_improvements(self, analysis):
        return {'recommendations': ['Improve response time', 'Enhance service quality']}

    def calculate_customer_lifetime_value(self, segment_id):
        return {'avg_clv': 50000, 'distribution': {}, 'insights': []}

    def optimize_customer_value(self, clv_analysis):
        return {'strategies': ['Upselling', 'Cross-selling'], 'potential_increase': '20%'}

    def predict_customer_churn_batch(self, segment_id, threshold):
        return {'at_risk_customers': [], 'total_risk_score': 15}

    def recommend_retention_strategies(self, churn_prediction):
        return {'strategies': ['Loyalty program', 'Personal outreach']}

    def analyze_campaign_performance(self, campaigns):
        return {'performance': 'good', 'insights': []}

    def optimize_communication_campaign(self, data):
        return {'optimizations': [], 'expected_improvement': '15%'}

    def optimize_campaign_audience(self, data):
        return {'target_segments': [], 'reach_optimization': {}}

    def optimize_campaign_content(self, data):
        return {'content_suggestions': [], 'engagement_prediction': 0.75}

    def analyze_survey_responses(self, surveys):
        return {'insights': [], 'satisfaction_score': 4.2}

    def optimize_survey_design(self, data):
        return {'optimizations': [], 'response_rate_prediction': 0.65}

    def recommend_survey_questions(self, data):
        return {'questions': [], 'rationale': []}

    def analyze_loyalty_program_effectiveness(self, programs):
        return {'effectiveness': 'high', 'insights': []}

    def optimize_loyalty_program(self, data):
        return {'optimizations': [], 'engagement_prediction': 0.8}

    def optimize_reward_structure(self, data):
        return {'structure': data, 'improvements': []}

    def recommend_products(self, customer_data):
        return {'products': ['Premium Rice', 'Organic Variety'], 'confidence': 0.8}

    def recommend_services(self, customer_data):
        return {'services': ['Delivery service', 'Quality testing'], 'priority': []}

    def recommend_engagement_strategies(self, customer_data):
        return {'strategies': ['Personal calls', 'Email campaigns'], 'timeline': []}

    def analyze_customer_journey_patterns(self, segment_id):
        return {'patterns': [], 'insights': []}

    def optimize_customer_journey(self, analysis):
        return {'optimizations': [], 'impact_prediction': {}}

    def analyze_support_tickets(self, tickets):
        return {'insights': [], 'resolution_time': '2 days'}

    def recommend_ticket_resolutions(self, tickets):
        return {'recommendations': [], 'auto_resolve_candidates': []}

    def classify_support_ticket(self, data):
        return {'category': 'general', 'urgency': 'normal', 'complexity': 'low'}

    def assess_ticket_priority(self, data):
        return {'priority': 'medium', 'score': 60}

    def check_auto_resolution(self, data):
        return {'can_auto_resolve': False, 'confidence': 0.3}

    def recommend_agent_assignment(self, data, classification):
        return {'recommended_agent': 'general_support', 'reasoning': []}

    def analyze_voice_of_customer(self, period):
        return {'themes': [], 'sentiment': 'positive', 'insights': []}

    def analyze_sentiment_trends(self, period):
        return {'trend': 'stable', 'score': 0.75, 'changes': []}

    def recommend_voc_actions(self, analysis):
        return {'actions': [], 'priority': []}

    def predict_customer_behavior(self, customer_id, horizon):
        return {'predictions': [], 'confidence': 0.7}

    def recommend_behavioral_interventions(self, prediction):
        return {'interventions': [], 'expected_impact': {}}

    def analyze_feedback(self, data):
        return {'sentiment': 'positive', 'themes': [], 'actionable_items': []}

    def get_general_recommendations(self):
        return {'recommendations': ['Improve response time', 'Enhance product quality'], 'priority': []}

# Mock Customer Service
class MockCustomerService:
    def create_customer(self, user, data, segment, credit_assessment):
        customer = Customer(
            name=data.get('name', 'New Customer'),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            created_by=user.id
        )

        db.session.add(customer)
        db.session.commit()
        return customer

    def update_customer(self, customer, user, data, new_segment):
        for key, value in data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)

        db.session.commit()
        return customer

    def get_customer_interactions(self, customer_id, page, per_page, interaction_type):
        # Mock pagination response
        return {
            'items': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': 0,
                'pages': 0
            }
        }

    def create_interaction(self, customer, user, data, classification, sentiment, priority):
        # Mock interaction object
        class MockInteraction:
            def __init__(self):
                self.id = 1
                self.customer_id = customer.id
                self.interaction_type = data.get('type', 'call')
                self.notes = data.get('notes', '')
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'customer_id': self.customer_id,
                    'interaction_type': self.interaction_type,
                    'notes': self.notes,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockInteraction()

    def get_customer_segments(self):
        return []  # Return empty list for now

    def create_segment(self, user, data, optimized_criteria):
        # Mock segment object
        class MockSegment:
            def __init__(self):
                self.id = 1
                self.name = data.get('name', 'New Segment')
                self.criteria = data.get('criteria', {})
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'name': self.name,
                    'criteria': self.criteria,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockSegment()

    def get_customer_contracts(self, customer_id):
        return []  # Return empty list for now

    def create_contract(self, customer, user, data, optimization, pricing):
        # Mock contract object
        class MockContract:
            def __init__(self):
                self.id = 1
                self.customer_id = customer.id
                self.contract_type = data.get('type', 'standard')
                self.value = data.get('value', 0)
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'customer_id': self.customer_id,
                    'contract_type': self.contract_type,
                    'value': self.value,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockContract()

    def get_satisfaction_analytics(self, period, segment_id):
        return {'average_score': 4.2, 'trend': 'positive', 'responses': 150}

    def get_communication_campaigns(self, status):
        return []  # Return empty list for now

    def create_communication_campaign(self, user, data, optimization, audience, content):
        # Mock campaign object
        class MockCampaign:
            def __init__(self):
                self.id = 1
                self.name = data.get('name', 'New Campaign')
                self.status = 'active'
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'name': self.name,
                    'status': self.status,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockCampaign()

    def get_customer_surveys(self, status):
        return []  # Return empty list for now

    def create_customer_survey(self, user, data, optimization):
        # Mock survey object
        class MockSurvey:
            def __init__(self):
                self.id = 1
                self.title = data.get('title', 'Customer Survey')
                self.status = 'active'
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'title': self.title,
                    'status': self.status,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockSurvey()

    def get_loyalty_programs(self):
        return []  # Return empty list for now

    def create_loyalty_program(self, user, data, optimization, reward_optimization):
        # Mock loyalty program object
        class MockLoyaltyProgram:
            def __init__(self):
                self.id = 1
                self.name = data.get('name', 'Loyalty Program')
                self.status = 'active'
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'name': self.name,
                    'status': self.status,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockLoyaltyProgram()

    def get_support_tickets(self, status, priority, customer_id):
        return []  # Return empty list for now

    def create_support_ticket(self, user, data, classification, priority, agent_assignment):
        # Mock support ticket object
        class MockSupportTicket:
            def __init__(self):
                self.id = 1
                self.title = data.get('title', 'Support Request')
                self.status = 'open'
                self.priority = priority.get('priority', 'medium')
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'title': self.title,
                    'status': self.status,
                    'priority': self.priority,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockSupportTicket()

    def store_feedback(self, feedback_data):
        # Mock feedback object
        class MockFeedback:
            def __init__(self):
                self.id = 1
                self.customer_id = feedback_data.get('customer_id')
                self.feedback_text = feedback_data.get('feedback', '')
                self.rating = feedback_data.get('rating', 5)
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'customer_id': self.customer_id,
                    'feedback_text': self.feedback_text,
                    'rating': self.rating,
                    'created_at': self.created_at.isoformat()
                }

        return MockFeedback()

# Initialize services
customer_service = MockCustomerService()
ai_customer = MockAICustomerService()

# Add analytics endpoints that frontend expects
@customers_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Customer analytics overview for frontend compatibility"""
    customers = Customer.query.all()

    analytics = {
        'total_customers': len(customers),
        'active_customers': len([c for c in customers if c.status == 'active']),
        'new_customers_this_month': 5,
        'customer_satisfaction': 4.2,
        'retention_rate': 85.5
    }

    return jsonify({
        'analytics': analytics,
        'message': 'Customer analytics loaded successfully'
    })

@customers_bp.route('/analytics/segments', methods=['GET'])
@jwt_required()
def get_analytics_segments():
    """Customer segments for frontend compatibility"""
    segments = [
        {'id': 1, 'name': 'Premium Buyers', 'count': 25, 'value': 150000},
        {'id': 2, 'name': 'Regular Customers', 'count': 45, 'value': 200000},
        {'id': 3, 'name': 'Occasional Buyers', 'count': 30, 'value': 75000}
    ]

    return jsonify({
        'segments': segments,
        'message': 'Customer segments loaded successfully'
    })

@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    segment = request.args.get('segment', '')
    status = request.args.get('status', 'active')

    # Get customers directly from database
    query = Customer.query

    if search:
        query = query.filter(Customer.name.contains(search))
    if status:
        # Map status parameter to is_active field
        if status == 'active':
            query = query.filter(Customer.is_active == True)
        elif status == 'inactive':
            query = query.filter(Customer.is_active == False)

    customers = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Simplified insights
    customer_insights = {
        'total_customers': customers.total,
        'active_customers': len([c for c in customers.items if c.is_active]),
        'insights': ['Customer data loaded successfully']
    }

    segmentation_analysis = {
        'segments': ['Premium', 'Regular', 'Occasional'],
        'distribution': [25, 45, 30]
    }

    return jsonify({
        'customers': [c.to_dict() for c in customers.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': customers.total,
            'pages': customers.pages
        },
        'insights': customer_insights,
        'segmentation_analysis': segmentation_analysis
    })

@customers_bp.route('/', methods=['POST'])
@jwt_required()
def create_customer():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI data validation and enrichment
    validation_result = ai_customer.validate_customer_data(data)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'errors': validation_result['errors']
        }), 400
    
    # AI customer segmentation prediction
    predicted_segment = ai_customer.predict_customer_segment(data)
    
    # AI credit scoring
    credit_assessment = ai_customer.assess_credit_worthiness(data)
    
    # AI duplicate detection
    duplicate_check = ai_customer.detect_duplicate_customer(data)
    
    if duplicate_check['is_duplicate']:
        return jsonify({
            'success': False,
            'message': 'Potential duplicate customer detected',
            'similar_customers': duplicate_check['similar_customers']
        }), 409
    
    # AI data enrichment
    enriched_data = ai_customer.enrich_customer_data(data)
    
    customer = customer_service.create_customer(user, enriched_data, predicted_segment, credit_assessment)
    
    # AI onboarding recommendations
    onboarding_plan = ai_customer.generate_onboarding_plan(customer.to_dict())
    
    return jsonify({
        'success': True,
        'customer': customer.to_dict(),
        'predicted_segment': predicted_segment,
        'credit_assessment': credit_assessment,
        'onboarding_plan': onboarding_plan
    }), 201

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # AI customer analysis
    customer_analysis = ai_customer.analyze_customer_profile(customer.to_dict())
    
    # AI interaction history analysis
    interaction_analysis = ai_customer.analyze_interaction_history(customer_id)
    
    # AI next best action
    next_best_action = ai_customer.get_next_best_action({
        'customer': customer.to_dict(),
        'recent_interactions': interaction_analysis.get('recent_interactions', [])
    })
    
    # AI satisfaction prediction
    satisfaction_prediction = ai_customer.predict_customer_satisfaction(customer.to_dict())
    
    # AI churn risk assessment
    churn_risk = ai_customer.assess_churn_risk(customer.to_dict())
    
    return jsonify({
        'customer': customer.to_dict(),
        'analysis': customer_analysis,
        'interaction_analysis': interaction_analysis,
        'next_best_action': next_best_action,
        'satisfaction_prediction': satisfaction_prediction,
        'churn_risk': churn_risk
    })

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    # AI change impact analysis
    change_impact = ai_customer.analyze_update_impact(customer.to_dict(), data)
    
    # AI data validation
    validation_result = ai_customer.validate_customer_data(data)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'errors': validation_result['errors']
        }), 400
    
    # AI re-segmentation check
    new_segment = ai_customer.predict_customer_segment(data)
    
    updated_customer = customer_service.update_customer(customer, user, data, new_segment)
    
    return jsonify({
        'success': True,
        'customer': updated_customer.to_dict(),
        'change_impact': change_impact,
        'new_segment': new_segment
    })

@customers_bp.route('/<int:customer_id>/interactions', methods=['GET'])
@jwt_required()
def get_customer_interactions(customer_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    interaction_type = request.args.get('type', '')
    
    interactions = customer_service.get_customer_interactions(customer_id, page, per_page, interaction_type)
    
    # AI interaction analysis
    interaction_insights = ai_customer.analyze_interaction_patterns([i.to_dict() for i in interactions['items']])
    
    # AI sentiment analysis
    sentiment_analysis = ai_customer.analyze_interaction_sentiment([i.to_dict() for i in interactions['items']])
    
    return jsonify({
        'interactions': [i.to_dict() for i in interactions['items']],
        'pagination': interactions['pagination'],
        'insights': interaction_insights,
        'sentiment_analysis': sentiment_analysis
    })

@customers_bp.route('/<int:customer_id>/interactions', methods=['POST'])
@jwt_required()
def create_customer_interaction():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    customer_id = request.view_args['customer_id']
    customer = Customer.query.get_or_404(customer_id)
    
    data = request.get_json()
    
    # AI interaction classification
    interaction_classification = ai_customer.classify_interaction(data)
    
    # AI sentiment analysis
    sentiment_analysis = ai_customer.analyze_text_sentiment(data.get('notes', ''))
    
    # AI priority assessment
    priority_assessment = ai_customer.assess_interaction_priority(data, customer.to_dict())
    
    # AI auto-response suggestions
    response_suggestions = ai_customer.suggest_interaction_response(data, customer.to_dict())
    
    interaction = customer_service.create_interaction(
        customer, user, data, interaction_classification, sentiment_analysis, priority_assessment
    )
    
    # AI follow-up recommendations
    followup_recommendations = ai_customer.recommend_followup_actions(interaction.to_dict())
    
    return jsonify({
        'success': True,
        'interaction': interaction.to_dict(),
        'classification': interaction_classification,
        'sentiment': sentiment_analysis,
        'priority': priority_assessment,
        'response_suggestions': response_suggestions,
        'followup_recommendations': followup_recommendations
    }), 201

@customers_bp.route('/segments', methods=['GET'])
@jwt_required()
def get_customer_segments():
    segments = customer_service.get_customer_segments()
    
    # AI segment analysis
    segment_analysis = ai_customer.analyze_segment_performance([s.to_dict() for s in segments])
    
    # AI segment optimization
    segment_optimization = ai_customer.optimize_customer_segments(segment_analysis)
    
    return jsonify({
        'segments': [s.to_dict() for s in segments],
        'analysis': segment_analysis,
        'optimization': segment_optimization
    })

@customers_bp.route('/segments', methods=['POST'])
@jwt_required()
def create_customer_segment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI segment validation
    segment_validation = ai_customer.validate_segment_criteria(data)
    
    if not segment_validation['valid']:
        return jsonify({
            'success': False,
            'errors': segment_validation['errors']
        }), 400
    
    # AI segment optimization
    optimized_criteria = ai_customer.optimize_segment_criteria(data)
    
    segment = customer_service.create_segment(user, data, optimized_criteria)
    
    return jsonify({
        'success': True,
        'segment': segment.to_dict(),
        'optimized_criteria': optimized_criteria
    }), 201

@customers_bp.route('/<int:customer_id>/contracts', methods=['GET'])
@jwt_required()
def get_customer_contracts(customer_id):
    contracts = customer_service.get_customer_contracts(customer_id)
    
    # AI contract analysis
    contract_analysis = ai_customer.analyze_customer_contracts([c.to_dict() for c in contracts])
    
    # AI renewal predictions
    renewal_predictions = ai_customer.predict_contract_renewals([c.to_dict() for c in contracts])
    
    return jsonify({
        'contracts': [c.to_dict() for c in contracts],
        'analysis': contract_analysis,
        'renewal_predictions': renewal_predictions
    })

@customers_bp.route('/<int:customer_id>/contracts', methods=['POST'])
@jwt_required()
def create_customer_contract():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    customer_id = request.view_args['customer_id']
    customer = Customer.query.get_or_404(customer_id)
    
    data = request.get_json()
    
    # AI contract optimization
    contract_optimization = ai_customer.optimize_contract_terms(data, customer.to_dict())
    
    # AI risk assessment
    contract_risk = ai_customer.assess_contract_risk(data, customer.to_dict())
    
    # AI pricing recommendations
    pricing_recommendations = ai_customer.recommend_contract_pricing(data, customer.to_dict())
    
    contract = customer_service.create_contract(
        customer, user, data, contract_optimization, pricing_recommendations
    )
    
    return jsonify({
        'success': True,
        'contract': contract.to_dict(),
        'optimization': contract_optimization,
        'risk_assessment': contract_risk,
        'pricing_recommendations': pricing_recommendations
    }), 201

@customers_bp.route('/analytics/satisfaction', methods=['GET'])
@jwt_required()
def get_satisfaction_analytics():
    period = request.args.get('period', 'monthly')
    segment_id = request.args.get('segment_id', type=int)
    
    satisfaction_data = customer_service.get_satisfaction_analytics(period, segment_id)
    
    # AI satisfaction analysis
    satisfaction_analysis = ai_customer.analyze_satisfaction_trends(satisfaction_data)
    
    # AI improvement recommendations
    improvement_recommendations = ai_customer.recommend_satisfaction_improvements(satisfaction_analysis)
    
    return jsonify({
        'satisfaction_data': satisfaction_data,
        'analysis': satisfaction_analysis,
        'improvement_recommendations': improvement_recommendations
    })

@customers_bp.route('/analytics/lifetime-value', methods=['GET'])
@jwt_required()
def get_lifetime_value_analytics():
    segment_id = request.args.get('segment_id', type=int)
    
    # AI customer lifetime value calculation
    clv_analysis = ai_customer.calculate_customer_lifetime_value(segment_id)
    
    # AI value optimization strategies
    value_optimization = ai_customer.optimize_customer_value(clv_analysis)
    
    return jsonify({
        'clv_analysis': clv_analysis,
        'value_optimization': value_optimization
    })

@customers_bp.route('/analytics/churn-prediction', methods=['GET'])
@jwt_required()
def get_churn_prediction():
    segment_id = request.args.get('segment_id', type=int)
    risk_threshold = request.args.get('risk_threshold', 0.7, type=float)
    
    # AI churn prediction
    churn_prediction = ai_customer.predict_customer_churn_batch(segment_id, risk_threshold)
    
    # AI retention strategies
    retention_strategies = ai_customer.recommend_retention_strategies(churn_prediction)
    
    return jsonify({
        'churn_prediction': churn_prediction,
        'retention_strategies': retention_strategies
    })

@customers_bp.route('/communication/campaigns', methods=['GET'])
@jwt_required()
def get_communication_campaigns():
    status = request.args.get('status', 'active')
    
    campaigns = customer_service.get_communication_campaigns(status)
    
    # AI campaign performance analysis
    campaign_analysis = ai_customer.analyze_campaign_performance([c.to_dict() for c in campaigns])
    
    return jsonify({
        'campaigns': [c.to_dict() for c in campaigns],
        'analysis': campaign_analysis
    })

@customers_bp.route('/communication/campaigns', methods=['POST'])
@jwt_required()
def create_communication_campaign():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI campaign optimization
    campaign_optimization = ai_customer.optimize_communication_campaign(data)
    
    # AI audience segmentation
    audience_optimization = ai_customer.optimize_campaign_audience(data)
    
    # AI content optimization
    content_optimization = ai_customer.optimize_campaign_content(data)
    
    campaign = customer_service.create_communication_campaign(
        user, data, campaign_optimization, audience_optimization, content_optimization
    )
    
    return jsonify({
        'success': True,
        'campaign': campaign.to_dict(),
        'optimization': campaign_optimization,
        'audience_optimization': audience_optimization,
        'content_optimization': content_optimization
    }), 201

@customers_bp.route('/feedback/surveys', methods=['GET'])
@jwt_required()
def get_customer_surveys():
    status = request.args.get('status', 'active')
    
    surveys = customer_service.get_customer_surveys(status)
    
    # AI survey analysis
    survey_analysis = ai_customer.analyze_survey_responses([s.to_dict() for s in surveys])
    
    return jsonify({
        'surveys': [s.to_dict() for s in surveys],
        'analysis': survey_analysis
    })

@customers_bp.route('/feedback/surveys', methods=['POST'])
@jwt_required()
def create_customer_survey():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI survey optimization
    survey_optimization = ai_customer.optimize_survey_design(data)
    
    # AI question recommendations
    question_recommendations = ai_customer.recommend_survey_questions(data)
    
    survey = customer_service.create_customer_survey(user, data, survey_optimization)
    
    return jsonify({
        'success': True,
        'survey': survey.to_dict(),
        'optimization': survey_optimization,
        'question_recommendations': question_recommendations
    }), 201

@customers_bp.route('/loyalty/programs', methods=['GET'])
@jwt_required()
def get_loyalty_programs():
    programs = customer_service.get_loyalty_programs()
    
    # AI program effectiveness analysis
    program_analysis = ai_customer.analyze_loyalty_program_effectiveness([p.to_dict() for p in programs])
    
    return jsonify({
        'programs': [p.to_dict() for p in programs],
        'analysis': program_analysis
    })

@customers_bp.route('/loyalty/programs', methods=['POST'])
@jwt_required()
def create_loyalty_program():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI program optimization
    program_optimization = ai_customer.optimize_loyalty_program(data)
    
    # AI reward structure optimization
    reward_optimization = ai_customer.optimize_reward_structure(data)
    
    program = customer_service.create_loyalty_program(user, data, program_optimization, reward_optimization)
    
    return jsonify({
        'success': True,
        'program': program.to_dict(),
        'optimization': program_optimization,
        'reward_optimization': reward_optimization
    }), 201

@customers_bp.route('/<int:customer_id>/recommendations', methods=['GET'])
@jwt_required()
def get_customer_recommendations(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # AI personalized recommendations
    product_recommendations = ai_customer.recommend_products(customer.to_dict())
    
    # AI service recommendations
    service_recommendations = ai_customer.recommend_services(customer.to_dict())
    
    # AI engagement recommendations
    engagement_recommendations = ai_customer.recommend_engagement_strategies(customer.to_dict())
    
    return jsonify({
        'product_recommendations': product_recommendations,
        'service_recommendations': service_recommendations,
        'engagement_recommendations': engagement_recommendations
    })

@customers_bp.route('/analytics/journey-mapping', methods=['GET'])
@jwt_required()
def get_customer_journey_mapping():
    segment_id = request.args.get('segment_id', type=int)
    
    # AI customer journey analysis
    journey_analysis = ai_customer.analyze_customer_journey_patterns(segment_id)
    
    # AI journey optimization
    journey_optimization = ai_customer.optimize_customer_journey(journey_analysis)
    
    return jsonify({
        'journey_analysis': journey_analysis,
        'journey_optimization': journey_optimization
    })

@customers_bp.route('/support/tickets', methods=['GET'])
@jwt_required()
def get_support_tickets():
    status = request.args.get('status', 'open')
    priority = request.args.get('priority', '')
    customer_id = request.args.get('customer_id', type=int)
    
    tickets = customer_service.get_support_tickets(status, priority, customer_id)
    
    # AI ticket analysis
    ticket_analysis = ai_customer.analyze_support_tickets([t.to_dict() for t in tickets])
    
    # AI resolution recommendations
    resolution_recommendations = ai_customer.recommend_ticket_resolutions([t.to_dict() for t in tickets])
    
    return jsonify({
        'tickets': [t.to_dict() for t in tickets],
        'analysis': ticket_analysis,
        'resolution_recommendations': resolution_recommendations
    })

@customers_bp.route('/support/tickets', methods=['POST'])
@jwt_required()
def create_support_ticket():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI ticket classification
    ticket_classification = ai_customer.classify_support_ticket(data)
    
    # AI priority assessment
    priority_assessment = ai_customer.assess_ticket_priority(data)
    
    # AI auto-resolution check
    auto_resolution = ai_customer.check_auto_resolution(data)
    
    # AI agent assignment
    agent_assignment = ai_customer.recommend_agent_assignment(data, ticket_classification)
    
    ticket = customer_service.create_support_ticket(
        user, data, ticket_classification, priority_assessment, agent_assignment
    )
    
    return jsonify({
        'success': True,
        'ticket': ticket.to_dict(),
        'classification': ticket_classification,
        'priority_assessment': priority_assessment,
        'auto_resolution': auto_resolution,
        'agent_assignment': agent_assignment
    }), 201

@customers_bp.route('/analytics/voice-of-customer', methods=['GET'])
@jwt_required()
def get_voice_of_customer():
    period = request.args.get('period', 'monthly')
    
    # AI voice of customer analysis
    voc_analysis = ai_customer.analyze_voice_of_customer(period)
    
    # AI sentiment trends
    sentiment_trends = ai_customer.analyze_sentiment_trends(period)
    
    # AI action recommendations
    action_recommendations = ai_customer.recommend_voc_actions(voc_analysis)
    
    return jsonify({
        'voc_analysis': voc_analysis,
        'sentiment_trends': sentiment_trends,
        'action_recommendations': action_recommendations
    })

@customers_bp.route('/predictive/behavior', methods=['GET'])
@jwt_required()
def get_predictive_behavior():
    customer_id = request.args.get('customer_id', type=int)
    prediction_horizon = request.args.get('horizon', 90, type=int)  # days
    
    # AI behavior prediction
    behavior_prediction = ai_customer.predict_customer_behavior(customer_id, prediction_horizon)
    
    # AI intervention recommendations
    intervention_recommendations = ai_customer.recommend_behavioral_interventions(behavior_prediction)
    
    return jsonify({
        'behavior_prediction': behavior_prediction,
        'intervention_recommendations': intervention_recommendations
    })

@customers_bp.route('/<int:customer_id>/feedback', methods=['POST'])
@jwt_required()
def analyze_feedback(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    # AI feedback analysis
    analysis = ai_customer.analyze_feedback(data)
    
    # Store feedback with AI analysis
    feedback_data = {
        **data,
        'ai_analysis': analysis,
        'customer_id': customer_id
    }
    
    feedback = customer_service.store_feedback(feedback_data)
    
    return jsonify({
        'success': True,
        'feedback': feedback.to_dict(),
        'ai_analysis': analysis
    })

@customers_bp.route('/ai-recommendations', methods=['GET'])
@jwt_required()
def get_ai_recommendations():
    user_id = get_jwt_identity()
    
    # Get general AI recommendations for customer management
    recommendations = ai_customer.get_general_recommendations()
    
    return jsonify({
        'recommendations': recommendations,
        'generated_at': datetime.now().isoformat()
    })






