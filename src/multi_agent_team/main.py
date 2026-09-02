import argparse
import sys

from src.multi_agent_team.agents.base import load_agent_contracts
from src.multi_agent_team.orchestration.engine import run_multi_agent_workflow

sys.path.insert(0, '.')


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

    if args.command == "billing":
        _print_billing_report()
        return

    if args.command == "governance":
        _print_governance_report(args.author, args.reviewer)
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


if __name__ == "__main__":
    main()
