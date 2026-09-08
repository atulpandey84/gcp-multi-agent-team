import pytest
import asyncio
from httpx import AsyncClient
from playwright.async_api import async_playwright

# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(scope="session")
async def api_client() -> AsyncClient:
    """Provides an asynchronous HTTP client configured to hit the running API."""
    # Assuming the main FastAPI application is run on http://localhost:8000
    # We use an API client here for robust, non-UI API testing.
    base_url = "http://localhost:8000"
    async with AsyncClient(base_url=base_url, headers={"Authorization": "Bearer test-api-key"}) as client:
        yield client

@pytest.fixture(scope="session")
async def playwright_context():
    """Fixture for Playwright: Launches a browser and yields a context."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        yield context
        await browser.close()

@pytest.fixture(scope="session")
async def mock_api_server(api_client: AsyncClient):
    """
    A simplified mock server fixture to ensure tests don't rely on
    a live, running, complex external service for pure logic testing.
    In a real setup, we would use FastAPI's TestClient.
    For this E2E context, we will just ensure the API client is available.
    """
    return api_client

# ==============================================================================
# END OF FIXTURES
# ==============================================================================
import pytest
import asyncio
from httpx import AsyncClient
from playwright.async_api import async_playwright

# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(scope=\"session\")
async def api_client() -> AsyncClient:
    \"\"\"Provides an asynchronous HTTP client configured to hit the running API."""
    # Assuming the main FastAPI application is run on http://localhost:8000
    # We use an API client here for robust, non-UI API testing.
    base_url = \"http://localhost:8000\"
    async with AsyncClient(base_url=base_url, headers={\\\"Authorization\\\": \\\"Bearer test-api-key\\\"}) as client:
        yield client

@pytest.fixture(scope=\"session\")
async def playwright_context():
    \"\"\"Fixture for Playwright: Launches a browser and yields a context."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        yield context
        await browser.close()

@pytest.fixture(scope=\"session\")
async def mock_api_server(api_client: AsyncClient):
    \"\"\"
    A simplified mock server fixture to ensure tests don't rely on
    a live, running, complex external service for pure logic testing.
    In a real setup, we would use FastAPI's TestClient.
    For this E2E context, we will just ensure the API client is available.
    \"\"\"
    return api_client

# ==============================================================================
# END OF FIXTURES
# ==============================================================================