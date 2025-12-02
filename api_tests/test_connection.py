import sys
print("Python version:", sys.version)
print("Testing imports...")

try:
    import requests
    print("✅ requests OK")
except ImportError as e:
    print("❌ requests ERROR:", e)

try:
    import csv
    print("✅ csv OK")
except ImportError as e:
    print("❌ csv ERROR:", e)

print("\nTesting API connection...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    print(f"✅ API Status: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except Exception as e:
    print(f"❌ API ERROR: {e}")
