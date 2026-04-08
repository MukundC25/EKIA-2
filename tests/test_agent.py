"""
Tests — Agent Pipeline
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from app.utils.parser import parse_raw_input, detect_language, extract_error_type


# ---------------------------------------------------------------------------
# Parser unit tests (no LLM/external deps needed)
# ---------------------------------------------------------------------------

def test_detect_java_language():
    assert detect_language("NullPointerException at line 42") == "java"


def test_detect_python_language():
    assert detect_language("KeyError: 'user_id' in dict lookup") == "python"


def test_detect_javascript_language():
    assert detect_language("TypeError: Cannot read properties of undefined") == "javascript"


def test_detect_unknown_language():
    result = detect_language("something went wrong with the server")
    assert result is None or isinstance(result, str)


def test_extract_error_type_npe():
    result = extract_error_type("NullPointerException at UserService.java:42")
    assert "NullPointerException" in result


def test_extract_error_type_python():
    result = extract_error_type("Traceback (most recent call last):\n  File test.py\nKeyError: 'name'")
    assert len(result) > 0


def test_parse_raw_input_complete():
    result = parse_raw_input(
        "NullPointerException",
        language="java",
        context="calling getName() on null object"
    )
    assert result["error_type"] == "NullPointerException"
    assert result["language"] == "java"
    assert "rewritten_query" in result


def test_parse_raw_input_auto_detect():
    result = parse_raw_input("KeyError: 'user_id'")
    assert result["language"] in ["python", "unknown"]
    assert len(result["rewritten_query"]) > 0


# ---------------------------------------------------------------------------
# LangGraph state validation tests (mocked LLM)
# ---------------------------------------------------------------------------

def test_validate_node_adds_defaults():
    """validate_node should fill in missing fields."""
    from agent.langgraph_flow import validate_node

    state = {
        "raw_input": "test error",
        "language": "python",
        "context": "",
        "code_snippet": "",
        "parsed_query": {"error_type": "TestError", "language": "python"},
        "vector_results": [],
        "graph_results": [],
        "vector_context_str": "",
        "graph_context_str": "",
        "reasoning_output": {},  # Empty — should be filled with defaults
        "final_response": {},
        "error": None,
        "trace_id": None,
    }
    result = validate_node(state)
    output = result["reasoning_output"]
    assert "error" in output
    assert "fix" in output
    assert "confidence_score" in output
    assert 0.0 <= output["confidence_score"] <= 1.0
    assert isinstance(output["related_concepts"], list)
    assert isinstance(output["practice_problems"], list)


def test_confidence_clamping():
    """validate_node should clamp confidence to [0.0, 1.0]."""
    from agent.langgraph_flow import validate_node

    state = {
        "raw_input": "error",
        "language": "java",
        "context": "",
        "code_snippet": "",
        "parsed_query": {},
        "vector_results": [],
        "graph_results": [],
        "vector_context_str": "",
        "graph_context_str": "",
        "reasoning_output": {"confidence_score": 1.5},  # Over max
        "final_response": {},
        "error": None,
        "trace_id": None,
    }
    result = validate_node(state)
    assert result["reasoning_output"]["confidence_score"] == 1.0
