"""
Tests — FastAPI API Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_health_check():
    """Health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_root_endpoint():
    """Root endpoint should return API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_graph_stats():
    """Graph stats endpoint should return without error."""
    response = client.get("/api/graph/stats")
    assert response.status_code == 200


def test_graph_full():
    """Full graph endpoint should return nodes and edges."""
    response = client.get("/api/graph/")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


def test_debug_endpoint_valid_request():
    """Debug endpoint should accept a valid request and return structured response."""
    mock_response = MagicMock()
    mock_response.error = "NullPointerException"
    mock_response.root_cause = "Accessing null object reference"
    mock_response.beginner_explanation = "You tried to use something that doesn't exist"
    mock_response.technical_explanation = "NPE thrown when dereferencing null pointer"
    mock_response.fix = "Check for null before calling methods"
    mock_response.related_concepts = ["Null Reference", "Optional"]
    mock_response.practice_problems = ["LeetCode 206"]
    mock_response.confidence_score = 0.9
    mock_response.sources = []
    mock_response.graph_context = None
    mock_response.trace_id = "test-trace-id"

    with patch("app.routes.debug.agent_service.run", return_value=mock_response):
        response = client.post(
            "/api/debug",
            json={
                "error": "NullPointerException",
                "language": "java",
                "context": "Accessing user.getName() when user is null",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "NullPointerException"
    assert "root_cause" in data
    assert "fix" in data
    assert "confidence_score" in data
    assert 0.0 <= data["confidence_score"] <= 1.0


def test_debug_endpoint_missing_error():
    """Debug endpoint should reject request with empty error field."""
    response = client.post(
        "/api/debug",
        json={"error": "", "language": "python"},
    )
    assert response.status_code == 422  # Validation error


def test_debug_history():
    """Debug history endpoint should return 200."""
    response = client.get("/api/debug/history")
    assert response.status_code == 200
