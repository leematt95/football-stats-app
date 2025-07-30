#!/usr/bin/env python3
"""
Pytest-based API Testing Suite for Football Stats Application
Professional test suite with fixtures, parametrized tests, and detailed reporting.
"""

import asyncio
import json
import time
from typing import Any, Dict, List
from urllib.parse import urlencode

import aiohttp
import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for the API."""
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def api_session():
    """Requests session for API calls."""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def wait_for_api(api_base_url):
    """Wait for the API to be available before running tests."""
    max_retries = 10
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{api_base_url}/", timeout=5)
            if response.status_code == 200:
                return True
        except:
            if attempt < max_retries - 1:
                time.sleep(2)
    pytest.skip("API is not available")


class TestWelcomeEndpoint:
    """Test the welcome/root endpoint."""

    def test_welcome_message(self, api_session, api_base_url, wait_for_api):
        """Test that the welcome endpoint returns expected message."""
        response = api_session.get(f"{api_base_url}/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "Football Stats API" in data["message"]

    def test_welcome_response_time(self, api_session, api_base_url, wait_for_api):
        """Test that welcome endpoint responds quickly."""
        start_time = time.time()
        response = api_session.get(f"{api_base_url}/")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds


class TestPlayerEndpoints:
    """Test player-related endpoints."""

    def test_get_players_basic(self, api_session, api_base_url, wait_for_api):
        """Test basic player retrieval."""
        response = api_session.get(f"{api_base_url}/api/players/", params={"limit": 5})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

        if data:
            player = data[0]
            assert "Name" in player
            assert "Club" in player
            assert "Position" in player

    @pytest.mark.parametrize(
        "player_name", ["Salah", "Haaland", "Kane", "De Bruyne", "Son"]
    )
    def test_search_players_by_name(
        self, api_session, api_base_url, wait_for_api, player_name
    ):
        """Test searching for players by name."""
        response = api_session.get(
            f"{api_base_url}/api/players/", params={"name": player_name}
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If players found, verify they match the search
        for player in data:
            assert player_name.lower() in player["Name"].lower()

    def test_search_nonexistent_player(self, api_session, api_base_url, wait_for_api):
        """Test searching for a non-existent player."""
        response = api_session.get(
            f"{api_base_url}/api/players/", params={"name": "NonExistentPlayer123"}
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_player_by_id(self, api_session, api_base_url, wait_for_api):
        """Test retrieving a specific player by ID."""
        response = api_session.get(f"{api_base_url}/api/players/1")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "ID" in data
        assert "Name" in data
        assert "Club" in data
        assert "Position" in data
        assert data["ID"] == 1

    def test_get_nonexistent_player(self, api_session, api_base_url, wait_for_api):
        """Test retrieving a non-existent player."""
        response = api_session.get(f"{api_base_url}/api/players/99999")
        assert response.status_code == 404


class TestSearchEndpoints:
    """Test search-specific endpoints."""

    @pytest.mark.parametrize(
        "team_name", ["Liverpool", "Arsenal", "Manchester", "Chelsea", "Tottenham"]
    )
    def test_json_search_by_team(
        self, api_session, api_base_url, wait_for_api, team_name
    ):
        """Test JSON search endpoint with team names."""
        response = api_session.get(
            f"{api_base_url}/api/players/search/json", params={"name": team_name}
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Verify players are from the searched team (if any found)
        for player in data:
            assert (
                team_name.lower() in player["Club"].lower()
                or team_name.lower() in player["Name"].lower()
            )

    def test_json_search_missing_parameter(
        self, api_session, api_base_url, wait_for_api
    ):
        """Test JSON search without required name parameter."""
        response = api_session.get(f"{api_base_url}/api/players/search/json")
        assert response.status_code == 400

    def test_html_search_endpoint(self, api_session, api_base_url, wait_for_api):
        """Test HTML search endpoint returns HTML content."""
        response = api_session.get(
            f"{api_base_url}/api/players/search/html", params={"name": "Arsenal"}
        )
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestPaginationEndpoints:
    """Test pagination functionality."""

    @pytest.mark.parametrize("page,per_page", [(1, 5), (1, 10), (2, 5), (1, 20)])
    def test_pagination_basic(
        self, api_session, api_base_url, wait_for_api, page, per_page
    ):
        """Test basic pagination with different parameters."""
        response = api_session.get(
            f"{api_base_url}/api/players/paginated",
            params={"page": page, "per_page": per_page},
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "players" in data
        assert "total_items" in data
        assert "total_pages" in data
        assert "current_page" in data

        assert data["current_page"] == page
        assert len(data["players"]) <= per_page
        assert isinstance(data["players"], list)

    def test_pagination_with_search(self, api_session, api_base_url, wait_for_api):
        """Test pagination combined with search."""
        response = api_session.get(
            f"{api_base_url}/api/players/paginated",
            params={"page": 1, "per_page": 5, "name": "Manchester"},
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "players" in data

        # Verify search filter is applied
        for player in data["players"]:
            assert (
                "manchester" in player["Club"].lower()
                or "manchester" in player["Name"].lower()
            )

    def test_pagination_metadata(self, api_session, api_base_url, wait_for_api):
        """Test pagination metadata is correct."""
        response = api_session.get(
            f"{api_base_url}/api/players/paginated", params={"page": 1, "per_page": 10}
        )
        assert response.status_code == 200

        data = response.json()
        total_items = data["total_items"]
        total_pages = data["total_pages"]
        per_page = 10

        # Calculate expected total pages
        expected_pages = (total_items + per_page - 1) // per_page
        assert total_pages == expected_pages


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_nonexistent_endpoint(self, api_session, api_base_url, wait_for_api):
        """Test accessing non-existent endpoints."""
        response = api_session.get(f"{api_base_url}/api/nonexistent")
        assert response.status_code == 404

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
    def test_unsupported_methods(self, api_session, api_base_url, wait_for_api, method):
        """Test unsupported HTTP methods on read-only endpoints."""
        response = api_session.request(method, f"{api_base_url}/api/players/")
        assert response.status_code == 405


class TestPerformance:
    """Test API performance and response times."""

    @pytest.mark.parametrize(
        "endpoint,description",
        [
            ("/", "Root endpoint"),
            ("/api/players/?limit=10", "Get 10 players"),
            ("/api/players/1", "Get single player"),
            ("/api/players/?name=Liverpool", "Search players"),
            ("/api/players/paginated?page=1&per_page=10", "Paginated results"),
        ],
    )
    def test_response_times(
        self, api_session, api_base_url, wait_for_api, endpoint, description
    ):
        """Test that endpoints respond within acceptable time limits."""
        start_time = time.time()
        response = api_session.get(f"{api_base_url}{endpoint}")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 3.0, f"{description} took too long: {response_time:.3f}s"

    def test_concurrent_requests(self, api_base_url, wait_for_api):
        """Test API can handle concurrent requests."""
        import concurrent.futures
        import threading

        def make_request():
            session = requests.Session()
            response = session.get(f"{api_base_url}/api/players/?limit=5")
            session.close()
            return response.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert all(status == 200 for status in results)


class TestDataIntegrity:
    """Test data integrity and structure."""

    def test_player_data_structure(self, api_session, api_base_url, wait_for_api):
        """Test that player data has the expected structure."""
        response = api_session.get(f"{api_base_url}/api/players/1")
        assert response.status_code == 200

        player = response.json()
        required_fields = ["ID", "Name", "Position", "Club"]

        for field in required_fields:
            assert field in player
            assert player[field] is not None
            assert player[field] != ""

    def test_search_results_consistency(self, api_session, api_base_url, wait_for_api):
        """Test that search results are consistent."""
        # Search for the same term multiple times
        term = "Liverpool"
        responses = []

        for _ in range(3):
            response = api_session.get(
                f"{api_base_url}/api/players/", params={"name": term}
            )
            assert response.status_code == 200
            responses.append(response.json())
            time.sleep(0.1)  # Small delay between requests

        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response

    def test_player_ids_unique(self, api_session, api_base_url, wait_for_api):
        """Test that player IDs are unique."""
        response = api_session.get(f"{api_base_url}/api/players/", params={"limit": 50})
        assert response.status_code == 200

        players = response.json()
        if players:
            player_ids = [player["ID"] for player in players]
            assert len(player_ids) == len(set(player_ids)), "Player IDs are not unique"


@pytest.mark.asyncio
async def test_async_api_calls():
    """Test asynchronous API operations."""
    async with aiohttp.ClientSession() as session:
        # Test async GET request
        async with session.get(
            "http://localhost:5000/api/players/?name=Salah"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert isinstance(data, list)

        # Test multiple async requests
        tasks = []
        for name in ["Arsenal", "Liverpool", "Chelsea"]:
            task = session.get(f"http://localhost:5000/api/players/?name={name}")
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status == 200
            response.close()


class TestAPIDocumentation:
    """Test API behavior matches documentation."""

    def test_api_returns_json(self, api_session, api_base_url, wait_for_api):
        """Test that API endpoints return JSON content."""
        endpoints = [
            "/",
            "/api/players/",
            "/api/players/1",
            "/api/players/search/json?name=Arsenal",
            "/api/players/paginated?page=1&per_page=5",
        ]

        for endpoint in endpoints:
            response = api_session.get(f"{api_base_url}{endpoint}")
            if response.status_code == 200:
                assert "application/json" in response.headers.get("content-type", "")
                # Should be valid JSON
                response.json()  # This will raise an exception if not valid JSON


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
