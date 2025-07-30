#!/usr/bin/env python3
"""
Comprehensive API Runtime Testing Suite for Football Stats Application
Tests all endpoints with various scenarios and validates responses.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import aiohttp
import requests


class APITestSuite:
    """Comprehensive API testing suite for the Football Stats API."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.test_results: List[Dict[str, Any]] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(
        self,
        test_name: str,
        status: str,
        response_time: float,
        details: Optional[str] = None,
    ) -> None:
        """Log test results."""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            status_icon = "✅"
        else:
            self.failed_tests += 1
            status_icon = "❌"

        result = {
            "test": test_name,
            "status": status,
            "response_time": response_time,
            "details": details,
        }
        self.test_results.append(result)

        print(f"{status_icon} {test_name}: {status} ({response_time:.3f}s)")
        if details and status == "FAIL":
            print(f"   └─ {details}")

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        params: Optional[Dict[str, Any]] = None,
        test_name: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Test a single API endpoint."""
        if test_name is None:
            test_name = f"{method} {endpoint}"

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            else:
                response = self.session.request(method, url, params=params, timeout=10)

            response_time = time.time() - start_time

            # Check status code
            if response.status_code != expected_status:
                self.log_test(
                    test_name,
                    "FAIL",
                    response_time,
                    f"Expected {expected_status}, got {response.status_code}",
                )
                return False, {}

            # Try to parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                self.log_test(
                    test_name, "FAIL", response_time, "Response is not valid JSON"
                )
                return False, {}

            self.log_test(test_name, "PASS", response_time)
            return True, data

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.log_test(test_name, "FAIL", response_time, f"Request failed: {str(e)}")
            return False, {}

    def test_welcome_endpoint(self) -> None:
        """Test the welcome/root endpoint."""
        print("\n🏠 Testing Welcome Endpoint")
        print("-" * 40)

        success, data = self.test_endpoint("GET", "/", test_name="Welcome Message")
        if success and "message" in data:
            if "Football Stats API" in data["message"]:
                print(f"   └─ Message: {data['message']}")
            else:
                self.log_test(
                    "Welcome Message Content",
                    "FAIL",
                    0,
                    "Message doesn't contain expected text",
                )

    def test_player_endpoints(self) -> None:
        """Test all player-related endpoints."""
        print("\n⚽ Testing Player Endpoints")
        print("-" * 40)

        # Test get all players (limited)
        success, data = self.test_endpoint(
            "GET",
            "/api/players/",
            params={"limit": 5},
            test_name="Get Players (limited)",
        )

        # Test player search by name
        test_names = ["Salah", "Haaland", "Kane", "De Bruyne"]
        for name in test_names:
            success, data = self.test_endpoint(
                "GET",
                "/api/players/",
                params={"name": name},
                test_name=f"Search player: {name}",
            )
            if success and isinstance(data, list) and len(data) > 0:
                player = data[0]
                if 'Name' not in player or 'Club' not in player:
                    print(f"   ❌ Missing required fields in player data: {list(player.keys())}")
                else:
                    print(
                        f"   └─ Found: {player['Name']} ({player['Club']})"
                    )

        # Test search with no results
        self.test_endpoint(
            "GET",
            "/api/players/",
            params={"name": "NonExistentPlayer123"},
            test_name="Search non-existent player",
        )

        # Test single player by ID
        success, data = self.test_endpoint(
            "GET", "/api/players/1", test_name="Get player by ID (1)"
        )
        if success and "name" in data:
            if data and 'Name' in data:
                print(f"   └─ Player 1: {data['Name']} ({data['Club']})")
            else:
                print(f"   ❌ Missing required fields in player data: {list(data.keys()) if data else 'No data'}")

        # Test invalid player ID
        self.test_endpoint(
            "GET",
            "/api/players/99999",
            expected_status=404,
            test_name="Get non-existent player",
        )

    def test_search_endpoints(self) -> None:
        """Test search-specific endpoints."""
        print("\n🔍 Testing Search Endpoints")
        print("-" * 40)

        # Test JSON search endpoint
        success, data = self.test_endpoint(
            "GET",
            "/api/players/search/json",
            params={"name": "Liverpool"},
            test_name="JSON search for Liverpool players",
        )
        if success and isinstance(data, list):
            print(f"   └─ Found {len(data)} Liverpool players")

        # Test JSON search without name parameter
        self.test_endpoint(
            "GET",
            "/api/players/search/json",
            expected_status=400,
            test_name="JSON search without name parameter",
        )

        # Test HTML search endpoint (should return HTML, not JSON)
        try:
            url = f"{self.base_url}/api/players/search/html"
            response = self.session.get(url, params={"name": "Arsenal"}, timeout=10)
            if response.status_code == 200 and "text/html" in response.headers.get(
                "content-type", ""
            ):
                self.log_test("HTML search endpoint", "PASS", 0)
            else:
                self.log_test(
                    "HTML search endpoint", "FAIL", 0, "Should return HTML content"
                )
        except Exception as e:
            self.log_test("HTML search endpoint", "FAIL", 0, str(e))

    def test_pagination_endpoints(self) -> None:
        """Test pagination functionality."""
        print("\n📄 Testing Pagination Endpoints")
        print("-" * 40)

        # Test basic pagination
        success, data = self.test_endpoint(
            "GET",
            "/api/players/paginated",
            params={"page": 1, "per_page": 5},
            test_name="Pagination: page 1, 5 per page",
        )

        if success and isinstance(data, dict):
            required_fields = ["total_items", "total_pages", "current_page", "players"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ Missing required pagination fields: {missing_fields}")
                return
                
            total_items = data["total_items"]
            total_pages = data["total_pages"]
            current_page = data["current_page"]
            players = data["players"]

            print(f"   └─ Total items: {total_items}")
            print(f"   └─ Total pages: {total_pages}")
            print(f"   └─ Current page: {current_page}")
            print(f"   └─ Players on page: {len(players)}")

        # Test different page sizes
        for per_page in [3, 10, 20]:
            self.test_endpoint(
                "GET",
                "/api/players/paginated",
                params={"page": 1, "per_page": per_page},
                test_name=f"Pagination: {per_page} per page",
            )

        # Test pagination with search
        success, data = self.test_endpoint(
            "GET",
            "/api/players/paginated",
            params={"page": 1, "per_page": 5, "name": "Manchester"},
            test_name="Pagination with search filter",
        )

        # Test invalid pagination parameters
        self.test_endpoint(
            "GET",
            "/api/players/paginated",
            params={"page": 0, "per_page": 5},
            expected_status=500,  # Should handle gracefully
            test_name="Invalid page number (0)",
        )

    def test_error_handling(self) -> None:
        """Test error handling and edge cases."""
        print("\n⚠️  Testing Error Handling")
        print("-" * 40)

        # Test non-existent endpoints
        self.test_endpoint(
            "GET",
            "/api/nonexistent",
            expected_status=404,
            test_name="Non-existent endpoint",
        )

        self.test_endpoint(
            "GET",
            "/api/players/invalid",
            expected_status=404,
            test_name="Invalid player endpoint",
        )

        # Test invalid HTTP methods
        self.test_endpoint(
            "POST",
            "/api/players/",
            expected_status=405,
            test_name="POST to read-only endpoint",
        )

        self.test_endpoint(
            "DELETE",
            "/api/players/1",
            expected_status=405,
            test_name="DELETE to read-only endpoint",
        )

    def test_performance(self) -> None:
        """Test API performance and response times."""
        print("\n⚡ Testing Performance")
        print("-" * 40)

        # Test response time for different operations
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/api/players/?limit=10", "Get 10 players"),
            ("/api/players/1", "Get single player"),
            ("/api/players/?name=Liverpool", "Search players"),
            ("/api/players/paginated?page=1&per_page=10", "Paginated results"),
        ]

        response_times = []
        for endpoint, description in endpoints_to_test:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                response_times.append(response_time)

                if response_time < 1.0:
                    status = "PASS"
                    details = f"Fast response: {response_time:.3f}s"
                elif response_time < 3.0:
                    status = "PASS"
                    details = f"Acceptable response: {response_time:.3f}s"
                else:
                    status = "FAIL"
                    details = f"Slow response: {response_time:.3f}s"

                self.log_test(
                    f"Performance: {description}", status, response_time, details
                )

            except Exception as e:
                self.log_test(f"Performance: {description}", "FAIL", 0, str(e))

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"   └─ Average response time: {avg_time:.3f}s")

    def test_data_integrity(self) -> None:
        """Test data integrity and structure."""
        print("\n🔍 Testing Data Integrity")
        print("-" * 40)

        # Test player data structure
        success, data = self.test_endpoint(
            "GET", "/api/players/1", test_name="Player data structure"
        )

        if success and isinstance(data, dict):
            required_fields = ["id", "name", "position", "team"]
            missing_fields = [field for field in required_fields if field not in data]

            if not missing_fields:
                self.log_test("Player data has required fields", "PASS", 0)
                print(
                    f"   └─ Player: {data['name']} - {data['position']} - {data['team']}"
                )
            else:
                self.log_test(
                    "Player data has required fields",
                    "FAIL",
                    0,
                    f"Missing fields: {missing_fields}",
                )

        # Test search results structure
        success, data = self.test_endpoint(
            "GET",
            "/api/players/",
            params={"name": "Arsenal"},
            test_name="Search results structure",
        )

        if success and isinstance(data, list) and len(data) > 0:
            first_player = data[0]
            if isinstance(first_player, dict) and "name" in first_player:
                self.log_test("Search results structure", "PASS", 0)
                print(f"   └─ Found {len(data)} Arsenal players")
            else:
                self.log_test(
                    "Search results structure",
                    "FAIL",
                    0,
                    "Invalid player object structure",
                )

    def run_all_tests(self) -> None:
        """Run the complete test suite."""
        print("🧪 Football Stats API - Runtime Testing Suite")
        print("=" * 50)
        print(f"Testing API at: {self.base_url}")

        # Wait for API to be ready
        print("\n⏳ Checking API availability...")
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.session.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ API is available")
                    break
            except:
                if attempt < max_retries - 1:
                    print(
                        f"⏳ Waiting for API... (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(2)
                else:
                    print("❌ API is not available - tests may fail")

        # Run all test categories
        self.test_welcome_endpoint()
        self.test_player_endpoints()
        self.test_search_endpoints()
        self.test_pagination_endpoints()
        self.test_error_handling()
        self.test_performance()
        self.test_data_integrity()

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print test execution summary."""
        print("\n" + "=" * 50)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 50)

        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")

        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(
                        f"   • {result['test']}: {result.get('details', 'Unknown error')}"
                    )

        # Performance summary
        performance_tests = [r for r in self.test_results if "Performance" in r["test"]]
        if performance_tests:
            avg_response_time = sum(
                r["response_time"] for r in performance_tests
            ) / len(performance_tests)
            print(f"\n⚡ Average Response Time: {avg_response_time:.3f}s")

        print(
            "\n🎯 Overall Status:", "✅ PASS" if self.failed_tests == 0 else "❌ FAIL"
        )


async def test_async_functionality():
    """Test asynchronous operations (like the original understat test)."""
    print("\n🔄 Testing Async Data Fetching")
    print("-" * 40)

    try:
        async with aiohttp.ClientSession() as session:
            # Test if we can fetch data from the API asynchronously
            async with session.get(
                "http://localhost:5000/api/players/?name=Salah"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Async API call: PASS")
                    if data and len(data) > 0:
                        print(f"   └─ Found: {data[0].get('name', 'Unknown')}")
                else:
                    print(f"❌ Async API call: FAIL (Status: {response.status})")

    except Exception as e:
        print(f"❌ Async API call: FAIL ({str(e)})")


def main():
    """Main function to run all tests."""
    print("Starting comprehensive API runtime testing...\n")

    # Initialize test suite
    api_tester = APITestSuite()

    # Run synchronous tests
    api_tester.run_all_tests()

    # Run asynchronous tests
    print("\n" + "=" * 50)
    asyncio.run(test_async_functionality())

    print("\n🏁 Testing complete!")


if __name__ == "__main__":
    main()
