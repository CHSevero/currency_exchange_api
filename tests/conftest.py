"""Test configuration and shared fixtures for the Currency Exchange API.

This module contains pytest fixtures and configuration settings that are shared across multiple
test files. It includes setup and teardown functions for test database connections, API clients,
and other utilities.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """"Fixture for creating a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client
