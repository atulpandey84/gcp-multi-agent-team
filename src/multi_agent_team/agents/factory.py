"""
Agent Factory for the GCP Multi-Agent Engineering Organization.

Instantiates all 22 agents from their contracts with model assignments,
wires tools, memory, and collaboration capabilities. Supports concurrent
agent instances working together in parallel.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from .base import (
    BaseAgent,
    AgentContract,
    AgentAuthority,
    AgentMemory,
    AgentRole,
    Task,
    TaskStatus,
    AgentMessage,
    QualityGateResult,
    load_agent_contracts,
)
from ..models.provider import (
    get_model_provider,
    get_model_for_agent,
    SmartFallbackModel,
    MODEL_POLICY_AGENT_MAP,
)
from ..tools import register_all_tools, get_tool_registry
from ..governance.engine import GovernanceEngine
from ..memory.manager import get_memory_manager, initialize_memory
from .collaboration import CollaborationEngine

logger = logging.getLogger(__name__)

# Agent class registry - maps agent ID to implementation class
_AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {}


def register_agent_class(agent_id: str, cls: Type[BaseAgent]):
    _AGENT_CLASSES[agent_id] = cls


def get_agent_class(agent_id: str) -> Optional[Type[BaseAgent]]:
    return _AGENT_CLASSES.get(agent_id)


class GenericOperationalAgent(BaseAgent):
    """Generic operational agent that uses the model for execution when no
    specialized implementation class is registered."""

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        model = getattr(self, "model", None)
        model_error = None
        if model:
            try:
                prompt = f"""You are {self.contract.role} ({self.contract.id}).
Mission: {self.contract.mission}
Responsibilities: {', '.join(self.contract.responsibilities)}
Task: {task.objective}
Context: {context}
Produce your output as a structured response with key results, decisions, and recommendations."""
                result = model.invoke(prompt)
                return {
                    "agent_id": self.contract.id,
                    "role": self.contract.role,
                    "model_output": str(result),
                    "status": "completed",
                    "model_used": getattr(model, 'policy', 'unknown'),
                }
            except Exception as exc:
                model_error = str(exc)

        # Fallback: contract-based execution when model is unavailable
        return {
            "agent_id": self.contract.id,
            "role": self.contract.role,
            "team": self.contract.team,
            "mission": self.contract.mission,
            "responsibilities": self.contract.responsibilities,
            "objective": task.objective,
            "context_received": context,
            "status": "completed",
            "execution_mode": "contract_based" if not model_error else "model_fallback",
            "model_error": model_error,
            "outputs": self.contract.outputs,
            "definition_of_done": self.contract.definition_of_done,
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "agent_id" in output and "status" in output


class AgentFactory:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._contracts: Dict[str, AgentContract] = {}
        self._model_provider = None
        self._tool_registry = None
        self._governance = None
        self._memory_manager = None
        self._collaboration_engine = None
        self._initialized = False

    def initialize(self, database_url: Optional[str] = None):
        if self._initialized:
            return
        self._model_provider = get_model_provider()
        self._tool_registry = register_all_tools()
        self._governance = GovernanceEngine()
        self._memory_manager = initialize_memory(database_url)
        self._collaboration_engine = CollaborationEngine()
        self._contracts = load_agent_contracts()
        self._initialized = True
        logger.info(f"AgentFactory initialized with {len(self._contracts)} contracts")

    def create_agent(self, agent_id: str) -> Optional[BaseAgent]:
        if not self._initialized:
            self.initialize()
        if agent_id in self._agents:
            return self._agents[agent_id]
        contract = self._contracts.get(agent_id)
        if contract is None:
            logger.error(f"No contract found for agent: {agent_id}")
            return None
        model = get_model_for_agent(agent_id)
        agent_tools = self._tool_registry.get_tools_for_agent(agent_id) if self._tool_registry else []
        agent_cls = _AGENT_CLASSES.get(agent_id)
        if agent_cls is None:
            agent = GenericOperationalAgent(contract=contract)
        else:
            agent = agent_cls(contract=contract)
        agent.model = model
        agent.model_provider = self._model_provider
        agent.tool_registry = self._tool_registry
        agent.governance = self._governance
        agent.memory_manager = self._memory_manager
        agent.collaboration_engine = self._collaboration_engine
        self._agents[agent_id] = agent
        logger.info(f"Created agent: {agent_id} with model: {model.policy if model else 'none'}")
        return agent

    def create_all_agents(self) -> Dict[str, BaseAgent]:
        if not self._initialized:
            self.initialize()
        for agent_id in self._contracts:
            self.create_agent(agent_id)
        logger.info(f"Created {len(self._agents)} agents")
        return self._agents

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def get_agents_by_team(self, team: str) -> List[BaseAgent]:
        return [a for a in self._agents.values() if a.contract.team == team]

    def get_all_agents(self) -> Dict[str, BaseAgent]:
        return dict(self._agents)

    async def execute_agents_concurrent(
        self,
        agent_ids: List[str],
        task: Task,
        shared_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        results = {}

        async def _execute_single(agent_id: str):
            agent = self.get_agent(agent_id) or self.create_agent(agent_id)
            if agent is None:
                return agent_id, {"error": f"Agent {agent_id} not available"}
            try:
                result = agent.execute(task, shared_context)
                return agent_id, result
            except Exception as exc:
                logger.error(f"Agent {agent_id} execution failed: {exc}")
                return agent_id, {"error": str(exc)}

        task_results = await asyncio.gather(
            *[_execute_single(aid) for aid in agent_ids],
            return_exceptions=True,
        )

        for result in task_results:
            if isinstance(result, Exception):
                logger.error(f"Concurrent execution error: {result}")
                continue
            agent_id, output = result
            results[agent_id] = output

        return results

    def get_factory_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self._agents),
            "agents_by_team": {
                team: len([a for a in self._agents.values() if a.contract.team == team])
                for team in set(a.contract.team for a in self._agents.values())
            },
            "model_stats": self._model_provider.get_total_stats() if self._model_provider else {},
        }


_agent_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    global _agent_factory
    if _agent_factory is None:
        _agent_factory = AgentFactory()
    return _agent_factory


def initialize_agent_factory(database_url: Optional[str] = None) -> AgentFactory:
    global _agent_factory
    _agent_factory = AgentFactory()
    _agent_factory.initialize(database_url)
    return _agent_factory