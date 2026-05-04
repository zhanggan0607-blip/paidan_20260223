"""SSTCP - Security Deep Test v2 (with error handling)"""
import requests
import json
import sys

BASE = "https://www.paidan.sstcp.top"

def safe_request(method, url, **kwargs):
    kwargs.setdefault("timeout", 30)
    try:
        return getattr(requests, method)(url, **kwargs)
    except Exception as e:
        print(f"   [ERROR] {e}")
        return None

print("=== SSTCP Security Deep Test ===")
print()

print("1. Personnel endpoint without auth:")
resp = safe_request("get", f"{BASE}/api/v1/personnel")
if resp:
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            data = resp.json()
            items = data.get("data", {}).get("items", [])
            print(f"   Items count: {len(items)}")
            if items:
                print(f"   First item keys: {list(items[0].keys())}")
                print(f"   !! SECURITY ISSUE: Unauthenticated access to personnel data!")
            else:
                print(f"   Empty data returned - may be safe")
        except:
            print(f"   Response: {resp.text[:200]}")

print()
print("2. Swagger docs access:")
for path in ["/api/docs", "/api/redoc", "/api/openapi.json", "/docs", "/redoc"]:
    resp = safe_request("get", f"{BASE}{path}")
    if resp:
        print(f"   {path}: Status {resp.status_code}")
    else:
        print(f"   {path}: Request failed")

print()
print("3. Sensitive file access:")
for path in ["/.env", "/.git/config", "/.gitignore", "/.git/HEAD"]:
    resp = safe_request("get", f"{BASE}{path}", allow_redirects=False)
    if resp:
        ct = resp.headers.get("Content-Type", "N/A")
        print(f"   {path}: Status {resp.status_code}, Content-Type: {ct}")
        if resp.status_code == 200:
            content = resp.text[:300] if resp.text else "(empty)"
            is_html = "<!DOCTYPE" in content or "<html" in content.lower()
            if is_html:
                print(f"   -> SPA HTML page (not actual file)")
            else:
                print(f"   !! SENSITIVE FILE EXPOSED: {content[:100]}")
    else:
        print(f"   {path}: Request failed")

print()
print("4. Auth bypass tests:")
resp = safe_request("get", f"{BASE}/api/v1/personnel", headers={"Authorization": "Bearer "})
if resp:
    print(f"   Empty Bearer: Status {resp.status_code}")

resp = safe_request("get", f"{BASE}/api/v1/personnel", headers={"Authorization": "Bearer invalid"})
if resp:
    print(f"   Invalid Token: Status {resp.status_code}")

resp = safe_request("get", f"{BASE}/api/v1/personnel/1")
if resp:
    print(f"   Personnel detail (no auth): Status {resp.status_code}")

print()
print("5. CORS config test:")
resp = safe_request("options", f"{BASE}/api/v1/auth/login-json",
    headers={
        "Origin": "https://evil.com",
        "Access-Control-Request-Method": "POST"
    })
if resp:
    cors = resp.headers.get("Access-Control-Allow-Origin", "N/A")
    print(f"   Evil origin CORS: {cors}")
    if cors == "*" or cors == "https://evil.com":
        print(f"   !! CORS allows any origin!")
    else:
        print(f"   CORS properly configured")
else:
    print(f"   CORS test request failed")

print()
print("6. Security response headers:")
resp = safe_request("get", f"{BASE}/")
if resp:
    headers_to_check = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
    ]
    for header in headers_to_check:
        value = resp.headers.get(header)
        status = "OK" if value else "MISSING"
        print(f"   {header}: {value if value else '(not set)'} [{status}]")

print()
print("7. Rate limiting test (10 rapid requests):")
success_count = 0
for i in range(10):
    resp = safe_request("get", f"{BASE}/api/v1/health", timeout=10)
    if resp and resp.status_code == 200:
        success_count += 1
print(f"   10 rapid requests: {success_count}/10 succeeded")
if success_count == 10:
    print(f"   NOTE: No rate limiting on health endpoint (expected)")

print()
print("8. Login brute force protection:")
for i in range(7):
    resp = safe_request("post", f"{BASE}/api/v1/auth/login-json",
        json={"username": "bruteforce_test", "password": f"wrong{i}", "device_type": "pc"})
    if resp:
        print(f"   Attempt {i+1}: Status {resp.status_code}")
    else:
        print(f"   Attempt {i+1}: Request failed")

print()
print("9. Error message info leakage:")
resp = safe_request("get", f"{BASE}/api/v1/nonexistent-endpoint")
if resp:
    print(f"   Non-existent endpoint: Status {resp.status_code}")
    if resp.status_code == 404:
        try:
            data = resp.json()
            print(f"   Response: {json.dumps(data, ensure_ascii=False)[:200]}")
        except:
            print(f"   Response: {resp.text[:200]}")

resp = safe_request("get", f"{BASE}/api/v1/personnel/abc")
if resp:
    print(f"   Invalid ID format: Status {resp.status_code}")
    if resp.status_code in [400, 422]:
        try:
            data = resp.json()
            print(f"   Response: {json.dumps(data, ensure_ascii=False)[:200]}")
        except:
            print(f"   Response: {resp.text[:200]}")

print()
print("10. Token refresh security:")
resp = safe_request("post", f"{BASE}/api/v1/auth/refresh",
    json={"refresh_token": "invalid_token"})
if resp:
    print(f"   Invalid refresh token: Status {resp.status_code}")
else:
    print(f"   Refresh token test request failed")

print()
print("=== Security Test Complete ===")
