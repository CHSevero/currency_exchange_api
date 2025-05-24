"""Test module for the main FastAPI application.

This module contains test cases for the root and health check endpoints of the FastAPI application.
"""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Currency Converter API!"}


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
