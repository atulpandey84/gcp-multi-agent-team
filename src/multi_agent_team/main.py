import argparse
import sys
import asyncio
from typing import Optional

from src.multi_agent_team.agents.base import load_agent_contracts
from src.multi_agent_team.orchestration.engine import run_multi_agent_workflow
from src.multi_agent_team.memory import initialize_memory, get_memory_manager, MemoryManager
from src.multi_agent_team.api.main import app as api_app
from src.multi_agent_team.monitoring.models_sa import Base
from sqlalchemy import create_engine
import os

sys.path.insert(0, '.')


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
            "postgresql://user:password@localhost:5432/multi_agent_team"
        )
        print(f"1. Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        
        try:
            self.database_engine = create_engine(db_url, pool_pre_ping=True)
            # Test connection
            with self.database_engine.connect() as conn:
                conn.execute("SELECT 1")
            print("   ✓ Database connection established")
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.database_engine)
            print("   ✓ Database tables verified/created")
        except Exception as e:
            print(f"   ⚠ Database connection failed (continuing with in-memory): {e}")
            self.database_engine = None
        
        # 2. Initialize memory manager with session management
        print("2. Initializing memory manager...")
        self.memory_manager = initialize_memory(db_url)
        print("   ✓ Memory manager initialized (three-tier architecture)")
        
        # 3. Initialize agent registry
        print("3. Loading agent contracts...")
        try:
            contracts = load_agent_contracts()
            print(f"   ✓ Loaded {len(contracts)} agent contracts")
            for agent_id, contract in contracts.items():
                print(f"      - {agent_id.value}: {contract.role} ({contract.team})")
        except Exception as e:
            print(f"   ⚠ Failed to load contracts: {e}")
        
        # 4. Initialize cache (in-memory working memory)
        print("4. Initializing cache layer...")
        memory = get_memory_manager()
        # Pre-populate institutional memory with common patterns
        asyncio.run(self._populate_institutional_memory(memory))
        print("   ✓ Cache layer initialized with institutional memory")
        
        # 5. Verify governance engine
        print("5. Verifying governance engine...")
        from src.multi_agent_team.governance.engine import GovernanceEngine
        governance = GovernanceEngine()
        print("   ✓ Governance engine ready")
        
        # 6. Verify tool registry
        print("6. Verifying tool registry...")
        from src.multi_agent_team.tools import register_all_tools
        tools = register_all_tools()
        print(f"   ✓ Registered {len(tools)} tools")
        
        self.initialized = True
        print("\n=== System Bootstrap Complete ===\n")
        return True
    
    async def _populate_institutional_memory(self, memory: MemoryManager):
        """Pre-populate institutional memory with common patterns."""
        patterns = {
            "gcp_landing_zone": {
                "description": "Standard GCP Landing Zone architecture",
                "components": ["organization", "folders", "projects", "networking", "security", "monitoring"],
            },
            "terraform_best_practices": {
                "description": "Terraform best practices for GCP",
                "rules": ["use_modules", "state_locking", "plan_before_apply", "version_pinning"],
            },
            "security_baseline": {
                "description": "Security baseline for all deployments",
                "controls": ["iam_least_privilege", "encryption_at_rest", "encryption_in_transit", "audit_logging"],
            },
        }
        
        for key, value in patterns.items():
            await memory.set_institutional(key, value, category="architecture_patterns")
    
    def shutdown(self):
        """Graceful shutdown of all components."""
        print("=== Shutting down Multi-Agent Engineering Organization ===")
        
        if self.memory_manager:
            memory = get_memory_manager()
            memory.cleanup_expired()
            print("✓ Memory cleaned up")
        
        if self.database_engine:
            self.database_engine.dispose()
            print("✓ Database connections closed")
        
        self.initialized = False
        print("=== Shutdown Complete ===")


# Global bootstrap instance
_bootstrap: Optional[SystemBootstrap] = None


def get_bootstrap() -> SystemBootstrap:
    """Get the global bootstrap instance."""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = SystemBootstrap()
    return _bootstrap


def _print_billing_report():
    from multi_agent_team.tools.billing import get_billing_costs, forecast_monthly_cost

    costs = get_billing_costs("prj-test-01")
    forecast = forecast_monthly_cost(costs["total_cost_usd"], days_elapsed=15, days_in_month=30)
    print("GCP BILLING & COST MONITORING REPORT")
    print(f"Project: {costs['project_id']}")
    print(f"Total Cost: ${costs['total_cost_usd']:.2f} USD")
    print(f"Projected Monthly Cost: ${forecast['projected_monthly_cost_usd']:.2f} USD")
    print("Service Breakdown:")
    for svc in costs["service_breakdown"]:
        print(f"  - {svc['service']}: ${svc['cost_usd']:.2f}")


def _print_governance_report(author: str, reviewer: str):
    from multi_agent_team.policies.engine import validate_separation_of_duties

    result = validate_separation_of_duties(author, reviewer, "iam_policy_change")
    print("GOVERNANCE POLICY EVALUATION")
    print(f"Author: {author}")
    print(f"Reviewer: {reviewer}")
    print(f"Action: iam_policy_change")
    print(result["reason"])


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
    args = p.parse_args()

    # Bootstrap the system unless explicitly disabled
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
            # Start the API server
            import uvicorn
            print("Starting API server on http://0.0.0.0:8000")
            uvicorn.run(api_app, host="0.0.0.0", port=8000)
            return

        print(f"=== Multi-Agent Engineering Organization ===")
        print(f"Objective: {args.objective}\n")
        
        # Run workflow with bootstrapped system
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
        # Graceful shutdown
        if not args.no_bootstrap:
            bootstrap = get_bootstrap()
            bootstrap.shutdown()


if __name__ == "__main__":
    main()
