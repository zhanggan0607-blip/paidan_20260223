import requests
import json

print("Testing maintenance plan API...")
try:
    r = requests.get('http://localhost:8080/api/v1/maintenance-plan?page=0&size=10', timeout=5)
    print("Status:", r.status_code)
    
    if r.status_code == 200:
        response = r.json()
        print("Response:", json.dumps(response, indent=2, ensure_ascii=False))
        
        if response.get('code') == 200:
            data = response.get('data', {})
            total_elements = data.get('totalElements', 0)
            content = data.get('content', [])
            print("Total elements:", total_elements)
            print("Content length:", len(content))
        else:
            print("Error:", response.get('message'))
    else:
        print("HTTP Error:", r.status_code)
        
except Exception as e:
    print("Exception:", str(e))
    import traceback
    traceback.print_exc()
