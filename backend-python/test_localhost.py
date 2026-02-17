import subprocess
import time
import requests
import socket

print("=" * 60)
print("详细诊断localhost问题")
print("=" * 60)

print("\n1. 检查hosts文件内容:")
with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
    content = f.read()
    for line in content.split('\n'):
        if 'localhost' in line.lower() and not line.strip().startswith('#'):
            print(f"   {line}")

print("\n2. DNS解析测试:")
start = time.time()
ip = socket.gethostbyname('localhost')
elapsed = (time.time() - start) * 1000
print(f"   gethostbyname('localhost') = {ip}, 耗时: {elapsed:.2f}ms")

try:
    start = time.time()
    infos = socket.getaddrinfo('localhost', 8000)
    elapsed = (time.time() - start) * 1000
    print(f"   getaddrinfo('localhost', 8000) 耗时: {elapsed:.2f}ms")
    for info in infos:
        print(f"      地址族: {info[0].name}, 地址: {info[4]}")
except Exception as e:
    print(f"   getaddrinfo错误: {e}")

print("\n3. API响应测试对比:")
print("   使用127.0.0.1:")
times_127 = []
for i in range(3):
    start = time.time()
    response = requests.get("http://127.0.0.1:8000/api/v1/project-info?page=0&size=10", timeout=10)
    elapsed = (time.time() - start) * 1000
    times_127.append(elapsed)
    print(f"      第{i+1}次: {elapsed:.2f}ms")
print(f"   平均: {sum(times_127)/len(times_127):.2f}ms")

print("\n   使用localhost:")
times_local = []
for i in range(3):
    start = time.time()
    response = requests.get("http://localhost:8000/api/v1/project-info?page=0&size=10", timeout=10)
    elapsed = (time.time() - start) * 1000
    times_local.append(elapsed)
    print(f"      第{i+1}次: {elapsed:.2f}ms")
print(f"   平均: {sum(times_local)/len(times_local):.2f}ms")

print("\n" + "=" * 60)
print("结论:")
if sum(times_127)/len(times_127) < 100 and sum(times_local)/len(times_local) > 1000:
    print("   ⚠️ localhost仍有约2秒延迟")
    print("   原因：Python requests库可能使用IPv6连接")
    print("   解决方案：")
    print("   1. 前端已改用127.0.0.1，无需担心")
    print("   2. 如需修复localhost，需禁用系统IPv6")
else:
    print("   ✅ localhost解析正常")
