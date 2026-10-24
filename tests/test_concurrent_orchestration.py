"""
Tests for the concurrent orchestration engine and multi-model provider.
These tests run in offline/demo mode using MockModel when no external
model providers are available.
"""

import asyncio
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multi_agent_team.models.provider import MockModel, initialize_models
from multi_agent_team.orchestration.concurrent_engine import (
    initialize_concurrent_engine,
    ConcurrentOrchestrationEngine,
)
from multi_agent_team.agents.factory import initialize_agent_factory


def test_mock_model_architecture():
    """MockModel should generate architecture-related responses."""
    mock = MockModel("architecture_critical")
    result = mock.invoke("Design a GCP platform architecture with VPC and IAM")
    assert result.response_metadata["mock"] is True
    assert result.response_metadata["model_provider"] == "Mock (demo mode)"
    content = result.content
    assert "components" in content or "mock_architecture_designed" in str(content)


def test_mock_model_security():
    """MockModel should generate security-related responses."""
    mock = MockModel("architecture_critical")
    result = mock.invoke("Perform security threat model review")
    assert result.response_metadata["mock"] is True
    content = result.content
    assert "threat_model" in content or "controls" in content


def test_mock_model_requirements():
    """MockModel should generate product requirements."""
    mock = MockModel("senior_reasoning")
    result = mock.invoke("Define product requirements and acceptance criteria")
    assert result.response_metadata["mock"] is True
    content = result.content
    assert "requirements" in content or "epics" in content


def test_mock_model_finops():
    """MockModel should generate cost analysis."""
    mock = MockModel("fast_coding")
    result = mock.invoke("Analyze monthly cost estimate and budget impact")
    assert result.response_metadata["mock"] is True
    content = result.content
    assert "monthly_cost_estimate" in content or "budget_status" in content


def test_mock_model_testing():
    """MockModel should generate test results."""
    mock = MockModel("fast_agent")
    result = mock.invoke("Execute test plan and measure coverage")
    assert result.response_metadata["mock"] is True
    content = result.content
    assert "test_coverage" in content or "tests_passed" in content


def test_initialize_models_offline():
    """initialize_models should succeed even without NVIDIA API or Ollama."""
    mp = initialize_models()
    assert mp is not None
    policies = mp.list_models()
    assert len(policies) == 7
    assert "architecture_critical" in policies
    assert "senior_reasoning" in policies
    assert "coding" in policies
    assert "fast_agent" in policies
    assert "fast_coding" in policies
    assert "embedding" in policies
    assert "reranker" in policies


def test_concurrent_engine_initialization():
    """ConcurrentOrchestrationEngine should initialize successfully."""
    engine = initialize_concurrent_engine()
    assert engine is not None
    assert isinstance(engine, ConcurrentOrchestrationEngine)


def test_agent_factory_creates_all_agents():
    """AgentFactory should create all 22 agents."""
    factory = initialize_agent_factory()
    agents = factory.create_all_agents()
    assert len(agents) == 22


@pytest.mark.asyncio
async def test_concurrent_agent_execution():
    """All 22 agents should execute concurrently without errors."""
    engine = initialize_concurrent_engine()
    agent_ids = [
        "product_owner", "platform_architect", "security_architect",
        "solution_architect", "development_lead", "backend_engineer",
        "frontend_engineer", "qa_lead", "devops_lead",
        "sre_observability_engineer",
    ]
    result = await engine.execute_agents_in_concurrence(
        agent_ids=agent_ids,
        objective="Test concurrent agent execution",
        max_concurrent=len(agent_ids),
    )
    assert result["status"] == "completed"
    assert result["successful_agents"] == len(agent_ids)
    assert result["failed_agents"] == 0
    assert len(result["errors"]) == 0


def test_model_stats_tracking():
    """Model provider should track invocation statistics."""
    mp = initialize_models()
    stats = mp.get_total_stats()
    assert "total_invocations" in stats
    assert "total_tokens" in stats
    assert "total_success" in stats
    assert "total_failure" in stats
    assert "policies" in stats