import time
import requests
import socket

def test_dns_resolution():
    print("=" * 50)
    print("测试DNS解析")
    print("=" * 50)
    
    start = time.time()
    ip = socket.gethostbyname('localhost')
    elapsed = (time.time() - start) * 1000
    print(f"localhost解析: {ip}, 耗时: {elapsed:.2f}ms")
    
    start = time.time()
    ip = socket.gethostbyname('127.0.0.1')
    elapsed = (time.time() - start) * 1000
    print(f"127.0.0.1解析: {ip}, 耗时: {elapsed:.2f}ms")
    
    print("\n使用localhost:")
    for i in range(3):
        start = time.time()
        response = requests.get("http://localhost:8000/api/v1/project-info?page=0&size=10")
        elapsed = (time.time() - start) * 1000
        print(f"  第{i+1}次: {elapsed:.2f}ms")
    
    print("\n使用127.0.0.1:")
    for i in range(3):
        start = time.time()
        response = requests.get("http://127.0.0.1:8000/api/v1/project-info?page=0&size=10")
        elapsed = (time.time() - start) * 1000
        print(f"  第{i+1}次: {elapsed:.2f}ms")

if __name__ == "__main__":
    test_dns_resolution()
