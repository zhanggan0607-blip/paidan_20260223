import requests
import json

print("Checking available API endpoints...")
try:
    r = requests.get('http://localhost:8080/docs', timeout=5)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\nAvailable paths ({len(data.get('paths', {}))} total):")
        paths = list(data.get('paths', {}).keys())
        
        maintenance_plan_paths = [p for p in paths if 'maintenance' in p.lower()]
        print(f"\nMaintenance Plan paths ({len(maintenance_plan_paths)}):")
        for i, path in enumerate(maintenance_plan_paths, 1):
            print(f"  {i}. {path}")
            
        if len(maintenance_plan_paths) == 0:
            print("\n  No maintenance plan paths found!")
            print("\nAll paths:")
            for i, path in enumerate(paths[:20], 1):
                print(f"  {i}. {path}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
