import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ricemill.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL') or 'http://ai-services:8000'