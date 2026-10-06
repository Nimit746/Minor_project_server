"""
Pytest configuration file for the entire test suite.
Contains shared fixtures and configuration for all tests.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture(scope="session")
def event_loop_policy():
    """Create an event loop policy for the test session."""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
def memory_saver():
    """Fixture to create a fresh MemorySaver for each test."""
    return MemorySaver()


@pytest.fixture
def sample_candidate_data():
    """Fixture providing sample candidate data for tests."""
    return {
        "candidate_id": "test_candidate_001",
        "company_name": "Amazon",
        "target_role": "AI Engineer",
        "resume_text": """
        Nimit - AI Engineer
        Skills: Python, FastAPI, Distributed Systems, PostgreSQL, Docker, Redis, Kubernetes, LangGraph, PyTorch
        Experience: 2 years building high-throughput microservices and REST APIs in Python.
        """
    }


@pytest.fixture
def test_config():
    """Fixture providing standard test configuration."""
    return {"configurable": {"thread_id": "test_thread_001"}}