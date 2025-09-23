"""
FAISS Integration for Rice Mill Quality Control

This module implements similarity search for quality metrics using FAISS.
"""

import numpy as np
import faiss
import json
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path

class QualitySimilaritySearch:
    """FAISS-based similarity search for rice quality metrics"""
    
    def __init__(self, dimension: int = 128):
        """Initialize FAISS index"""
        self.dimension = dimension
        # Use IndexIDMap2 which supports adding vectors with explicit IDs
        self.base_index = faiss.IndexFlatL2(dimension)
        self.index = faiss.IndexIDMap2(self.base_index)
        self.quality_data = {}  # Store metadata
        self.id_counter = 0
        
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize feature vectors to unit length"""
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return features / norms
    
    def add_quality_batch(self, quality_records: List[Dict]) -> List[int]:
        """Add batch of quality records to the index"""
        if not quality_records:
            return []
        
        # Convert quality records to feature vectors
        feature_vectors = []
        ids = []
        
        for record in quality_records:
            # Convert quality metrics to feature vector
            vector = self._quality_to_vector(record)
            feature_vectors.append(vector)
            
            # Store metadata
            record_id = self.id_counter
            self.quality_data[record_id] = {
                'batch_id': record.get('batch_id'),
                'timestamp': record.get('timestamp', datetime.now().isoformat()),
                'quality_metrics': record.get('quality_metrics', {}),
                'grade': record.get('grade'),
                'source': record.get('source', 'unknown')
            }
            
            ids.append(record_id)
            self.id_counter += 1
        
        # Convert to numpy array
        vectors = np.array(feature_vectors).astype('float32')
        
        # Normalize vectors
        vectors = self._normalize_features(vectors)
        
        # Add to index with IDs
        ids_array = np.array(ids).astype('int64')
        self.index.add_with_ids(vectors, ids_array)
        
        return ids
    
    def _quality_to_vector(self, record: Dict) -> List[float]:
        """Convert quality record to feature vector"""
        metrics = record.get('quality_metrics', {})
        
        # Extract key quality metrics
        vector = [
            metrics.get('moisture_content', 0),
            metrics.get('broken_percentage', 0),
            metrics.get('foreign_matter', 0),
            metrics.get('chalky_kernels', 0),
            metrics.get('grain_length', 0),
            metrics.get('grain_width', 0),
            metrics.get('color_uniformity', 0),
            metrics.get('protein_content', 0),
            metrics.get('starch_content', 0),
            metrics.get('amylose_content', 0)
        ]
        
        # Add derived features
        # Quality score (normalized)
        vector.append(metrics.get('quality_score', 0) / 100.0)
        
        # Grade encoding (A+ = 5, A = 4, B = 3, C = 2, D = 1)
        grade_map = {'A+': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
        vector.append(grade_map.get(record.get('grade', 'D'), 1))
        
        # Pad to required dimension
        while len(vector) < self.dimension:
            vector.append(0.0)
        
        return vector[:self.dimension]
    
    def search_similar(self, query_record: Dict, k: int = 5) -> List[Dict]:
        """Find k most similar quality records"""
        if self.index.ntotal == 0:
            return []
        
        # Convert query to vector
        query_vector = np.array([self._quality_to_vector(query_record)]).astype('float32')
        query_vector = self._normalize_features(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1 and idx in self.quality_data:  # Valid result
                result = self.quality_data[idx].copy()
                result['similarity_distance'] = float(distance)
                result['similarity_score'] = 1.0 / (1.0 + float(distance))  # Convert distance to similarity
                result['rank'] = i + 1
                results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get index statistics"""
        return {
            'total_records': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': 'IndexFlatL2',
            'last_updated': datetime.now().isoformat()
        }
    
    def save_index(self, filepath: str) -> None:
        """Save FAISS index to disk"""
        faiss.write_index(self.index, filepath)
        
        # Save metadata
        metadata_path = filepath + '.metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump({
                'quality_data': self.quality_data,
                'id_counter': self.id_counter,
                'dimension': self.dimension
            }, f, indent=2)
    
    def load_index(self, filepath: str) -> None:
        """Load FAISS index from disk"""
        self.index = faiss.read_index(filepath)
        
        # Load metadata
        metadata_path = filepath + '.metadata.json'
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.quality_data = metadata.get('quality_data', {})
                self.id_counter = metadata.get('id_counter', 0)
                self.dimension = metadata.get('dimension', 128)

def create_sample_quality_data() -> List[Dict]:
    """Create sample quality data for testing"""
    import random
    
    samples = []
    grades = ['A+', 'A', 'B', 'C', 'D']
    
    for i in range(100):
        sample = {
            'batch_id': f'BATCH_{i:04d}',
            'timestamp': datetime.now().isoformat(),
            'quality_metrics': {
                'moisture_content': random.uniform(10, 15),
                'broken_percentage': random.uniform(0, 8),
                'foreign_matter': random.uniform(0, 2),
                'chalky_kernels': random.uniform(0, 5),
                'grain_length': random.uniform(5.0, 7.0),
                'grain_width': random.uniform(2.0, 3.0),
                'color_uniformity': random.uniform(80, 100),
                'protein_content': random.uniform(6, 10),
                'starch_content': random.uniform(85, 95),
                'amylose_content': random.uniform(15, 25),
                'quality_score': random.uniform(70, 100)
            },
            'grade': random.choice(grades),
            'source': 'production_line_1'
        }
        samples.append(sample)
    
    return samples

def main():
    """Test FAISS integration"""
    print("Testing FAISS Quality Similarity Search...")
    
    # Create search engine
    search_engine = QualitySimilaritySearch(dimension=12)
    
    # Generate sample data
    sample_data = create_sample_quality_data()
    
    # Add data to index
    print(f"Adding {len(sample_data)} quality records to index...")
    ids = search_engine.add_quality_batch(sample_data)
    print(f"Added {len(ids)} records with IDs: {ids[:5]}...")
    
    # Test search
    print("\nTesting similarity search...")
    query_record = sample_data[0]  # Use first record as query
    similar_records = search_engine.search_similar(query_record, k=3)
    
    print(f"Query record: {query_record['batch_id']} (Grade: {query_record['grade']})")
    print("\nTop 3 similar records:")
    for record in similar_records:
        print(f"  {record['rank']}. {record['batch_id']} (Grade: {record['grade']}) - "
              f"Distance: {record['similarity_distance']:.4f}, "
              f"Score: {record['similarity_score']:.4f}")
    
    # Show statistics
    stats = search_engine.get_statistics()
    print(f"\nIndex statistics: {stats}")
    
    # Save index
    index_path = "quality_index.faiss"
    search_engine.save_index(index_path)
    print(f"\nIndex saved to {index_path}")
    
    # Load index
    new_search_engine = QualitySimilaritySearch(dimension=12)
    new_search_engine.load_index(index_path)
    print(f"\nIndex loaded from {index_path}")
    
    # Verify loaded index
    loaded_stats = new_search_engine.get_statistics()
    print(f"Loaded index statistics: {loaded_stats}")

if __name__ == "__main__":
    main()
