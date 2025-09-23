"""
Enhanced NLP API Routes
Handles advanced conversational AI queries for the Rice Mill Management System
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

from models import User
from extensions import db
from ai.enhanced_nlp import EnhancedNLPProcessor

# Initialize the enhanced NLP processor
enhanced_nlp_processor = EnhancedNLPProcessor()

# Create blueprint
enhanced_nlp_bp = Blueprint('enhanced_nlp', __name__)

@enhanced_nlp_bp.route('/health', methods=['GET'])
@jwt_required()
def health_check():
    """Health check endpoint for enhanced NLP service"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced NLP Processor',
        'timestamp': datetime.now().isoformat()
    }), 200

@enhanced_nlp_bp.route('/process-query', methods=['POST'])
@jwt_required()
def process_enhanced_query():
    """Process natural language query with enhanced NLP"""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Prepare user context
        user_context = {
            'user_id': user_id,
            'user_role': user.role,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process the query with enhanced NLP
        result = enhanced_nlp_processor.process_query(query, user_context)
        
        # Add to database if successful
        if result['success']:
            # Log the interaction (in a real implementation, you might want to store this in a database)
            # For now, we'll just return the result
            pass
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@enhanced_nlp_bp.route('/query-suggestions', methods=['GET'])
@jwt_required()
def get_enhanced_query_suggestions():
    """Get enhanced suggested queries for the user"""
    suggestions = [
        "What is today's production status?",
        "Show me the quality report for the latest batch",
        "How is our financial performance this month?",
        "What is the current inventory level of paddy?",
        "When is the next maintenance scheduled for the huller?",
        "Are we compliant with all regulations?",
        "Generate a report on production trends",
        "How satisfied are our customers?",
        "What is scheduled for tomorrow?",
        "Why is the moisture content high in recent batches?",
        "Which production line is most efficient?",
        "What are the quality issues in batch B12345?",
        "How much revenue did we generate last week?",
        "Are there any pending customer orders?",
        "What is the head rice yield for jasmine rice?"
    ]
    
    return jsonify({
        'success': True,
        'suggestions': suggestions,
        'timestamp': datetime.now().isoformat()
    }), 200

@enhanced_nlp_bp.route('/entities', methods=['POST'])
@jwt_required()
def extract_entities():
    """Extract entities from text using enhanced NLP"""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Prepare user context
        user_context = {
            'user_id': user_id,
            'user_role': user.role,
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract entities
        entities = enhanced_nlp_processor._extract_entities(text.lower())
        
        return jsonify({
            'success': True,
            'text': text,
            'entities': entities,
            'count': len(entities),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@enhanced_nlp_bp.route('/intent', methods=['POST'])
@jwt_required()
def classify_intent():
    """Classify intent from text using enhanced NLP"""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Prepare user context
        user_context = {
            'user_id': user_id,
            'user_role': user.role,
            'timestamp': datetime.now().isoformat()
        }
        
        # Classify intent
        intent = enhanced_nlp_processor._classify_intent(text.lower())
        
        # Also get sentiment for context
        sentiment = enhanced_nlp_processor._analyze_sentiment(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'intent': intent,
            'sentiment': sentiment,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
