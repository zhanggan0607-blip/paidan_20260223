import requests
import json

print("Testing maintenance plan API...")
try:
    r = requests.get('http://localhost:8080/api/v1/maintenance-plan?page=0&size=10', timeout=5)
    print(f"Status: {r.status_code}")
    response = r.json()
    print(f"Response: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    if r.status_code == 200:
        print(f"Total elements: {response['data']['totalElements']}")
        print(f"Content length: {len(response['data']['content'])}")
    else:
        print(f"Error: {response}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
