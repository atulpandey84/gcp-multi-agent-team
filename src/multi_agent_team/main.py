import argparse
import sys
sys.path.insert(0, '.')

# Import full multi-agent orchestration
from src.multi_agent_team.orchestration.engine import run_multi_agent_workflow
from src.multi_agent_team.agents.base import load_agent_contracts, AgentContract
from src.multi_agent_team.agents.engineering_orchestrator import EngineeringOrchestratorAgent

def main():
    p = argparse.ArgumentParser(description="Multi-Agent Engineering Organization - Full Specification Implementation")
    p.add_argument("objective", nargs="?", default="Provision a new non-production GCP application environment using approved Landing Zone with security, FinOps, testing and operational controls.")
    p.add_argument("--validate-contracts", action="store_true", help="Validate all agent contracts against specification")
    p.add_argument("--list-agents", action="store_true", help="List all registered agents")
    args = p.parse_args()

    if args.validate_contracts:
        contracts = load_agent_contracts()
        for agent_id, contract in contracts.items():
            print(f"Agent: {agent_id} ({contract.role}) - Team: {contract.team} - Status: Validated")
        print(f"\nTotal agents: {len(contracts)} (Specification requires 22)")
        return

    if args.list_agents:
        contracts = load_agent_contracts()
        print("=== Multi-Agent Team Registry ===")
        for agent_id, contract in contracts.items():
            print(f"{agent_id:30s} | {contract.role:25s} | Team: {contract.team}")
        return

    # Execute full multi-agent workflow with evidence tracking, quality gates, approvals
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
    
    # Show workflow state summary
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

if __name__ == "__main__":
    main()
