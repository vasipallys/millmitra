"""
AI Vision Testing Suite
Comprehensive tests for the enhanced computer vision module
"""

import unittest
import sys
import os
import base64
import numpy as np
import cv2

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from ai.enhanced_vision import EnhancedVisionAnalyzer, PYTORCH_AVAILABLE
    VISION_MODULE_AVAILABLE = True
except ImportError:
    VISION_MODULE_AVAILABLE = False
    print("Warning: Enhanced vision module not available for testing")


class TestEnhancedVisionAnalyzer(unittest.TestCase):
    """Test suite for the enhanced vision analyzer"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test suite"""
        if VISION_MODULE_AVAILABLE:
            cls.analyzer = EnhancedVisionAnalyzer()
        else:
            cls.analyzer = None
    
    def setUp(self):
        """Set up test case"""
        if not VISION_MODULE_AVAILABLE:
            self.skipTest("Enhanced vision module not available")
    
    def test_vision_analyzer_initialization(self):
        """Test that the vision analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.quality_standards)
        
        # Check that models are properly initialized
        if PYTORCH_AVAILABLE:
            # When PyTorch is available, models may be None (if model files don't exist) but should not cause errors
            pass
        else:
            # When PyTorch is not available, models should be None
            self.assertIsNone(self.analyzer.quality_model)
            self.assertIsNone(self.analyzer.defect_model)
    
    def test_decode_image(self):
        """Test image decoding functionality"""
        # Create a simple test image (10x10 pixels, red)
        test_image = np.zeros((10, 10, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Convert to base64
        import cv2
        _, buffer = cv2.imencode('.jpg', test_image)
        image_data = base64.b64encode(buffer).decode('utf-8')
        
        # Test decoding
        decoded_image = self.analyzer._decode_image(image_data)
        self.assertIsNotNone(decoded_image)
        self.assertEqual(decoded_image.shape, (10, 10, 3))
    
    def test_traditional_defect_detection(self):
        """Test traditional defect detection functionality"""
        # Create a simple test image
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Convert to PIL
        from PIL import Image
        pil_image = Image.fromarray(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
        
        # Test defect detection
        defects = self.analyzer._traditional_defect_detection(pil_image)
        self.assertIsInstance(defects, dict)
        self.assertIn('total_defective', defects)
    
    def test_color_analysis(self):
        """Test color analysis functionality"""
        # Create a simple test image
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Test color analysis
        color_analysis = self.analyzer._enhanced_color_analysis(test_image)
        self.assertIsInstance(color_analysis, dict)
        self.assertIn('hue_mean', color_analysis)
        self.assertIn('saturation_mean', color_analysis)
        self.assertIn('value_mean', color_analysis)
    
    def test_size_distribution(self):
        """Test size distribution analysis"""
        # Create a simple test image with some shapes
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Add some shapes to create contours
        cv2.rectangle(test_image, (10, 10), (30, 30), (0, 255, 0), -1)
        cv2.circle(test_image, (70, 70), 15, (0, 255, 0), -1)
        
        # Test size distribution
        size_dist = self.analyzer._enhanced_size_distribution(test_image)
        self.assertIsInstance(size_dist, dict)
        self.assertIn('small_grains_percentage', size_dist)
    
    def test_foreign_matter_detection(self):
        """Test foreign matter detection"""
        # Create a simple test image
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Test foreign matter detection
        foreign_matter = self.analyzer._enhanced_foreign_matter_detection(test_image)
        self.assertIsInstance(foreign_matter, dict)
        self.assertIn('foreign_matter_percentage', foreign_matter)
    
    def test_moisture_estimation(self):
        """Test moisture estimation"""
        # Create a simple test image
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red channel
        
        # Test moisture estimation
        moisture = self.analyzer._enhanced_moisture_estimation(test_image)
        self.assertIsInstance(moisture, dict)
        self.assertIn('estimated_moisture_percentage', moisture)
    
    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation"""
        # Create mock analysis data
        mock_analysis = {
            'grain_analysis': {
                'broken_percentage': 2.0,
                'average_length': 6.5
            },
            'defect_detection': {
                'defect_percentage': 1.5
            },
            'color_analysis': {
                'color_uniformity': 90.0
            },
            'foreign_matter': {
                'cleanliness_score': 95.0
            },
            'moisture_estimation': {
                'estimated_moisture_percentage': 13.5
            }
        }
        
        # Test quality metrics calculation
        metrics = self.analyzer._calculate_enhanced_quality_metrics(mock_analysis, 'basmati')
        self.assertIsInstance(metrics, dict)
        self.assertIn('quality_score', metrics)
        self.assertIn('overall_grade', metrics)
    
    def test_recommendations_generation(self):
        """Test recommendations generation"""
        # Create mock analysis data with issues
        mock_analysis = {
            'grain_analysis': {
                'broken_percentage': 15.0  # High broken percentage
            },
            'moisture_estimation': {
                'estimated_moisture_percentage': 16.0  # High moisture
            },
            'foreign_matter': {
                'foreign_matter_percentage': 3.0  # High foreign matter
            },
            'color_analysis': {
                'color_uniformity': 70.0  # Low uniformity
            },
            'defect_detection': {
                'defect_percentage': 8.0  # High defects
            }
        }
        
        # Test recommendations generation
        recommendations = self.analyzer._generate_enhanced_recommendations(mock_analysis, 'basmati')
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check that all high priority issues have recommendations
        high_priority_count = sum(1 for rec in recommendations if rec.get('priority') == 'high')
        self.assertGreaterEqual(high_priority_count, 3)  # Should have at least 3 high priority recommendations


class TestEnhancedVisionAPI(unittest.TestCase):
    """Test suite for the enhanced vision API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        if not VISION_MODULE_AVAILABLE:
            self.skipTest("Enhanced vision module not available")
            return
            
        from app import app
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/enhanced-vision/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('service', data)
        self.assertIn('vision_available', data)
        self.assertIn('status', data)
        self.assertEqual(data['service'], 'enhanced_vision_analysis')
    
    def test_analyze_image_endpoint_invalid_data(self):
        """Test the analyze image endpoint with invalid data"""
        # Test without data
        response = self.client.post('/api/enhanced-vision/analyze/image', 
                                  json={},
                                  headers={'Authorization': 'Bearer fake-token'})
        self.assertEqual(response.status_code, 400)
        
        # Test without image
        response = self.client.post('/api/enhanced-vision/analyze/image', 
                                  json={'variety': 'basmati'},
                                  headers={'Authorization': 'Bearer fake-token'})
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_batch_endpoint_invalid_data(self):
        """Test the analyze batch endpoint with invalid data"""
        # Test without data
        response = self.client.post('/api/enhanced-vision/analyze/batch', 
                                  json={},
                                  headers={'Authorization': 'Bearer fake-token'})
        self.assertEqual(response.status_code, 400)
        
        # Test without images
        response = self.client.post('/api/enhanced-vision/analyze/batch', 
                                  json={'variety': 'basmati'},
                                  headers={'Authorization': 'Bearer fake-token'})
        self.assertEqual(response.status_code, 400)


def create_test_suite():
    """Create and return the test suite"""
    suite = unittest.TestSuite()
    
    # Add vision analyzer tests
    suite.addTest(unittest.makeSuite(TestEnhancedVisionAnalyzer))
    
    # Add API tests
    suite.addTest(unittest.makeSuite(TestEnhancedVisionAPI))
    
    return suite


def main():
    """Run the AI vision test suite"""
    print("Running AI Vision Test Suite...")
    
    if not VISION_MODULE_AVAILABLE:
        print("Enhanced vision module not available, skipping tests")
        return
    
    # Create and run test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

if __name__ == '__main__':
    main()
