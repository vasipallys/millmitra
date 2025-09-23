#!/usr/bin/env python3
"""""
Test script for AI services enhancements
"""""

import asyncio
import sys
import os

# Handle Unicode encoding issues on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the ai-services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from core.ai_orchestrator import RiceMillAIOrchestrator
from analytics.predictive_analytics import PredictiveAnalytics

async def test_ai_orchestrator():
    """Test the enhanced AI orchestrator"""
    print("Testing AI Orchestrator Enhancements...")
    
    # Initialize orchestrator
    orchestrator = RiceMillAIOrchestrator()
    
    # Test enhanced natural language responses
    test_queries = [
        "Why is production low today?",
        "Show me today's status",
        "What are the best performing areas?",
        "Do we need maintenance on any equipment?",
        "What's our current inventory status?"
    ]
    
    context = {
        'active_batches': 3,
        'current_date': '2024-01-15',
        'user_role': 'manager'
    }
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await orchestrator.process_query(query, context)
        try:
            print(f"Response: {response}")
        except UnicodeEncodeError:
            print("Response: <Unicode content - see full response in logs>")
    
    # Test domain-specific agents
    print("\nTesting Domain-Specific Agents...")
    operations_agent = orchestrator.agents['operations']
    
    operations_queries = [
        "What's our current production status?",
        "How is quality control performing?",
        "What's our inventory situation?",
        "Are there any equipment issues?"
    ]
    
    for query in operations_queries:
        print(f"\nOperations Query: {query}")
        response = await operations_agent.process(query, context)
        try:
            print(f"Response: {response}")
        except UnicodeEncodeError:
            print("Response: <Unicode content - see full response in logs>")

async def test_predictive_analytics():
    """Test the enhanced predictive analytics"""
    print("\n\nTesting Predictive Analytics Enhancements...")
    
    analytics = PredictiveAnalytics()
    
    # Test enhanced demand prediction
    historical_data = [
        {'date': '2024-01-01', 'demand': 2500},
        {'date': '2024-01-02', 'demand': 2600},
        {'date': '2024-01-03', 'demand': 2400},
        {'date': '2024-01-04', 'demand': 2700},
        {'date': '2024-01-05', 'demand': 2800},
        {'date': '2024-01-06', 'demand': 2650},
        {'date': '2024-01-07', 'demand': 2750}
    ]
    
    print("\nTesting Demand Prediction...")
    demand_prediction = await analytics.predict_demand(historical_data, days_ahead=7)
    try:
        print(f"Demand Prediction: {demand_prediction}")
    except UnicodeEncodeError:
        print("Demand Prediction: <Unicode content - see full response in logs>")
    
    # Test enhanced maintenance prediction
    equipment_data = [
        {
            'id': 'mill_1',
            'runtime_hours': 450,
            'last_maintenance_hours': 0,
            'efficiency_rating': 92,
            'error_count': 2,
            'temperature': 65
        },
        {
            'id': 'mill_2',
            'runtime_hours': 520,
            'last_maintenance_hours': 0,
            'efficiency_rating': 75,
            'error_count': 8,
            'temperature': 75
        },
        {
            'id': 'packaging_line',
            'runtime_hours': 380,
            'last_maintenance_hours': 100,
            'efficiency_rating': 88,
            'error_count': 1,
            'temperature': 55
        }
    ]
    
    print("\nTesting Maintenance Prediction...")
    maintenance_prediction = await analytics.predict_maintenance(equipment_data)
    try:
        print(f"Maintenance Prediction: {maintenance_prediction}")
    except UnicodeEncodeError:
        print("Maintenance Prediction: <Unicode content - see full response in logs>")

async def main():
    """Main test function"""
    print("=" * 50)
    print("AI Services Enhancement Tests")
    print("=" * 50)
    
    try:
        await test_ai_orchestrator()
        await test_predictive_analytics()
        print("\n\nAll tests completed successfully!")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
