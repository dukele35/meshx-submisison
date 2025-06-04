"""Tests for the health endpoint."""

import pytest


class TestHealthEndpoint:
    """Test cases for the /health endpoint."""

    def test_health_check(self, client):
        """Test that the health check endpoint returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_health_check_method_not_allowed(self, client):
        """Test that only GET requests are allowed on the health endpoint."""
        response = client.post('/health')
        assert response.status_code == 405
        
        response = client.put('/health')
        assert response.status_code == 405
        
        response = client.delete('/health')
        assert response.status_code == 405