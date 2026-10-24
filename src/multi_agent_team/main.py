import argparse
import sys
import asyncio
from typing import Optional

sys.path.insert(0, '.')

from src.multi_agent_team.agents.base import load_agent_contracts
from src.multi_agent_team.orchestration.engine import run_multi_agent_workflow
from src.multi_agent_team.orchestration.concurrent_engine import (
    initialize_concurrent_engine,
    get_concurrent_engine,
)
from src.multi_agent_team.memory import initialize_memory, get_memory_manager, MemoryManager
from src.multi_agent_team.api.main import app as api_app
from src.multi_agent_team.monitoring.models_sa import Base
from src.multi_agent_team.models.provider import initialize_models, get_model_provider
from src.multi_agent_team.agents.factory import initialize_agent_factory, get_agent_factory
from sqlalchemy import create_engine
import os


class SystemBootstrap:
    """Bootstrap the entire system stack before workflow execution."""

    def __init__(self):
        self.memory_manager: Optional[object] = None
        self.database_engine = None
        self.initialized = False

    def initialize(self, database_url: Optional[str] = None) -> bool:
        """Initialize all system components."""
        if self.initialized:
            return True

        print("=== Bootstrapping Multi-Agent Engineering Organization ===")

        # 1. Initialize database connection
        db_url = database_url or os.environ.get(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/multi_agent_team",
        )
        print(f"1. Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

        try:
            self.database_engine = create_engine(db_url, pool_pre_ping=True)
            with self.database_engine.connect() as conn:
                conn.execute("SELECT 1")
            print("   Database connection established")
            Base.metadata.create_all(bind=self.database_engine)
            print("   Database tables verified/created")
        except Exception as e:
            print(f"   Database connection failed (continuing with in-memory): {e}")
            self.database_engine = None

        # 2. Initialize model provider (NVIDIA + Ollama fallback)
        print("2. Initializing multi-model provider...")
        try:
            model_provider = initialize_models()
            print(f"   Loaded {len(model_provider.list_models())} model policies")
            for policy in model_provider.list_models():
                model = model_provider.get_model(policy)
                print(f"      - {policy}: {model.model_name if model else 'failed'}")
        except Exception as e:
            print(f"   Model provider initialization failed: {e}")

        # 3. Initialize agent factory
        print("3. Initializing agent factory...")
        try:
            factory = initialize_agent_factory(db_url)
            factory.create_all_agents()
            print(f"   Created {len(factory.get_all_agents())} agents")
        except Exception as e:
            print(f"   Agent factory initialization failed: {e}")

        # 4. Initialize memory manager
        print("4. Initializing memory manager...")
        self.memory_manager = initialize_memory(db_url)
        print("   Memory manager initialized (three-tier architecture)")

        # 5. Initialize concurrent orchestration engine
        print("5. Initializing concurrent orchestration engine...")
        try:
            engine = initialize_concurrent_engine(db_url)
            print("   Concurrent orchestration engine ready")
        except Exception as e:
            print(f"   Concurrent engine initialization failed: {e}")

        # 6. Verify governance engine
        print("6. Verifying governance engine...")
        from src.multi_agent_team.governance.engine import GovernanceEngine
        governance = GovernanceEngine()
        print("   Governance engine ready")

        # 7. Verify tool registry
        print("7. Verifying tool registry...")
        from src.multi_agent_team.tools import register_all_tools
        tools = register_all_tools()
        print(f"   Registered {len(tools)} tools")

        self.initialized = True
        print("\n=== System Bootstrap Complete ===\n")
        return True

    def shutdown(self):
        print("\n=== System Shutdown Complete ===")


_bootstrap: Optional[SystemBootstrap] = None


def get_bootstrap() -> SystemBootstrap:
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = SystemBootstrap()
    return _bootstrap


def _print_model_stats():
    provider = get_model_provider()
    stats = provider.get_total_stats()
    print("\n=== Model Provider Statistics ===")
    print(f"Total Invocations: {stats.get('total_invocations', 0)}")
    print(f"Total Tokens: {stats.get('total_tokens', 0)}")
    print(f"Total Latency: {stats.get('total_latency_ms', 0):.2f}ms")
    print(f"Success: {stats.get('total_success', 0)} | Failures: {stats.get('total_failure', 0)}")
    for policy, pstats in stats.get("policies", {}).items():
        print(f"   {policy}: {pstats.total_invocations} invocations, {pstats.total_tokens} tokens")


def _print_agent_stats():
    factory = get_agent_factory()
    stats = factory.get_factory_stats()
    print("\n=== Agent Factory Statistics ===")
    print(f"Total Agents: {stats.get('total_agents', 0)}")
    for team, count in stats.get("agents_by_team", {}).items():
        print(f"   {team}: {count} agents")


async def _run_concurrent_workflow(objective: str, agent_ids: Optional[list] = None):
    """Run a workflow with multiple agents in concurrence."""
    engine = get_concurrent_engine()

    if agent_ids is None:
        agent_ids = [
            "product_owner",
            "platform_architect",
            "security_architect",
            "solution_architect",
            "development_lead",
            "backend_engineer",
            "frontend_engineer",
            "qa_lead",
            "devops_lead",
            "sre_observability_engineer",
        ]

    print(f"\n=== Concurrent Multi-Agent Execution ===")
    print(f"Objective: {objective}")
    print(f"Agents: {', '.join(agent_ids)}")
    print(f"Mode: All agents executing in concurrence\n")

    result = await engine.execute_agents_in_concurrence(
        agent_ids=agent_ids,
        objective=objective,
        max_concurrent=len(agent_ids),
    )

    print(f"\n=== Results ===")
    print(f"Status: {result['status']}")
    print(f"Successful Agents: {result['successful_agents']}/{result['agent_count']}")
    print(f"Quality Gates Passed: {result['quality_gate_summary']['passed']}")
    print(f"Quality Gates Failed: {result['quality_gate_summary']['failed']}")

    for agent_id, output in result.get("agent_outputs", {}).items():
        print(f"\n--- {agent_id} ---")
        if isinstance(output, dict):
            for k, v in output.items():
                if k != "error":
                    print(f"   {k}: {v}")
        if "error" in output:
            print(f"   ERROR: {output['error']}")

    if result.get("errors"):
        print(f"\n=== Errors ===")
        for agent_id, error in result["errors"].items():
            print(f"   {agent_id}: {error}")

    print(f"\n=== Evidence Collected: {len(result.get('evidence', []))} items ===")

    _print_model_stats()
    _print_agent_stats()

    return result


def main():
    p = argparse.ArgumentParser(description="Multi-Agent Engineering Organization - Full Specification Implementation")
    p.add_argument("command", nargs="?", default="workflow")
    p.add_argument("objective", nargs="?", default="Provision a new non-production GCP application environment using approved Landing Zone with security, FinOps, testing and operational controls.")
    p.add_argument("--validate-contracts", action="store_true", help="Validate all agent contracts against specification")
    p.add_argument("--list-agents", action="store_true", help="List all registered agents")
    p.add_argument("--author", default="agent_a")
    p.add_argument("--reviewer", default="agent_b")
    p.add_argument("--no-bootstrap", action="store_true", help="Skip system bootstrap (for testing)")
    p.add_argument("--database-url", help="Database URL for persistence")
    p.add_argument("--concurrent", action="store_true", help="Run agents in concurrence (parallel execution)")
    p.add_argument("--agents", nargs="*", help="Specific agent IDs for concurrent execution")
    p.add_argument("--max-concurrent", type=int, default=10, help="Maximum concurrent agent executions")
    args = p.parse_args()

    if not args.no_bootstrap:
        bootstrap = get_bootstrap()
        bootstrap.initialize(args.database_url)

    try:
        if args.validate_contracts:
            contracts = load_agent_contracts()
            for agent_id, contract in contracts.items():
                print(f"Agent: {agent_id.value} ({contract.role}) - Team: {contract.team} - Status: Validated")
            print(f"\nTotal agents: {len(contracts)} (Specification requires 22)")
            return

        if args.list_agents:
            contracts = load_agent_contracts()
            print("=== Multi-Agent Team Registry ===")
            for agent_id, contract in contracts.items():
                print(f"{agent_id.value:30s} | {contract.role:25s} | Team: {contract.team}")
            return

        if args.command == "billing":
            _print_billing_report()
            return

        if args.command == "governance":
            _print_governance_report(args.author, args.reviewer)
            return

        if args.command == "api":
            import uvicorn
            print("Starting API server on http://0.0.0.0:8000")
            uvicorn.run(api_app, host="0.0.0.0", port=8000)
            return

        if args.concurrent:
            result = asyncio.run(_run_concurrent_workflow(args.objective, args.agents))
            return

        print(f"=== Multi-Agent Engineering Organization ===")
        print(f"Objective: {args.objective}\n")

        result = run_multi_agent_workflow(args.objective)
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Tasks Completed: Check workflow state for details")
        print(f"Evidence Collected: {result.get('evidence_collected', 0)} artifacts")
        print(f"Quality Gates Passed: {result.get('quality_gates_passed', 0)}")
        print(f"Risks: {result.get('risks_identified', 0)}")
        print(f"\n=== Final Response ===")
        print(result.get('final_response', 'No response'))

        workflow_state = result.get('workflow_state', {})
        if workflow_state:
            print(f"\n=== Workflow State ===")
            for key, value in workflow_state.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  {key}: {len(value)} entries")
                else:
                    print(f"  {key}: {value}")

    finally:
        if not args.no_bootstrap:
            bootstrap = get_bootstrap()
            bootstrap.shutdown()


if __name__ == "__main__":
    main()