"""
Base Tool Framework for Multi-Agent System

Defines the contract and base implementation for all specialized agent tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json


class ToolRisk(Enum):
    """Risk level for tool execution"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalRequired(Enum):
    """Approval levels for tool execution"""
    NONE = "none"
    PEER = "peer"
    HUMAN = "human"


class SimulationMode(Enum):
    """Simulation mode for pre-flight checks"""
    DISABLED = "disabled"      # No simulation, execute directly
    DRY_RUN = "dry_run"        # Simulate without side effects
    PLAN_ONLY = "plan_only"    # Generate execution plan only (e.g., terraform plan)
    FULL_SIMULATION = "full_simulation"  # Full simulation with mock results


@dataclass
class ToolInput:
    """Standardized input for tool execution"""
    agent_id: str
    task_id: str
    action: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Simulation/pre-flight fields
    simulation_mode: SimulationMode = SimulationMode.DISABLED
    require_approval: bool = False
    approval_chain: List[str] = field(default_factory=list)
    dry_run: bool = False  # Legacy field, use simulation_mode instead


@dataclass
class ToolOutput:
    """Standardized output from tool execution"""
    success: bool
    action: str
    result: Any
    evidence: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Simulation/pre-flight fields
    simulation_mode: SimulationMode = SimulationMode.DISABLED
    simulation_result: Optional[Dict[str, Any]] = None
    execution_plan: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    confirmation_token: Optional[str] = None


@dataclass
class ToolDefinition:
    """Metadata about a tool"""
    tool_id: str
    name: str
    description: str
    risk_level: ToolRisk
    approval_required: ApprovalRequired
    agent_ids: List[str]  # Which agents can use this tool
    allowed_actions: List[str]  # Specific actions allowed
    requires_authentication: bool = True
    requires_authorization: bool = True
    mutable: bool = False  # Does tool change state
    environment_restriction: Optional[str] = None  # dev, staging, prod, etc.


class BaseTool(ABC):
    """
    Base class for all agent tools.
    
    All tools must implement this interface to be integrated into the system.
    """
    
    def __init__(self, tool_id: str, agent_ids: List[str]):
        self.tool_id = tool_id
        self.agent_ids = agent_ids
        self.execution_log: List[Dict[str, Any]] = []
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Return tool metadata and permissions"""
        pass
    
    @abstractmethod
    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        """
        Execute the tool action.
        
        Must validate:
        - Agent is authorized
        - Action is allowed
        - Parameters are valid
        - Risk is acceptable
        """
        pass
    
    # ============================================================
    # Pre-Flight Simulation Methods
    # ============================================================
    
    async def pre_flight_check(self, tool_input: ToolInput) -> ToolOutput:
        """
        Perform pre-flight simulation before actual execution.
        
        This method runs in simulation mode to:
        1. Validate the action plan
        2. Estimate resource impact
        3. Check for conflicts
        4. Generate execution plan
        5. Determine if confirmation is required
        
        Override in subclass for tool-specific simulation logic.
        """
        # Default implementation: basic validation
        simulation_result = {
            "validated": True,
            "estimated_impact": "unknown",
            "conflicts": [],
            "warnings": [],
        }
        
        execution_plan = {
            "action": tool_input.action,
            "parameters": tool_input.parameters,
            "estimated_duration_ms": 1000,
            "resources_affected": [],
            "rollback_possible": True,
        }
        
        # Check if confirmation is required based on risk level
        definition = self.get_definition()
        requires_confirmation = definition.risk_level in [ToolRisk.HIGH, ToolRisk.CRITICAL]
        
        return ToolOutput(
            success=True,
            action=f"pre_flight_{tool_input.action}",
            result=simulation_result,
            simulation_mode=SimulationMode.PLAN_ONLY,
            simulation_result=simulation_result,
            execution_plan=execution_plan,
            requires_confirmation=requires_confirmation,
            confirmation_token=None,  # Would be generated in production
            execution_time_ms=0,
        )
    
    async def simulate(self, tool_input: ToolInput) -> ToolOutput:
        """
        Run full simulation of the tool action.
        
        This is a dry-run that simulates the complete execution
        without making any actual changes.
        
        Override in subclass for tool-specific simulation logic.
        """
        # Run pre-flight check first
        pre_flight = await self.pre_flight_check(tool_input)
        
        if not pre_flight.success:
            return pre_flight
        
        # Default simulation: return mock result
        simulation_result = {
            "simulated": True,
            "mock_result": f"Simulated execution of {tool_input.action}",
            "estimated_changes": [],
            "warnings": ["This is a simulation - no actual changes made"],
        }
        
        return ToolOutput(
            success=True,
            action=f"simulate_{tool_input.action}",
            result=simulation_result,
            simulation_mode=SimulationMode.FULL_SIMULATION,
            simulation_result=simulation_result,
            execution_plan=pre_flight.execution_plan,
            requires_confirmation=False,
            execution_time_ms=0,
        )
    
    async def execute_with_simulation(self, tool_input: ToolInput) -> ToolOutput:
        """
        Execute tool with integrated pre-flight simulation.
        
        Flow:
        1. Run pre-flight check
        2. If simulation_mode is DRY_RUN or PLAN_ONLY, return simulation result
        3. If requires_confirmation and no confirmation_token, return pending confirmation
        4. Execute actual action
        5. Log execution
        """
        start_time = datetime.utcnow()
        
        # Validate agent and action
        if not self.validate_agent(tool_input.agent_id):
            return self._create_output(
                success=False,
                action=tool_input.action,
                result=None,
                error=f"Agent {tool_input.agent_id} not authorized",
                execution_time_ms=0,
            )
        
        definition = self.get_definition()
        if not self.validate_action(tool_input.action, definition):
            return self._create_output(
                success=False,
                action=tool_input.action,
                result=None,
                error=f"Action {tool_input.action} not allowed",
                execution_time_ms=0,
            )
        
        # Handle simulation modes
        if tool_input.simulation_mode != SimulationMode.DISABLED or tool_input.dry_run:
            if tool_input.simulation_mode == SimulationMode.PLAN_ONLY:
                return await self.pre_flight_check(tool_input)
            elif tool_input.simulation_mode in [SimulationMode.DRY_RUN, SimulationMode.FULL_SIMULATION]:
                return await self.simulate(tool_input)
        
        # Check if confirmation is required
        definition = self.get_definition()
        requires_confirmation = (
            definition.risk_level in [ToolRisk.HIGH, ToolRisk.CRITICAL] or
            tool_input.require_approval
        )
        
        if requires_confirmation and not tool_input.metadata.get("confirmation_token"):
            # Return pending confirmation
            pre_flight = await self.pre_flight_check(tool_input)
            return ToolOutput(
                success=False,
                action=tool_input.action,
                result=None,
                error="Confirmation required for high-risk action",
                simulation_mode=SimulationMode.DISABLED,
                requires_confirmation=True,
                confirmation_token=None,
                execution_time_ms=0,
            )
        
        # Execute actual action
        try:
            result = await self.execute(tool_input)
            
            # Log execution
            self.log_execution(tool_input, result)
            
            return result
            
        except Exception as e:
            error_output = self._create_output(
                success=False,
                action=tool_input.action,
                result=None,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )
            self.log_execution(tool_input, error_output)
            return error_output
    
    def validate_agent(self, agent_id: str) -> bool:
        """Check if agent is authorized to use this tool"""
        return agent_id in self.agent_ids
    
    def validate_action(self, action: str, definition: ToolDefinition) -> bool:
        """Check if action is in allowed list"""
        return action in definition.allowed_actions
    
    def validate_parameters(self, parameters: Dict[str, Any], action: str) -> bool:
        """
        Validate tool parameters. Override in subclass.
        Should check for required params, types, ranges, etc.
        """
        return True
    
    def log_execution(self, tool_input: ToolInput, tool_output: ToolOutput):
        """Audit log tool executions"""
        log_entry = {
            "timestamp": tool_output.timestamp.isoformat(),
            "agent_id": tool_input.agent_id,
            "task_id": tool_input.task_id,
            "action": tool_input.action,
            "success": tool_output.success,
            "error": tool_output.error,
            "execution_time_ms": tool_output.execution_time_ms,
        }
        self.execution_log.append(log_entry)
    
    def _create_output(
        self,
        success: bool,
        result: Any,
        action: str,
        error: Optional[str] = None,
        warnings: Optional[List[str]] = None,
        evidence: Optional[Dict[str, Any]] = None,
        execution_time_ms: float = 0.0,
    ) -> ToolOutput:
        """Helper to create standardized output"""
        return ToolOutput(
            success=success,
            action=action,
            result=result,
            error=error,
            warnings=warnings or [],
            evidence=evidence,
            execution_time_ms=execution_time_ms,
            audit_log=self.execution_log,
        )


class ToolRegistry:
    """
    Central registry of all available tools.
    
    Used by agents to:
    - Discover available tools
    - Check permissions
    - Execute tools
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.definitions: Dict[str, ToolDefinition] = {}
    
    def __len__(self) -> int:
        """Return the number of registered tools"""
        return len(self.tools)
    
    def register(self, tool: BaseTool):
        """Register a new tool"""
        definition = tool.get_definition()
        self.tools[tool.tool_id] = tool
        self.definitions[definition.tool_id] = definition
    
    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    def get_tools_for_agent(self, agent_id: str) -> List[ToolDefinition]:
        """Get all tools available to an agent"""
        return [
            defn for defn in self.definitions.values()
            if agent_id in defn.agent_ids
        ]
    
    def can_execute(
        self,
        agent_id: str,
        tool_id: str,
        action: str,
        environment: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if agent can execute tool action.
        Returns (can_execute, reason_if_not)
        """
        definition = self.definitions.get(tool_id)
        if not definition:
            return False, f"Tool not found: {tool_id}"
        
        if agent_id not in definition.agent_ids:
            return False, f"Agent {agent_id} not authorized for {tool_id}"
        
        if action not in definition.allowed_actions:
            return False, f"Action {action} not allowed for {tool_id}"
        
        if definition.environment_restriction and environment != definition.environment_restriction:
            return False, f"Tool {tool_id} restricted to {definition.environment_restriction} environment"
        
        return True, None


# Global registry instance
_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _tool_registry
