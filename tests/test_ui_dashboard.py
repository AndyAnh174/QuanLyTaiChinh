"""
UI Tests for Dashboard page using Playwright

These tests run against a manually started Django server at localhost:8000.
"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.ui
def test_dashboard_requires_access_code(page: Page):
    """Test that dashboard requires access code verification"""
    # Clear cookies to ensure fresh state
    page.context.clear_cookies()
    
    # Try to access dashboard without verification
    page.goto(f"{BASE_URL}/")
    
    # Should be redirected to access code page
    expect(page).to_have_url(f"{BASE_URL}/auth/access-code")

