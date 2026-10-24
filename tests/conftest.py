"""
Pytest configuration and shared fixtures for the GCP Multi-Agent Engineering
Team test suite.
"""

import asyncio
import os
import sys

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multi_agent_team.models.provider import initialize_models  # noqa: E402


@pytest.fixture(scope="session")
def model_provider():
    """Initialize the model provider once for the test session."""
    return initialize_models()


@pytest.fixture
def mock_model():
    """Provide a MockModel instance for testing."""
    from multi_agent_team.models.provider import MockModel

    return MockModel("architecture_critical")
