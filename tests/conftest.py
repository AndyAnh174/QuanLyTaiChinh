"""
Pytest configuration for Playwright tests
"""
import pytest


@pytest.fixture
def authenticated_client(client):
    """Create a client with verified access code"""
    session = client.session
    session['access_code_verified'] = True
    session.save()
    return client

