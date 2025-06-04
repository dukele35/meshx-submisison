"""Tests for the transformations endpoints."""

import pytest


class TestTransformationsEndpoint:
    """Test cases for the /transformations endpoint."""

    def test_get_transformations(self, client):
        """Test getting the list of available transformations."""
        response = client.get('/transformations')
        assert response.status_code == 200
        data = response.get_json()
        assert 'available_transformations' in data
        assert isinstance(data['available_transformations'], list)

    def test_transformations_method_not_allowed(self, client):
        """Test that only GET requests are allowed on the transformations endpoint."""
        response = client.post('/transformations')
        assert response.status_code == 405


class TestTransformationToggleEndpoint:
    """Test cases for the /transformations/<name>/enable endpoint."""

    def test_enable_transformation(self, client):
        """Test enabling a transformation."""
        response = client.post('/transformations/filter_rows/enable',
                             json={'enabled': True})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'filter_rows' in data['message']
        assert 'enabled' in data['message']

    def test_disable_transformation(self, client):
        """Test disabling a transformation."""
        response = client.post('/transformations/filter_rows/enable',
                             json={'enabled': False})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'filter_rows' in data['message']
        assert 'disabled' in data['message']

    def test_toggle_with_default_enabled_value(self, client):
        """Test that enabled defaults to True when not specified."""
        response = client.post('/transformations/filter_rows/enable',
                             json={})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'enabled' in data['message']

    def test_toggle_invalid_transformation(self, client):
        """Test toggling a non-existent transformation."""
        response = client.post('/transformations/invalid_transform/enable',
                             json={'enabled': True})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_toggle_missing_json(self, client):
        """Test POST request with JSON content-type but no body."""
        response = client.post('/transformations/filter_rows/enable',
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 400

    def test_toggle_method_not_allowed(self, client):
        """Test that only POST requests are allowed on the toggle endpoint."""
        response = client.get('/transformations/filter_rows/enable')
        assert response.status_code == 405
        
        response = client.put('/transformations/filter_rows/enable')
        assert response.status_code == 405