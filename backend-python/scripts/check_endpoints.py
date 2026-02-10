import requests

print("Checking available API endpoints...")
try:
    r = requests.get('http://localhost:8080/docs', timeout=5)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\nAvailable paths:")
        paths = list(data.get('paths', {}).keys())
        for i, path in enumerate(paths[:20], 1):
            print(f"  {i+1}. {path}")
        
        if len(paths) > 20:
            print(f"  ... and {len(paths) - 20} more")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
