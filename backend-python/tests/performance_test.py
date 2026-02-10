import time
import statistics
from typing import List, Dict
import requests
import json

BASE_URL = "http://localhost:8080/api"


class PerformanceTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict] = []
    
    def measure_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, params=data)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration_ms": duration,
                "success": response.status_code < 400,
            }
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            return {
                "method": method,
                "endpoint": endpoint,
                "status_code": 0,
                "duration_ms": duration,
                "success": False,
                "error": str(e),
            }
    
    def run_test(self, name: str, method: str, endpoint: str, data: Dict = None, iterations: int = 10) -> None:
        print(f"\nRunning test: {name}")
        print(f"Method: {method} {endpoint}")
        print(f"Iterations: {iterations}")
        
        test_results = []
        for i in range(iterations):
            result = self.measure_request(method, endpoint, data)
            test_results.append(result)
            self.results.append(result)
            print(f"  Iteration {i+1}: {result['duration_ms']:.2f}ms - Status: {result['status_code']}")
        
        durations = [r["duration_ms"] for r in test_results]
        successful = [r for r in test_results if r["success"]]
        
        print(f"\nResults for {name}:")
        print(f"  Total requests: {len(test_results)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(test_results) - len(successful)}")
        print(f"  Average duration: {statistics.mean(durations):.2f}ms")
        print(f"  Min duration: {min(durations):.2f}ms")
        print(f"  Max duration: {max(durations):.2f}ms")
        print(f"  Median duration: {statistics.median(durations):.2f}ms")
        if len(durations) > 1:
            print(f"  Std deviation: {statistics.stdev(durations):.2f}ms")
    
    def generate_report(self) -> str:
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        all_durations = [r["duration_ms"] for r in self.results]
        
        report = f"""
Performance Test Report
======================

Total Tests: {total_tests}
Successful: {successful_tests}
Failed: {failed_tests}
Success Rate: {(successful_tests / total_tests * 100):.2f}%

Overall Statistics:
  Average Duration: {statistics.mean(all_durations):.2f}ms
  Min Duration: {min(all_durations):.2f}ms
  Max Duration: {max(all_durations):.2f}ms
  Median Duration: {statistics.median(all_durations):.2f}ms
"""
        return report


def main():
    print("SSTCP Maintenance System - Performance Test")
    print("=" * 50)
    
    tester = PerformanceTester()
    
    test_data = {
        "project_id": "PERF-001",
        "project_name": "性能测试项目",
        "completion_date": "2024-01-01T00:00:00",
        "maintenance_end_date": "2025-12-31T00:00:00",
        "maintenance_period": "每月",
        "client_unit": "性能测试客户",
        "client_address": "性能测试地址",
    }
    
    # Test 1: Health Check
    tester.run_test("Health Check", "GET", "/health", iterations=5)
    
    # Test 2: Create Project Info
    tester.run_test("Create Project Info", "POST", "/project-info", data=test_data, iterations=10)
    
    # Test 3: Get Project Info List
    tester.run_test("Get Project Info List", "GET", "/project-info", iterations=10)
    
    # Test 4: Get All Project Info
    tester.run_test("Get All Project Info", "GET", "/project-info/all/list", iterations=5)
    
    # Test 5: Get Project Info by ID (assuming ID 1 exists)
    tester.run_test("Get Project Info by ID", "GET", "/project-info/1", iterations=10)
    
    # Test 6: Update Project Info
    update_data = {
        "project_id": "PERF-001",
        "project_name": "更新后的性能测试项目",
        "completion_date": "2024-01-01T00:00:00",
        "maintenance_end_date": "2025-12-31T00:00:00",
        "maintenance_period": "每月",
        "client_name": "性能测试客户",
        "address": "性能测试地址",
    }
    tester.run_test("Update Project Info", "PUT", "/project-info/1", data=update_data, iterations=10)
    
    # Generate final report
    print("\n" + "=" * 50)
    print(tester.generate_report())
    
    # Save results to file
    with open("performance_report.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    print("Detailed results saved to performance_report.json")


if __name__ == "__main__":
    main()
