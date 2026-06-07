import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://play.ludigames.com"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def browser_context():
    """Shared browser context for all UI tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(browser_context):
    """Fresh page for each UI test."""
    page = browser_context.new_page()
    yield page
    page.close()
