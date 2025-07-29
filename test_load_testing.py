#!/usr/bin/env python3
"""
Load Testing Suite for Football Stats API
Tests API performance under various load conditions.
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

import aiohttp
import requests


class LoadTester:
    """Load testing utility for the Football Stats API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.results: List[Dict] = []
    
    def single_request(self, endpoint: str, params: Dict = None) -> Tuple[float, int]:
        """Make a single request and return response time and status code."""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=30)
            response_time = time.time() - start_time
            return response_time, response.status_code
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, 0  # 0 indicates error
    
    def concurrent_load_test(self, endpoint: str, num_requests: int, 
                           max_workers: int = 10, params: Dict = None) -> Dict:
        """Perform concurrent load testing on an endpoint."""
        print(f"🔄 Testing {endpoint} with {num_requests} concurrent requests...")
        
        start_time = time.time()
        response_times = []
        status_codes = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            futures = [
                executor.submit(self.single_request, endpoint, params)
                for _ in range(num_requests)
            ]
            
            # Collect results
            for future in as_completed(futures):
                response_time, status_code = future.result()
                response_times.append(response_time)
                status_codes.append(status_code)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        successful_requests = sum(1 for code in status_codes if code == 200)
        failed_requests = num_requests - successful_requests
        success_rate = (successful_requests / num_requests) * 100
        
        results = {
            "endpoint": endpoint,
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": self.percentile(response_times, 95) if response_times else 0,
            "p99_response_time": self.percentile(response_times, 99) if response_times else 0
        }
        
        self.results.append(results)
        return results
    
    @staticmethod
    def percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of response times."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def async_load_test(self, endpoint: str, num_requests: int, 
                            concurrency: int = 10) -> Dict:
        """Perform asynchronous load testing."""
        print(f"🚀 Async testing {endpoint} with {num_requests} requests, concurrency: {concurrency}")
        
        async def make_request(session: aiohttp.ClientSession) -> Tuple[float, int]:
            start_time = time.time()
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    await response.read()  # Ensure we read the full response
                    response_time = time.time() - start_time
                    return response_time, response.status
            except Exception:
                response_time = time.time() - start_time
                return response_time, 0
        
        start_time = time.time()
        response_times = []
        status_codes = []
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_request(session: aiohttp.ClientSession):
            async with semaphore:
                return await make_request(session)
        
        async with aiohttp.ClientSession() as session:
            tasks = [bounded_request(session) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, tuple):
                    response_time, status_code = result
                    response_times.append(response_time)
                    status_codes.append(status_code)
        
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for code in status_codes if code == 200)
        failed_requests = num_requests - successful_requests
        success_rate = (successful_requests / num_requests) * 100
        
        return {
            "endpoint": endpoint,
            "test_type": "async",
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": self.percentile(response_times, 95) if response_times else 0,
            "p99_response_time": self.percentile(response_times, 99) if response_times else 0
        }
    
    def ramp_up_test(self, endpoint: str, max_concurrent: int = 50, step: int = 5) -> List[Dict]:
        """Perform ramp-up testing to find the breaking point."""
        print(f"📈 Ramp-up testing {endpoint} from 1 to {max_concurrent} concurrent requests...")
        
        ramp_results = []
        
        for concurrent in range(step, max_concurrent + 1, step):
            print(f"   Testing with {concurrent} concurrent requests...")
            
            result = self.concurrent_load_test(endpoint, concurrent, max_workers=concurrent)
            ramp_results.append(result)
            
            # Stop if success rate drops below 90%
            if result["success_rate"] < 90:
                print(f"   ⚠️  Success rate dropped to {result['success_rate']:.1f}% - stopping ramp-up")
                break
            
            # Add delay between tests
            time.sleep(1)
        
        return ramp_results
    
    def stress_test_scenario(self) -> None:
        """Run comprehensive stress testing scenario."""
        print("🏋️  STRESS TESTING SCENARIO")
        print("=" * 50)
        
        # Test different endpoints under load
        test_scenarios = [
            {"endpoint": "/", "requests": 100, "workers": 20, "name": "Homepage Load Test"},
            {"endpoint": "/api/players/?limit=10", "requests": 100, "workers": 20, "name": "Player List Load Test"},
            {"endpoint": "/api/players/1", "requests": 100, "workers": 20, "name": "Single Player Load Test"},
            {"endpoint": "/api/players/?name=Arsenal", "requests": 50, "workers": 10, "name": "Search Load Test"},
            {"endpoint": "/api/players/paginated?page=1&per_page=10", "requests": 50, "workers": 10, "name": "Pagination Load Test"}
        ]
        
        for scenario in test_scenarios:
            print(f"\n🎯 {scenario['name']}")
            print("-" * 30)
            
            result = self.concurrent_load_test(
                scenario["endpoint"], 
                scenario["requests"], 
                scenario["workers"]
            )
            
            self.print_test_results(result)
    
    def print_test_results(self, result: Dict) -> None:
        """Print formatted test results."""
        print(f"📊 Results for {result['endpoint']}:")
        print(f"   Total Requests: {result['total_requests']}")
        print(f"   Successful: {result['successful_requests']} ({result['success_rate']:.1f}%)")
        print(f"   Failed: {result['failed_requests']}")
        print(f"   Total Time: {result['total_time']:.2f}s")
        print(f"   Requests/sec: {result['requests_per_second']:.2f}")
        print(f"   Avg Response Time: {result['avg_response_time']:.3f}s")
        print(f"   Min Response Time: {result['min_response_time']:.3f}s")
        print(f"   Max Response Time: {result['max_response_time']:.3f}s")
        print(f"   95th Percentile: {result['p95_response_time']:.3f}s")
        print(f"   99th Percentile: {result['p99_response_time']:.3f}s")
        
        # Performance assessment
        if result['success_rate'] >= 99:
            status = "✅ EXCELLENT"
        elif result['success_rate'] >= 95:
            status = "🟢 GOOD"
        elif result['success_rate'] >= 90:
            status = "🟡 ACCEPTABLE"
        else:
            status = "🔴 POOR"
        
        print(f"   Status: {status}")
    
    def print_summary(self) -> None:
        """Print overall test summary."""
        if not self.results:
            print("No test results to summarize.")
            return
        
        print("\n" + "=" * 50)
        print("📈 LOAD TESTING SUMMARY")
        print("=" * 50)
        
        total_requests = sum(r["total_requests"] for r in self.results)
        successful_requests = sum(r["successful_requests"] for r in self.results)
        overall_success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        avg_rps = statistics.mean([r["requests_per_second"] for r in self.results])
        avg_response_time = statistics.mean([r["avg_response_time"] for r in self.results])
        
        print(f"Total Requests Tested: {total_requests}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Average RPS: {avg_rps:.2f}")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        
        # Find worst performing endpoint
        worst_endpoint = min(self.results, key=lambda x: x["success_rate"])
        best_endpoint = max(self.results, key=lambda x: x["success_rate"])
        
        print(f"\n🔴 Worst Performing: {worst_endpoint['endpoint']} ({worst_endpoint['success_rate']:.1f}%)")
        print(f"🟢 Best Performing: {best_endpoint['endpoint']} ({best_endpoint['success_rate']:.1f}%)")


async def main():
    """Main function to run load tests."""
    print("🚀 Football Stats API - Load Testing Suite")
    print("=" * 50)
    
    # Check if API is available
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ API is not available - please start the application first")
            return
    except:
        print("❌ API is not available - please start the application first")
        return
    
    print("✅ API is available - starting load tests...")
    
    tester = LoadTester()
    
    # 1. Basic load tests
    print("\n🔄 BASIC LOAD TESTS")
    print("-" * 30)
    
    basic_tests = [
        {"endpoint": "/", "requests": 50, "workers": 10},
        {"endpoint": "/api/players/?limit=5", "requests": 50, "workers": 10},
        {"endpoint": "/api/players/1", "requests": 50, "workers": 10}
    ]
    
    for test in basic_tests:
        result = tester.concurrent_load_test(test["endpoint"], test["requests"], test["workers"])
        tester.print_test_results(result)
        print()
    
    # 2. Async load test
    print("\n🚀 ASYNC LOAD TEST")
    print("-" * 30)
    
    async_result = await tester.async_load_test("/api/players/?limit=10", 100, 20)
    print(f"📊 Async Results for {async_result['endpoint']}:")
    print(f"   Success Rate: {async_result['success_rate']:.1f}%")
    print(f"   Requests/sec: {async_result['requests_per_second']:.2f}")
    print(f"   Avg Response Time: {async_result['avg_response_time']:.3f}s")
    print()
    
    # 3. Ramp-up test
    print("\n📈 RAMP-UP TEST")
    print("-" * 30)
    
    ramp_results = tester.ramp_up_test("/api/players/?limit=5", max_concurrent=30, step=5)
    print(f"🎯 Ramp-up test completed with {len(ramp_results)} steps")
    
    # 4. Stress test scenario
    tester.stress_test_scenario()
    
    # 5. Print summary
    tester.print_summary()
    
    print("\n🏁 Load testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
