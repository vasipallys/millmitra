import os

print("Environment variables related to database:")
for key, value in os.environ.items():
    if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper() or 'SQL' in key.upper():
        print(f"{key}: {value}")

print()
print("All environment variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")
