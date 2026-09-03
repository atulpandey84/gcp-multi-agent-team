"""
FastAPI application for the Multi-Agent Engineering Organization.
Provides REST API endpoints for workflow management, agent monitoring, and system health.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
import uuid

from src.multi_agent_team.schemas.contracts import (
    AgentRole,
    Team,
    TaskStatus,
    WorkflowRequest,
    WorkflowResponse,
    AgentStatusResponse,
    MetricsResponse,
    HealthCheckResponse,
    TaskInput,
    TaskOutput,
    AgentMessage,
    ApprovalRequest,
    QualityGateResult,
    ToolInvocation,
    ToolResult,
    WorkflowState,
)

app = FastAPI(
    title="GCP Multi-Agent Engineering Team API",
    description="REST API for managing the 22-agent autonomous engineering organization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
workflows: Dict[str, WorkflowState] = {}
agent_statuses: Dict[AgentRole, AgentStatusResponse] = {}
system_metrics = MetricsResponse(
    total_workflows=0,
    active_workflows=0,
    completed_workflows=0,
    failed_workflows=0,
    average_completion_time_seconds=0.0,
    agent_utilization={},
    quality_gate_pass_rate=0.0,
    approval_rate=0.0,
)


def get_current_timestamp() -> datetime:
    return datetime.utcnow()


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """System health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=get_current_timestamp(),
        components={
            "api": "healthy",
            "database": "healthy",
            "message_queue": "healthy",
            "agent_registry": "healthy",
        },
        active_workflows=system_metrics.active_workflows,
        registered_agents=len(agent_statuses),
    )


@app.get("/api/v1/agents", response_model=List[AgentStatusResponse], tags=["Agents"])
async def list_agents():
    """List all registered agents and their statuses."""
    return list(agent_statuses.values())


@app.get("/api/v1/agents/{agent_id}", response_model=AgentStatusResponse, tags=["Agents"])
async def get_agent(agent_id: AgentRole):
    """Get status of a specific agent."""
    if agent_id not in agent_statuses:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent_statuses[agent_id]


@app.post("/api/v1/workflows", response_model=WorkflowResponse, tags=["Workflows"])
async def create_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Create and start a new workflow."""
    workflow_id = str(uuid.uuid4())
    
    workflow = WorkflowState(
        workflow_id=workflow_id,
        objective=request.objective,
        status=TaskStatus.CREATED,
        created_at=get_current_timestamp(),
        updated_at=get_current_timestamp(),
        assigned_agents=request.assigned_agents or [],
    )
    
    workflows[workflow_id] = workflow
    
    # Update metrics
    system_metrics.total_workflows += 1
    system_metrics.active_workflows += 1
    
    # Start workflow in background
    background_tasks.add_task(execute_workflow, workflow_id, request)
    
    return WorkflowResponse(
        workflow_id=workflow_id,
        status=TaskStatus.CREATED,
        message="Workflow created and queued for execution",
        estimated_duration_seconds=300,
    )


@app.get("/api/v1/workflows", response_model=List[WorkflowState], tags=["Workflows"])
async def list_workflows(status: Optional[TaskStatus] = None, limit: int = 50):
    """List all workflows with optional status filter."""
    filtered = list(workflows.values())
    if status:
        filtered = [w for w in filtered if w.status == status]
    return filtered[:limit]


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowState, tags=["Workflows"])
async def get_workflow(workflow_id: str):
    """Get detailed state of a specific workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return workflows[workflow_id]


@app.post("/api/v1/workflows/{workflow_id}/cancel", tags=["Workflows"])
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    workflow = workflows[workflow_id]
    if workflow.status in [TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Workflow already in terminal state: {workflow.status}")
    
    workflow.status = TaskStatus.CANCELLED
    workflow.updated_at = get_current_timestamp()
    workflow.final_response = "Workflow cancelled by user"
    
    system_metrics.active_workflows -= 1
    system_metrics.failed_workflows += 1
    
    return {"message": "Workflow cancelled", "workflow_id": workflow_id}


@app.get("/api/v1/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """Get system metrics for monitoring."""
    return system_metrics


@app.post("/api/v1/approvals", response_model=ApprovalRequest, tags=["Approvals"])
async def request_approval(approval: ApprovalRequest):
    """Submit a new approval request."""
    # In production, this would persist to database and notify approvers
    return approval


@app.get("/api/v1/approvals", response_model=List[ApprovalRequest], tags=["Approvals"])
async def list_approvals(status: Optional[str] = None):
    """List all approval requests."""
    # In production, this would query the database
    return []


@app.post("/api/v1/approvals/{approval_id}/decide", tags=["Approvals"])
async def decide_approval(approval_id: str, decision: Literal["approved", "rejected"], comments: Optional[str] = None):
    """Record a decision on an approval request."""
    # In production, this would update the database and notify the requester
    return {"approval_id": approval_id, "decision": decision, "comments": comments}


@app.post("/api/v1/tools/invoke", response_model=ToolResult, tags=["Tools"])
async def invoke_tool(invocation: ToolInvocation):
    """Invoke a tool on behalf of an agent."""
    # In production, this would route to the tool registry
    return ToolResult(
        tool_id=invocation.tool_id,
        success=True,
        result={"message": "Tool invocation simulated"},
        execution_time_ms=100,
    )


@app.get("/api/v1/quality-gates", response_model=List[QualityGateResult], tags=["Quality"])
async def list_quality_gates(workflow_id: Optional[str] = None):
    """List quality gate results."""
    # In production, this would query the database
    return []


# Background task for workflow execution
async def execute_workflow(workflow_id: str, request: WorkflowRequest):
    """Execute a workflow in the background."""
    workflow = workflows[workflow_id]
    
    try:
        workflow.status = TaskStatus.IN_PROGRESS
        workflow.updated_at = get_current_timestamp()
        
        # Simulate workflow execution
        import asyncio
        await asyncio.sleep(2)
        
        # Update workflow state
        workflow.status = TaskStatus.DONE
        workflow.updated_at = get_current_timestamp()
        workflow.final_response = f"Workflow completed: {request.objective}"
        workflow.evidence_collected = 5
        workflow.quality_gates_passed = 3
        workflow.risks_identified = 1
        
        # Update metrics
        system_metrics.active_workflows -= 1
        system_metrics.completed_workflows += 1
        
    except Exception as e:
        workflow.status = TaskStatus.FAILED
        workflow.updated_at = get_current_timestamp()
        workflow.final_response = f"Workflow failed: {str(e)}"
        
        system_metrics.active_workflows -= 1
        system_metrics.failed_workflows += 1


# Initialize default agent statuses
def initialize_agent_statuses():
    """Initialize default agent statuses for monitoring."""
    agents = [
        (AgentRole.PRODUCT_OWNER, "Product Owner", Team.PRODUCT_DELIVERY),
        (AgentRole.PROJECT_MANAGER, "Project Manager", Team.PRODUCT_DELIVERY),
        (AgentRole.PLATFORM_ARCHITECT, "Platform Architect", Team.ARCHITECTURE_DESIGN),
        (AgentRole.SOLUTION_ARCHITECT, "Solution Architect", Team.ARCHITECTURE_DESIGN),
        (AgentRole.SECURITY_ARCHITECT, "Security Architect", Team.ARCHITECTURE_DESIGN),
        (AgentRole.DEVOPS_LEAD, "DevOps Lead", Team.DEVOPS_INFRASTRUCTURE),
        (AgentRole.CLOUD_INFRASTRUCTURE_ENGINEER, "Cloud Infrastructure Engineer", Team.DEVOPS_INFRASTRUCTURE),
        (AgentRole.CICD_ENGINEER, "CI/CD Engineer", Team.DEVOPS_INFRASTRUCTURE),
        (AgentRole.SRE_OBSERVABILITY_ENGINEER, "SRE / Observability Engineer", Team.DEVOPS_INFRASTRUCTURE),
        (AgentRole.FINOPS_ENGINEER, "FinOps Engineer", Team.DEVOPS_INFRASTRUCTURE),
        (AgentRole.DEVELOPMENT_LEAD, "Development Lead", Team.DEVELOPMENT),
        (AgentRole.FRONTEND_ENGINEER, "Frontend Engineer", Team.DEVELOPMENT),
        (AgentRole.BACKEND_ENGINEER, "Backend Engineer", Team.DEVELOPMENT),
        (AgentRole.INTEGRATION_ENGINEER, "Integration Engineer", Team.DEVELOPMENT),
        (AgentRole.AI_AUTOMATION_ENGINEER, "AI / Automation Engineer", Team.DEVELOPMENT),
        (AgentRole.QA_LEAD, "QA Lead", Team.TESTING_QUALITY),
        (AgentRole.TEST_AUTOMATION_ENGINEER, "Test Automation Engineer", Team.TESTING_QUALITY),
        (AgentRole.NFR_TEST_ENGINEER, "Non-Functional Test Engineer", Team.TESTING_QUALITY),
        (AgentRole.APPLICATION_MANAGEMENT_LEAD, "Application Management Lead", Team.APPLICATION_MANAGEMENT_RELIABILITY),
        (AgentRole.APPLICATION_SUPPORT_ENGINEER, "L2/L3 Application Support Engineer", Team.APPLICATION_MANAGEMENT_RELIABILITY),
        (AgentRole.PRODUCTION_RELIABILITY_ENGINEER, "Production Reliability Engineer", Team.APPLICATION_MANAGEMENT_RELIABILITY),
        (AgentRole.ENGINEERING_ORCHESTRATOR, "Engineering Orchestrator", Team.ENGINEERING_GOVERNANCE),
    ]
    
    for agent_id, role, team in agents:
        agent_statuses[agent_id] = AgentStatusResponse(
            agent_id=agent_id,
            role=role,
            team=team,
            status="idle",
            tasks_completed=0,
            tasks_failed=0,
        )


# Initialize on startup
initialize_agent_statuses()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)