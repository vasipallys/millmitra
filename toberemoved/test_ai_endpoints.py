import requests
import json

# Test health endpoint
print("Testing health endpoint...")
response = requests.get("http://localhost:8000/health")
print(f"Health check: {response.status_code} - {response.json()}")

# Test insights endpoint
print("\nTesting insights endpoint...")
data = {
    "data_type": "production",
    "data": {
        "days": 7,
        "current_date": "2024-01-15"
    }
}
response = requests.post("http://localhost:8000/generate-insights", json=data)
print(f"Insights endpoint: {response.status_code}")
if response.status_code == 200:
    insights = response.json()
    print(f"Number of insights: {len(insights.get('insights', []))}")
    if insights.get('insights'):
        print(f"First insight: {insights['insights'][0]['title']}")
else:
    print(f"Error: {response.text}")

# Test query endpoint
print("\nTesting query endpoint...")
query_data = {
    "query": "What is today's production status?",
    "context": {
        "user_id": "test_user",
        "timestamp": "2024-01-15T10:30:00Z",
        "active_batches": 3,
        "current_date": "2024-01-15"
    }
}
response = requests.post("http://localhost:8000/process-query", json=query_data)
print(f"Query endpoint: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Query response type: {type(result.get('response'))}")
else:
    print(f"Error: {response.text}")
