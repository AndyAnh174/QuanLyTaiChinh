"""
UI Tests for Access Code page using Playwright

These tests run against a manually started Django server at localhost:8000.
Start the server first: python manage.py runserver 8000
"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.ui
def test_access_code_page_loads(page: Page):
    """Test that access code page loads correctly"""
    page.goto(f"{BASE_URL}/auth/access-code")
    
    # Check page title
    expect(page).to_have_title("Nhập Mã Truy Cập - AI Smart Finance")
    
    # Check heading (template uses h2, not h1)
    heading = page.locator("h2")
    expect(heading).to_be_visible()
    expect(heading).to_contain_text("Nhập Mã Truy Cập")
    
    # Check input field exists
    input_field = page.locator('input[type="password"][name="code"]')
    expect(input_field).to_be_visible()
    expect(input_field).to_have_attribute("placeholder", "Nhập mã truy cập")
    
    # Check submit button
    submit_button = page.locator('button[type="submit"]')
    expect(submit_button).to_be_visible()
    expect(submit_button).to_contain_text("Xác nhận")


@pytest.mark.ui
def test_access_code_redirect(page: Page):
    """Test that unauthenticated users are redirected to access code page"""
    # Try to access home page
    page.goto(f"{BASE_URL}/")
    
    # Should be redirected to access code page
    expect(page).to_have_url(f"{BASE_URL}/auth/access-code")


@pytest.mark.ui
def test_access_code_empty_submit(page: Page):
    """Test that empty code shows validation error"""
    page.goto(f"{BASE_URL}/auth/access-code")
    
    # HTML5 validation should prevent submission
    input_field = page.locator('input[type="password"][name="code"]')
    expect(input_field).to_have_attribute("required", "")


@pytest.mark.ui
def test_access_code_autofocus(page: Page):
    """Test that input field has autofocus"""
    page.goto(f"{BASE_URL}/auth/access-code")
    
    input_field = page.locator('input[type="password"][name="code"]')
    expect(input_field).to_have_attribute("autofocus", "")


@pytest.mark.ui
def test_access_code_success(page: Page):
    """Test successful access code verification"""
    page.goto(f"{BASE_URL}/auth/access-code")
    
    # Enter correct access code (1234 is default)
    input_field = page.locator('input[type="password"][name="code"]')
    input_field.fill("1234")
    
    # Submit form
    submit_button = page.locator('button[type="submit"]')
    submit_button.click()
    
    # Wait for redirect
    page.wait_for_timeout(2000)
    
    # Check if we're redirected away from access code page
    expect(page).not_to_have_url(f"{BASE_URL}/auth/access-code", timeout=5000)


@pytest.mark.ui
def test_access_code_wrong_code(page: Page):
    """Test error message when wrong access code is entered"""
    page.goto(f"{BASE_URL}/auth/access-code")
    
    # Enter wrong access code
    input_field = page.locator('input[type="password"][name="code"]')
    input_field.fill("wrong")
    
    # Submit form
    submit_button = page.locator('button[type="submit"]')
    submit_button.click()
    
    # Check error message appears
    error_message = page.locator("#errorMessage")
    expect(error_message).to_be_visible(timeout=3000)

