"""
AI Configuration Settings
Centralized configuration for AI services
"""

import os

class AIConfig:
    # AI Service URLs
    AI_SERVICE_BASE_URL = os.getenv('AI_SERVICE_URL', 'http://127.0.0.1:8000')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # AI Model Settings
    DEFAULT_MODEL = 'gemini-pro'
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    # Voice Processing
    VOICE_RECOGNITION_ENABLED = True
    VOICE_LANGUAGE = 'en-US'
    
    # Computer Vision
    VISION_MODEL_ENABLED = False
    QUALITY_ASSESSMENT_THRESHOLD = 0.8
    
    # Natural Language Processing
    NLP_ENABLED = True
    QUERY_TIMEOUT = 30
    
    @classmethod
    def is_ai_enabled(cls):
        """Check if AI services are properly configured"""
        return bool(cls.GEMINI_API_KEY or cls.OPENAI_API_KEY)
    
    @classmethod
    def get_active_model(cls):
        """Get the active AI model based on available API keys"""
        if cls.GEMINI_API_KEY:
            return 'gemini-pro'
        elif cls.OPENAI_API_KEY:
            return 'gpt-3.5-turbo'
        else:
            return None
