"""
Quality Similarity Search Routes
API endpoints for FAISS-based quality similarity search
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import sys
import os

# Add ai directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))

try:
    from faiss_quality_search import QualitySimilaritySearch
    FAISS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: FAISS not available: {e}")
    FAISS_AVAILABLE = False

quality_similarity_bp = Blueprint('quality_similarity', __name__)

# Initialize FAISS search engine
if FAISS_AVAILABLE:
    search_engine = QualitySimilaritySearch(dimension=12)
else:
    search_engine = None

@quality_similarity_bp.route('/similar-batches', methods=['POST'])
@jwt_required()
def find_similar_batches():
    """Find similar quality batches using FAISS"""
    if not FAISS_AVAILABLE:
        return jsonify({'error': 'FAISS similarity search not available'}), 501
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query_record = data.get('query_record')
        k = data.get('k', 5)
        
        if not query_record:
            return jsonify({'error': 'Query record is required'}), 400
        
        if k <= 0 or k > 100:
            return jsonify({'error': 'k must be between 1 and 100'}), 400
        
        # Search for similar batches
        similar_records = search_engine.search_similar(query_record, k)
        
        return jsonify({
            'success': True,
            'similar_batches': similar_records,
            'count': len(similar_records)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Similarity search failed: {str(e)}'}), 500

@quality_similarity_bp.route('/add-batches', methods=['POST'])
@jwt_required()
def add_quality_batches():
    """Add quality batches to FAISS index"""
    if not FAISS_AVAILABLE:
        return jsonify({'error': 'FAISS similarity search not available'}), 501
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        quality_records = data.get('quality_records')
        
        if not quality_records or not isinstance(quality_records, list):
            return jsonify({'error': 'Quality records list is required'}), 400
        
        # Add batches to index
        ids = search_engine.add_quality_batch(quality_records)
        
        return jsonify({
            'success': True,
            'added_count': len(ids),
            'message': f'Successfully added {len(ids)} quality records to index'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to add batches: {str(e)}'}), 500

@quality_similarity_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_index_statistics():
    """Get FAISS index statistics"""
    if not FAISS_AVAILABLE:
        return jsonify({'error': 'FAISS similarity search not available'}), 501
    
    try:
        stats = search_engine.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@quality_similarity_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for quality similarity service"""
    status = {
        'service': 'quality_similarity_search',
        'faiss_available': FAISS_AVAILABLE,
        'status': 'healthy' if FAISS_AVAILABLE else 'degraded'
    }
    
    if FAISS_AVAILABLE:
        try:
            stats = search_engine.get_statistics()
            status['index_stats'] = stats
        except Exception as e:
            status['status'] = 'degraded'
            status['error'] = str(e)
    
    return jsonify(status), 200
