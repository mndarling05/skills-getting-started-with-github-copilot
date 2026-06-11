"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
import httpx
from src.app import app


@pytest.fixture
async def async_client():
    """Provide an async HTTP client configured with the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
