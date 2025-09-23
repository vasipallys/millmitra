"""
Test suite for Enhanced NLP Processor
"""

import unittest
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.enhanced_nlp import EnhancedNLPProcessor


class TestEnhancedNLPProcessor(unittest.TestCase):
    """Test cases for the Enhanced NLP Processor"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests"""
        cls.processor = EnhancedNLPProcessor()
        cls.user_context = {
            'user_id': 'test_user',
            'user_role': 'manager',
            'timestamp': datetime.now().isoformat()
        }
    
    def test_initialization(self):
        """Test that the processor initializes correctly"""
        self.assertIsInstance(self.processor, EnhancedNLPProcessor)
        self.assertIsNotNone(self.processor.query_patterns)
        self.assertIsNotNone(self.processor.domain_entities)
        self.assertIsNotNone(self.processor.response_templates)
        self.assertIsNotNone(self.processor.intent_categories)
        self.assertIsNotNone(self.processor.entity_types)
    
    def test_query_preprocessing(self):
        """Test query preprocessing functionality"""
        test_query = "What's the production status today?"
        processed = self.processor._preprocess_query(test_query)
        
        # Check that contractions are expanded
        self.assertNotIn("What's", processed)
        self.assertIn("what is", processed)
        
        # Check that query is lowercase and stripped
        self.assertEqual(processed, processed.lower().strip())
    
    def test_entity_extraction(self):
        """Test entity extraction functionality"""
        test_query = "What is the moisture content in batch B12345?"
        entities = self.processor._extract_entities(test_query)
        
        # Check that entities are extracted
        self.assertIsInstance(entities, list)
        
        # Check for specific entities
        entity_texts = [e['text'] for e in entities]
        self.assertIn('moisture content', entity_texts)
        self.assertIn('B12345', entity_texts)
    
    def test_intent_classification(self):
        """Test intent classification functionality"""
        test_query = "Why is production low today?"
        intent = self.processor._classify_intent(test_query)
        
        # Check that intent is classified
        self.assertIsInstance(intent, str)
        self.assertIn(intent, self.processor.intent_categories)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        test_query = "This is a great production day!"
        sentiment = self.processor._analyze_sentiment(test_query)
        
        # Check that sentiment is analyzed
        self.assertIsInstance(sentiment, dict)
        self.assertIn('label', sentiment)
        self.assertIn('score', sentiment)
    
    def test_production_query_processing(self):
        """Test processing of production-related queries"""
        query = "What is today's production status?"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_quality_query_processing(self):
        """Test processing of quality-related queries"""
        query = "Show me the quality report for batch B12345"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_financial_query_processing(self):
        """Test processing of financial-related queries"""
        query = "How is our financial performance this month?"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_inventory_query_processing(self):
        """Test processing of inventory-related queries"""
        query = "What is the current inventory level of paddy?"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_maintenance_query_processing(self):
        """Test processing of maintenance-related queries"""
        query = "When is the next maintenance scheduled for the huller?"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_compliance_query_processing(self):
        """Test processing of compliance-related queries"""
        query = "Are we compliant with all regulations?"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
        self.assertIn('data', result)
    
    def test_general_query_processing(self):
        """Test processing of general queries"""
        query = "Tell me about the rice mill"
        result = self.processor.process_query(query, self.user_context)
        
        # Check that query is processed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['original_query'], query)
        self.assertIn('intent', result)
        self.assertIn('response', result)
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        query = ""
        result = self.processor.process_query(query, self.user_context)
        
        # Empty query should be handled gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_response_templates(self):
        """Test that response templates are properly loaded"""
        templates = self.processor.response_templates
        
        # Check that all expected templates are present
        expected_templates = [
            'production_summary', 'quality_report', 'financial_summary',
            'inventory_status', 'maintenance_alert', 'compliance_status',
            'general_response'
        ]
        
        for template in expected_templates:
            self.assertIn(template, templates)
            self.assertIsInstance(templates[template], str)
    
    def test_domain_entities(self):
        """Test that domain entities are properly loaded"""
        entities = self.processor.domain_entities
        
        # Check that all expected entity types are present
        expected_entity_types = [
            'products', 'processes', 'equipment', 'metrics', 'locations'
        ]
        
        for entity_type in expected_entity_types:
            self.assertIn(entity_type, entities)
            self.assertIsInstance(entities[entity_type], list)
            self.assertGreater(len(entities[entity_type]), 0)


def run_tests():
    """Run all tests in this module"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedNLPProcessor)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
